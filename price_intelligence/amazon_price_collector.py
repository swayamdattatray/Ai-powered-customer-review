"""
Official Amazon PA-API 5.0 Price Collector.
Handles official Amazon Product Advertising API 5.0 queries using standard AWS Signature v4.
"""

import os
import re
import json
import hashlib
import hmac
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import requests

from .base_price_collector import BasePriceCollector
from .models import PriceResult


class AmazonPriceCollector(BasePriceCollector):
    """
    Collector for Amazon product prices via official Amazon PA-API 5.0.
    Requires:
      - AMAZON_ACCESS_KEY
      - AMAZON_SECRET_KEY
      - AMAZON_PARTNER_TAG
      - AMAZON_COUNTRY (optional, defaults to 'IN')
    """

    ENDPOINTS = {
        "IN": "webservices.amazon.in",
        "US": "webservices.amazon.com",
        "UK": "webservices.amazon.co.uk",
    }
    REGIONS = {
        "IN": "eu-west-1",
        "US": "us-east-1",
        "UK": "eu-west-1",
    }

    def __init__(self):
        super().__init__(name="Amazon")
        self.access_key = os.getenv("AMAZON_ACCESS_KEY", "").strip()
        self.secret_key = os.getenv("AMAZON_SECRET_KEY", "").strip()
        self.partner_tag = os.getenv("AMAZON_PARTNER_TAG", "").strip()
        self.country = os.getenv("AMAZON_COUNTRY", "IN").strip().upper()

    def is_configured(self) -> bool:
        return bool(self.access_key and self.secret_key and self.partner_tag)

    def extract_asin(self, url: str) -> Optional[str]:
        if not url:
            return None
        patterns = [
            r"/dp/([A-Z0-9]{10})",
            r"/gp/product/([A-Z0-9]{10})",
            r"/product-reviews/([A-Z0-9]{10})",
            r"/ASIN/([A-Z0-9]{10})",
        ]
        for p in patterns:
            m = re.search(p, url, re.IGNORECASE)
            if m:
                return m.group(1).upper()
        return None

    def _sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        k_date = self._sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, region_name)
        k_service = self._sign(k_region, service_name)
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def _call_paapi(self, operation: str, payload: Dict[str, Any]) -> requests.Response:
        host = self.ENDPOINTS.get(self.country, "webservices.amazon.in")
        region = self.REGIONS.get(self.country, "eu-west-1")
        service = "ProductAdvertisingAPI"
        endpoint = f"https://{host}/paapi5/{operation.lower()}"

        t = datetime.now(timezone.utc)
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        body = json.dumps(payload)
        content_type = "application/json; charset=utf-8"
        amz_target = f"com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{operation}"

        headers = {
            "content-type": content_type,
            "host": host,
            "x-amz-date": amz_date,
            "x-amz-target": amz_target,
            "content-encoding": "amz-1.0",
        }

        canonical_headers = (
            f"content-encoding:amz-1.0\n"
            f"content-type:{content_type}\n"
            f"host:{host}\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:{amz_target}\n"
        )
        signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"
        payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

        canonical_request = (
            f"POST\n/paapi5/{operation.lower()}\n\n"
            f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
        string_to_sign = (
            f"{algorithm}\n{amz_date}\n{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = self._get_signature_key(self.secret_key, date_stamp, region, service)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        auth_header = (
            f"{algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        headers["authorization"] = auth_header

        return requests.post(endpoint, headers=headers, data=body, timeout=12)

    def get_price(
        self,
        product_url: Optional[str] = None,
        product_name: Optional[str] = None
    ) -> PriceResult:
        if not self.is_configured():
            return PriceResult(
                source="Amazon",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error="Amazon PA-API credentials not configured (set AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_PARTNER_TAG)",
                match_confidence="none"
            )

        asin = self.extract_asin(product_url) if product_url else None

        try:
            if asin:
                # 1. Use GetItems with ASIN
                payload = {
                    "ItemIds": [asin],
                    "Resources": [
                        "ItemInfo.Title",
                        "Offers.Listings.Price",
                        "Offers.Listings.Availability.Message",
                        "DetailPageURL"
                    ],
                    "PartnerTag": self.partner_tag,
                    "PartnerType": "Associates",
                    "Marketplace": f"www.amazon.{self.country.lower()}"
                }
                resp = self._call_paapi("GetItems", payload)
            elif product_name:
                # 2. Use SearchItems with product_name
                payload = {
                    "Keywords": product_name[:100],
                    "ItemCount": 1,
                    "Resources": [
                        "ItemInfo.Title",
                        "Offers.Listings.Price",
                        "Offers.Listings.Availability.Message",
                        "DetailPageURL"
                    ],
                    "PartnerTag": self.partner_tag,
                    "PartnerType": "Associates",
                    "Marketplace": f"www.amazon.{self.country.lower()}"
                }
                resp = self._call_paapi("SearchItems", payload)
            else:
                return PriceResult(
                    source="Amazon",
                    status="unavailable",
                    error="Neither product URL nor product name provided",
                    match_confidence="none"
                )

            if resp.status_code == 200:
                data = resp.json()
                items = []
                if "ItemsResult" in data and "Items" in data["ItemsResult"]:
                    items = data["ItemsResult"]["Items"]
                elif "SearchResult" in data and "Items" in data["SearchResult"]:
                    items = data["SearchResult"]["Items"]

                if not items:
                    return PriceResult(
                        source="Amazon",
                        status="unavailable",
                        product_url=product_url,
                        product_name=product_name,
                        error="Product not found in Amazon catalog via PA-API",
                        match_confidence="none"
                    )

                item = items[0]
                item_title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", product_name)
                detail_url = item.get("DetailPageURL", product_url)
                
                # Check match confidence if name matching
                confidence = "exact" if asin else self.assess_product_match(product_name, item_title)
                if confidence == "none":
                    return PriceResult(
                        source="Amazon",
                        status="unavailable",
                        product_url=detail_url,
                        product_name=item_title,
                        error=f"Candidate product does not match target specifications (found '{item_title}')",
                        match_confidence="uncertain"
                    )

                # Extract price
                listings = item.get("Offers", {}).get("Listings", [])
                if not listings:
                    return PriceResult(
                        source="Amazon",
                        status="unavailable",
                        product_url=detail_url,
                        product_name=item_title,
                        availability=False,
                        error="Product currently out of stock or offers unavailable",
                        match_confidence=confidence
                    )

                price_obj = listings[0].get("Price", {})
                amount = price_obj.get("Amount")
                currency = price_obj.get("Currency", "INR")
                avail_msg = listings[0].get("Availability", {}).get("Message", "")

                return PriceResult(
                    source="Amazon",
                    status="success",
                    product_name=item_title,
                    product_url=detail_url,
                    price=self.clean_price_value(amount),
                    currency=currency,
                    availability="in stock" in avail_msg.lower() or not avail_msg,
                    match_confidence=confidence
                )

            elif resp.status_code in (401, 403):
                return PriceResult(
                    source="Amazon",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error="Amazon PA-API authentication failed. Verify AccessKey, SecretKey and PartnerTag.",
                    match_confidence="none"
                )
            elif resp.status_code == 429:
                return PriceResult(
                    source="Amazon",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error="Amazon PA-API rate limit exceeded. Please retry shortly.",
                    match_confidence="none"
                )
            else:
                return PriceResult(
                    source="Amazon",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error=f"Amazon PA-API returned HTTP {resp.status_code}",
                    match_confidence="none"
                )

        except requests.exceptions.Timeout:
            return PriceResult(
                source="Amazon",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error="Amazon PA-API request timed out",
                match_confidence="none"
            )
        except Exception as e:
            return PriceResult(
                source="Amazon",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error=f"Amazon API error: {str(e)}",
                match_confidence="none"
            )
