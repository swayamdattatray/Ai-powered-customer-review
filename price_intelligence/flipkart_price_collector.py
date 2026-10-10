"""
Official Flipkart Affiliate API Price Collector.
Handles official Flipkart Affiliate API queries for product pricing.
"""

import os
import re
from typing import Optional, Dict, Any
import requests

from .base_price_collector import BasePriceCollector
from .models import PriceResult


class FlipkartPriceCollector(BasePriceCollector):
    """
    Collector for Flipkart product prices via official Flipkart Affiliate API.
    Requires:
      - FLIPKART_AFFILIATE_ID
      - FLIPKART_AFFILIATE_TOKEN
    """

    PRODUCT_API_URL = "https://affiliate-api.flipkart.net/affiliate/1.0/product.json"
    SEARCH_API_URL = "https://affiliate-api.flipkart.net/affiliate/1.0/search.json"

    def __init__(self):
        super().__init__(name="Flipkart")
        self.affiliate_id = os.getenv("FLIPKART_AFFILIATE_ID", "").strip()
        self.affiliate_token = os.getenv("FLIPKART_AFFILIATE_TOKEN", "").strip()

    def is_configured(self) -> bool:
        return bool(self.affiliate_id and self.affiliate_token)

    def extract_product_id(self, url: str) -> Optional[str]:
        if not url:
            return None
        # Common Flipkart URL patterns: /p/itm1234567 or ?pid=ITM1234567
        m = re.search(r"[?&]pid=([A-Z0-9]+)", url, re.IGNORECASE)
        if m:
            return m.group(1)
        m = re.search(r"/p/(itm[a-z0-9]+)", url, re.IGNORECASE)
        if m:
            return m.group(1)
        return None

    def get_price(
        self,
        product_url: Optional[str] = None,
        product_name: Optional[str] = None
    ) -> PriceResult:
        if not self.is_configured():
            return PriceResult(
                source="Flipkart",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error="Flipkart Affiliate API credentials not configured (set FLIPKART_AFFILIATE_ID and FLIPKART_AFFILIATE_TOKEN)",
                match_confidence="none"
            )

        headers = {
            "Fk-Affiliate-Id": self.affiliate_id,
            "Fk-Affiliate-Token": self.affiliate_token,
            "Accept": "application/json",
        }

        pid = self.extract_product_id(product_url) if product_url else None

        try:
            if pid:
                resp = requests.get(
                    self.PRODUCT_API_URL,
                    params={"id": pid},
                    headers=headers,
                    timeout=12
                )
            elif product_name:
                resp = requests.get(
                    self.SEARCH_API_URL,
                    params={"query": product_name[:100], "resultCount": 1},
                    headers=headers,
                    timeout=12
                )
            else:
                return PriceResult(
                    source="Flipkart",
                    status="unavailable",
                    error="Neither product URL nor product name provided",
                    match_confidence="none"
                )

            if resp.status_code == 200:
                data = resp.json()
                
                # Single item from product.json
                product_info = None
                if "productBaseInfoV1" in data:
                    product_info = data["productBaseInfoV1"]
                # Search items
                elif "products" in data and data["products"]:
                    product_info = data["products"][0].get("productBaseInfoV1")

                if not product_info:
                    return PriceResult(
                        source="Flipkart",
                        status="unavailable",
                        product_url=product_url,
                        product_name=product_name,
                        error="Product not found in Flipkart affiliate catalog",
                        match_confidence="none"
                    )

                title = product_info.get("title", product_name)
                detail_url = product_info.get("productUrl", product_url)
                in_stock = product_info.get("inStock", True)

                # Check match confidence
                confidence = "exact" if pid else self.assess_product_match(product_name, title)
                if confidence == "none":
                    return PriceResult(
                        source="Flipkart",
                        status="unavailable",
                        product_url=detail_url,
                        product_name=title,
                        error=f"Candidate product does not match target specifications (found '{title}')",
                        match_confidence="uncertain"
                    )

                # Selling price
                price_obj = product_info.get("flipkartSellingPrice") or product_info.get("flipkartSpecialPrice") or {}
                amount = price_obj.get("amount")
                currency = price_obj.get("currency", "INR")

                parsed_price = self.clean_price_value(amount)
                if parsed_price is None:
                    return PriceResult(
                        source="Flipkart",
                        status="unavailable",
                        product_url=detail_url,
                        product_name=title,
                        availability=in_stock,
                        error="Price not currently available from seller listing",
                        match_confidence=confidence
                    )

                return PriceResult(
                    source="Flipkart",
                    status="success",
                    product_name=title,
                    product_url=detail_url,
                    price=parsed_price,
                    currency=currency,
                    availability=in_stock,
                    match_confidence=confidence
                )

            elif resp.status_code in (401, 403):
                return PriceResult(
                    source="Flipkart",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error="Flipkart Affiliate API authentication failed. Verify affiliate ID and token.",
                    match_confidence="none"
                )
            elif resp.status_code == 429:
                return PriceResult(
                    source="Flipkart",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error="Flipkart Affiliate API rate limit exceeded. Please retry shortly.",
                    match_confidence="none"
                )
            else:
                return PriceResult(
                    source="Flipkart",
                    status="unavailable",
                    product_url=product_url,
                    product_name=product_name,
                    error=f"Flipkart Affiliate API returned HTTP {resp.status_code}",
                    match_confidence="none"
                )

        except requests.exceptions.Timeout:
            return PriceResult(
                source="Flipkart",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error="Flipkart Affiliate API request timed out",
                match_confidence="none"
            )
        except Exception as e:
            return PriceResult(
                source="Flipkart",
                status="unavailable",
                product_url=product_url,
                product_name=product_name,
                error=f"Flipkart API error: {str(e)}",
                match_confidence="none"
            )
