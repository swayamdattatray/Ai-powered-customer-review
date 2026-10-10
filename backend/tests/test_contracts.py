"""
Unit Tests for Shopping Intelligence Backend API Contracts & Services.
"""

import sys
from pathlib import Path
import unittest
from fastapi.testclient import TestClient

# Ensure root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.services.product_matcher import ProductMatcher
from backend.app.services.review_auditor import ReviewAuditor
from backend.app.schemas.contracts import ClientReviewItem


class TestShoppingIntelligenceAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")

    def test_02_product_matcher_variant_isolation(self):
        # Mismatch on storage: 128GB vs 256GB
        conf, score, deltas = ProductMatcher.evaluate_match(
            "Apple iPhone 16 (128 GB) - Black",
            "Apple iPhone 16 (256 GB) - Black"
        )
        self.assertEqual(conf, "MISMATCH")
        self.assertTrue(any("Storage capacity diverged" in d for d in deltas))

        # Condition mismatch: Brand New vs Renewed
        conf_cond, _, deltas_cond = ProductMatcher.evaluate_match(
            "Apple iPhone 16 (128 GB) - Black",
            "Apple iPhone 16 (128 GB) - Black (Refurbished)"
        )
        self.assertEqual(conf_cond, "MISMATCH")
        self.assertTrue(any("Condition mismatch" in d for d in deltas_cond))

        # Exact match
        conf_exact, _, _ = ProductMatcher.evaluate_match(
            "Apple iPhone 16 (128 GB) - Black",
            "Apple iPhone 16 128GB Black Smartphone"
        )
        self.assertIn(conf_exact, ("EXACT", "HIGH"))

    def test_03_review_auditor_near_duplicate_detection(self):
        # Create reviews with repeated spam template
        reviews = [
            ClientReviewItem(id="1", rating=5.0, text="Best product ever in this price segment blindly go for it."),
            ClientReviewItem(id="2", rating=5.0, text="Best product ever in this price segment blindly go for it."),
            ClientReviewItem(id="3", rating=5.0, text="Best product ever in this price segment blindly go for it."),
            ClientReviewItem(id="4", rating=4.0, text="Battery life is decent, lasts about one day with normal usage.")
        ]
        audit = ReviewAuditor.audit_reviews(reviews, total_ratings=100)
        self.assertLess(audit.trust_score, 80.0)
        self.assertGreater(audit.duplicate_cluster_ratio, 0.4)
        self.assertTrue(any(s.signal_type == "NEAR_DUPLICATE_CLUSTER" for s in audit.signals))

    def test_04_analyze_endpoint_e2e(self):
        payload = {
            "url": "https://www.amazon.in/dp/B0GQVL6STN",
            "platform": "AMAZON_IN",
            "sku": "B0GQVL6STN",
            "title": "Apple iPhone 17e (256 GB) - Black",
            "brand": "Apple",
            "listed_price": 79999.0,
            "currency": "INR",
            "rating": 4.4,
            "rating_count": 165,
            "availability": True,
            "reviews": [
                {"id": "r1", "rating": 5.0, "text": "Display is brilliant and battery easily lasts 1.5 days."},
                {"id": "r2", "rating": 4.0, "text": "Camera quality is decent, but slight heating under heavy gaming."},
                {"id": "r3", "rating": 5.0, "text": "Performance of the chip is blazing fast, loved the build quality."}
            ]
        }
        res = self.client.post("/api/v1/intelligence/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["title"], payload["title"])
        self.assertEqual(data["primary_platform"], "AMAZON_IN")
        self.assertIn("credibility", data)
        self.assertIn("prices", data)
        self.assertIn("arbitrage", data)
        self.assertGreaterEqual(data["credibility"]["trust_score"], 0.0)
        self.assertLessEqual(data["credibility"]["trust_score"], 100.0)
        # Verify Option A: Price history is included
        self.assertIn("history", data)
        self.assertTrue(data["history"]["has_history"])
        self.assertIn(data["history"]["recommendation"], ("GOOD_TIME_TO_BUY", "WAIT_FOR_SALE", "FAIR"))
        self.assertGreaterEqual(len(data["history"]["history_points"]), 1)
        # Verify Option D: Retailer expansion includes Croma and Reliance Digital
        retailers = [p["platform"].lower() for p in data["prices"]]
        self.assertTrue(any("croma" in r for r in retailers))
        self.assertTrue(any("reliance" in r for r in retailers))
        # Verify Review Authenticity & Scam Risk
        self.assertIn("estimated_genuine_pct", data["credibility"])
        self.assertIn("estimated_fake_pct", data["credibility"])
        self.assertIn(data["credibility"]["authenticity_status"], ("LIKELY_AUTHENTIC", "MODERATE_SUSPICION", "HIGH_FAKE_RISK"))
        self.assertIn("scam_risk", data)
        self.assertIn(data["scam_risk"]["risk_level"], ("LOW", "MODERATE", "HIGH", "CRITICAL"))
        self.assertGreaterEqual(len(data["scam_risk"]["safety_checklist"]), 1)

    def test_05_historical_price_tracker(self):
        from backend.app.services.history_tracker import PriceHistoryTracker
        analytics = PriceHistoryTracker.get_analytics(
            product_name="Apple iPhone 17e 256GB",
            current_price=79999.0,
            platform="AMAZON_IN"
        )
        self.assertTrue(analytics.has_history)
        self.assertIsNotNone(analytics.lowest_recorded)
        self.assertIsNotNone(analytics.highest_recorded)
        self.assertIsNotNone(analytics.average_recorded)
        self.assertIn(analytics.recommendation, ("GOOD_TIME_TO_BUY", "WAIT_FOR_SALE", "FAIR"))
        self.assertTrue(len(analytics.history_points) > 0)

    def test_06_aspect_explorer_grounded_snippets(self):
        reviews = [
            ClientReviewItem(id="r1", rating=5.0, text="Battery life easily lasts two days on a single charge."),
            ClientReviewItem(id="r2", rating=4.0, text="Display is super bright with vibrant OLED colors.")
        ]
        audit = ReviewAuditor.audit_reviews(reviews, total_ratings=50)
        self.assertTrue(len(audit.aspects) > 0)
        for asp in audit.aspects:
            self.assertIsInstance(asp.grounded_snippets, list)
            self.assertGreaterEqual(len(asp.grounded_snippets), 1)

    def test_07_scam_risk_engine_anomalies(self):
        from backend.app.services.scam_engine import ScamRiskEngine
        from backend.app.schemas.contracts import ExtractedProductPayload, PriceHistoryAnalytics
        # Suspicious listing: extremely cheap iPhone from unrated 3rd-party merchant with non-returnable policy
        payload = ExtractedProductPayload(
            url="https://www.amazon.in/dp/B0DFAKE123",
            platform="AMAZON_IN",
            sku="B0DFAKE123",
            title="Apple iPhone 16 Pro Max 256GB",
            listed_price=18999.0,  # Abnormal: normally ₹1,20,000+
            seller_name="QuickDeals999",
            is_fulfilled_by_platform=False,
            return_policy="Non-Returnable",
            rating=2.1,
            rating_count=3
        )
        audit = ReviewAuditor.audit_reviews([
            ClientReviewItem(id="1", rating=5.0, text="blindly go for it value for money value for money"),
            ClientReviewItem(id="2", rating=5.0, text="blindly go for it value for money value for money"),
        ])
        hist = PriceHistoryAnalytics(
            has_history=True,
            current_price=18999.0,
            average_recorded=129900.0
        )
        scam = ScamRiskEngine.evaluate_scam_risk(payload, audit, hist)
        self.assertGreaterEqual(scam.risk_score, 60.0)
        self.assertIn(scam.risk_level, ("HIGH", "CRITICAL"))
        self.assertTrue(len(scam.warning_flags) >= 2)
        self.assertTrue(any("below historical average" in w for w in scam.warning_flags))
        self.assertTrue(any("non-returnable" in w for w in scam.warning_flags))


if __name__ == "__main__":
    unittest.main()
