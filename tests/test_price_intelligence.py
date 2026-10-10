"""
Comprehensive Unit Tests for Price Intelligence Module.
Uses mocked API responses so tests are fast, deterministic, and never call live APIs.

Scenarios tested:
  1. Successful Amazon price response (mocked PA-API 5.0)
  2. Successful Flipkart price response (mocked Affiliate API)
  3. Missing API credentials
  4. Product not found
  5. API timeout
  6. Invalid / malformed API response
  7. Product mismatch (variant/storage mismatch)
  8. One source failing while another succeeds
  9. Price comparison calculation (lowest, highest, difference, percentages)
  10. No available prices (all sources fail/unconfigured)
"""

import unittest
from unittest.mock import patch, MagicMock
import requests

from price_intelligence.models import PriceResult
from price_intelligence.base_price_collector import BasePriceCollector
from price_intelligence.amazon_price_collector import AmazonPriceCollector
from price_intelligence.flipkart_price_collector import FlipkartPriceCollector
from price_intelligence.price_collector_factory import PriceCollectorFactory
from price_intelligence.price_service import PriceService


class TestPriceIntelligence(unittest.TestCase):

    def setUp(self):
        self.service = PriceService()

    # --------------------------------------------------------------------------
    # 1. Successful Amazon Price Response (Mocked PA-API)
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {
        "AMAZON_ACCESS_KEY": "test_access_key",
        "AMAZON_SECRET_KEY": "test_secret_key",
        "AMAZON_PARTNER_TAG": "test_tag-21"
    })
    @patch.object(AmazonPriceCollector, "_call_paapi")
    def test_01_successful_amazon_price(self, mock_call):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "ItemsResult": {
                "Items": [{
                    "ASIN": "B0GQVL6STN",
                    "DetailPageURL": "https://www.amazon.in/dp/B0GQVL6STN",
                    "ItemInfo": {"Title": {"DisplayValue": "Apple iPhone 17e 256 GB Black"}},
                    "Offers": {
                        "Listings": [{
                            "Price": {"Amount": 79999.0, "Currency": "INR"},
                            "Availability": {"Message": "In Stock."}
                        }]
                    }
                }]
            }
        }
        mock_call.return_value = mock_resp

        collector = AmazonPriceCollector()
        result = collector.get_price(product_url="https://www.amazon.in/dp/B0GQVL6STN")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.source, "Amazon")
        self.assertEqual(result.price, 79999.0)
        self.assertEqual(result.currency, "INR")
        self.assertTrue(result.availability)
        self.assertEqual(result.match_confidence, "exact")
        self.assertIn("₹79,999", result.to_dict()["formatted_price"])

    # --------------------------------------------------------------------------
    # 2. Successful Flipkart Price Response (Mocked Affiliate API)
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {
        "FLIPKART_AFFILIATE_ID": "test_affiliate_id",
        "FLIPKART_AFFILIATE_TOKEN": "test_token_123"
    })
    @patch("requests.get")
    def test_02_successful_flipkart_price(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "productBaseInfoV1": {
                "productId": "MOBGQVL6STN",
                "title": "Apple iPhone 17e (Black, 256 GB)",
                "productUrl": "https://www.flipkart.com/apple-iphone-17e/p/itmgqvl6stn",
                "inStock": True,
                "flipkartSellingPrice": {"amount": 78499.0, "currency": "INR"}
            }
        }
        mock_get.return_value = mock_resp

        collector = FlipkartPriceCollector()
        result = collector.get_price(product_url="https://www.flipkart.com/apple-iphone-17e/p/itmgqvl6stn")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.source, "Flipkart")
        self.assertEqual(result.price, 78499.0)
        self.assertTrue(result.availability)
        self.assertIn("₹78,499", result.to_dict()["formatted_price"])

    # --------------------------------------------------------------------------
    # 3. Missing API Credentials Handling
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {}, clear=True)
    def test_03_missing_credentials(self):
        amz = AmazonPriceCollector()
        fk = FlipkartPriceCollector()

        res_amz = amz.get_price(product_name="iPhone 17")
        res_fk = fk.get_price(product_name="iPhone 17")

        self.assertEqual(res_amz.status, "unavailable")
        self.assertIsNone(res_amz.price)
        self.assertIn("credentials not configured", res_amz.error.lower())

        self.assertEqual(res_fk.status, "unavailable")
        self.assertIsNone(res_fk.price)
        self.assertIn("credentials not configured", res_fk.error.lower())

        # Crucial requirement: Never replace failed values with 0!
        self.assertNotEqual(res_amz.price, 0)
        self.assertNotEqual(res_fk.price, 0)

    # --------------------------------------------------------------------------
    # 4. Product Not Found in Catalog
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {
        "AMAZON_ACCESS_KEY": "key",
        "AMAZON_SECRET_KEY": "sec",
        "AMAZON_PARTNER_TAG": "tag"
    })
    @patch.object(AmazonPriceCollector, "_call_paapi")
    def test_04_product_not_found(self, mock_call):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ItemsResult": {"Items": []}}
        mock_call.return_value = mock_resp

        collector = AmazonPriceCollector()
        result = collector.get_price(product_url="https://www.amazon.in/dp/BNONEXISTENT")

        self.assertEqual(result.status, "unavailable")
        self.assertIsNone(result.price)
        self.assertIn("not found", result.error.lower())

    # --------------------------------------------------------------------------
    # 5. API Timeout Handling
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {
        "FLIPKART_AFFILIATE_ID": "id",
        "FLIPKART_AFFILIATE_TOKEN": "tok"
    })
    @patch("requests.get", side_effect=requests.exceptions.Timeout("Connection timed out"))
    def test_05_api_timeout(self, mock_get):
        collector = FlipkartPriceCollector()
        result = collector.get_price(product_name="Apple iPhone 17")

        self.assertEqual(result.status, "unavailable")
        self.assertIsNone(result.price)
        self.assertIn("timed out", result.error.lower())

    # --------------------------------------------------------------------------
    # 6. Invalid / Malformed API Response
    # --------------------------------------------------------------------------
    @patch.dict("os.environ", {
        "AMAZON_ACCESS_KEY": "k",
        "AMAZON_SECRET_KEY": "s",
        "AMAZON_PARTNER_TAG": "t"
    })
    @patch.object(AmazonPriceCollector, "_call_paapi")
    def test_06_malformed_response(self, mock_call):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {"Error": "InternalFailure"}
        mock_call.return_value = mock_resp

        collector = AmazonPriceCollector()
        result = collector.get_price(product_url="https://www.amazon.in/dp/B0GQVL6STN")

        self.assertEqual(result.status, "unavailable")
        self.assertIsNone(result.price)
        self.assertIn("500", result.error)

    # --------------------------------------------------------------------------
    # 7. Product Mismatch Detection (e.g. 128GB target vs 512GB candidate)
    # --------------------------------------------------------------------------
    def test_07_product_mismatch(self):
        collector = AmazonPriceCollector()
        
        # Exact match
        conf1 = collector.assess_product_match(
            "Apple iPhone 17e 256 GB Black",
            "Apple iPhone 17e (256 GB) - Black"
        )
        self.assertIn(conf1, ["exact", "high"])

        # Storage mismatch: 128 GB vs 512 GB
        conf2 = collector.assess_product_match(
            "Apple iPhone 17 128 GB Black",
            "Apple iPhone 17 512 GB Blue"
        )
        self.assertEqual(conf2, "uncertain")

        # Completely different product
        conf3 = collector.assess_product_match(
            "Apple iPhone 17 256 GB",
            "Samsung Galaxy Z Fold 8 Ultra"
        )
        self.assertEqual(conf3, "none")

    # --------------------------------------------------------------------------
    # 8. One Source Succeeds While Another Fails (Partial Comparison)
    # --------------------------------------------------------------------------
    @patch.object(AmazonPriceCollector, "get_price")
    @patch.object(FlipkartPriceCollector, "get_price")
    def test_08_one_source_success_one_fails(self, mock_fk, mock_amz):
        mock_amz.return_value = PriceResult(
            source="Amazon",
            status="success",
            product_name="iPhone 17 256GB",
            price=79999.0,
            currency="INR"
        )
        mock_fk.return_value = PriceResult(
            source="Flipkart",
            status="unavailable",
            error="Flipkart API credentials not configured"
        )

        comparison = self.service.compare_prices(product_name="iPhone 17 256GB")

        summary = comparison["summary"]
        self.assertTrue(summary["has_comparison"])
        self.assertEqual(summary["sources_compared"], 1)
        self.assertEqual(summary["lowest_price"], 79999.0)
        self.assertEqual(summary["highest_price"], 79999.0)
        self.assertEqual(summary["price_difference"], 0.0)
        self.assertEqual(len(comparison["valid_prices"]), 1)
        self.assertEqual(len(comparison["prices"]), 2)

    # --------------------------------------------------------------------------
    # 9. Price Comparison Calculation (Lowest, Highest, Difference, Percentage)
    # --------------------------------------------------------------------------
    @patch.object(AmazonPriceCollector, "get_price")
    @patch.object(FlipkartPriceCollector, "get_price")
    def test_09_price_comparison_calculation(self, mock_fk, mock_amz):
        mock_amz.return_value = PriceResult(
            source="Amazon",
            status="success",
            product_name="iPhone 17 256GB",
            price=79999.0,
            currency="INR"
        )
        mock_fk.return_value = PriceResult(
            source="Flipkart",
            status="success",
            product_name="iPhone 17 256GB",
            price=78499.0,
            currency="INR"
        )

        comparison = self.service.compare_prices(product_name="iPhone 17 256GB")

        summary = comparison["summary"]
        self.assertTrue(summary["has_comparison"])
        self.assertEqual(summary["sources_compared"], 2)
        self.assertEqual(summary["lowest_price"], 78499.0)
        self.assertEqual(summary["lowest_source"], "Flipkart")
        self.assertEqual(summary["highest_price"], 79999.0)
        self.assertEqual(summary["highest_source"], "Amazon")
        self.assertEqual(summary["price_difference"], 1500.0)

        # Chart data verification
        chart = comparison["chart_data"]
        self.assertEqual(chart["labels"], ["Amazon", "Flipkart"])
        self.assertEqual(chart["values"], [79999.0, 78499.0])
        self.assertEqual(chart["max_value"], 79999.0)
        self.assertAlmostEqual(chart["percentages"][0], 100.0)
        self.assertAlmostEqual(chart["percentages"][1], 98.1, places=1)

    # --------------------------------------------------------------------------
    # 10. No Available Prices (All Unconfigured / Failed)
    # --------------------------------------------------------------------------
    @patch.object(AmazonPriceCollector, "get_price")
    @patch.object(FlipkartPriceCollector, "get_price")
    def test_10_no_available_prices(self, mock_fk, mock_amz):
        mock_amz.return_value = PriceResult(
            source="Amazon",
            status="unavailable",
            error="Amazon credentials missing"
        )
        mock_fk.return_value = PriceResult(
            source="Flipkart",
            status="unavailable",
            error="Flipkart credentials missing"
        )

        comparison = self.service.compare_prices(product_name="iPhone 17")

        summary = comparison["summary"]
        self.assertFalse(summary["has_comparison"])
        self.assertEqual(summary["sources_compared"], 0)
        self.assertIsNone(summary["lowest_price"])
        self.assertIsNone(summary["highest_price"])
        self.assertIsNone(summary["price_difference"])
        self.assertEqual(len(comparison["valid_prices"]), 0)


if __name__ == "__main__":
    unittest.main()
