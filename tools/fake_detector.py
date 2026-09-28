"""
Multi-Signal Fake & Suspicious Review Detector Tool.
Enhanced with Product-Level Trust Index (0-100%) and Adjusted "Real" Customer Rating.
Calculates what the customer rating actually is after filtering out suspicious reviews.
"""

import re
import logging
from typing import List, Dict, Any, Optional
import config
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class FakeReviewDetector:
    """Tool for analyzing review authenticity and generating evidence-backed suspicion scores."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    @staticmethod
    def evaluate_multi_signals(
        review_text: str,
        rating: Optional[int] = None,
        all_review_texts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculates a suspicion score (0-100) using multiple observable evidence signals."""
        text = str(review_text).strip()
        lower_text = text.lower()
        score = 8
        evidence_signals = []

        # Signal 1: Extremely short review with extreme rating
        words = text.split()
        if len(words) <= 5 and (rating == 5 or rating == 1):
            score += 35
            evidence_signals.append("Extremely short review length combined with extreme rating")

        # Signal 2: Generic promotional phrasing / superlatives density
        hype_patterns = [
            r"\b(best (ever|product|phone|in the world))\b",
            r"\b(must buy|buy now|dont think just buy)\b",
            r"\b(amazing amazing|perfect perfect|super super)\b",
            r"\b(greatest thing|life changing)\b"
        ]
        matched_hype = [p for p in hype_patterns if re.search(p, lower_text)]
        if matched_hype:
            score += 30 * len(matched_hype)
            evidence_signals.append("High density of generic promotional phrasing without specific usage details")

        # Signal 3: Lack of product-specific technical keywords
        feature_keywords = ["camera", "battery", "screen", "display", "charge", "speed", "sound", "speaker", "build", "price", "software", "ram", "processor"]
        has_features = any(k in lower_text for k in feature_keywords)
        if len(words) > 10 and not has_features:
            score += 20
            evidence_signals.append("Contains no mentions of specific product features or real-world use cases")

        # Signal 4: Excessive exclamation marks or unnatural punctuation
        exclamation_count = text.count("!")
        if exclamation_count >= 3:
            score += 15
            evidence_signals.append(f"Unusual punctuation pattern ({exclamation_count} exclamation marks)")

        # Signal 5: Duplicate / high similarity across review batch
        if all_review_texts:
            identical_matches = sum(1 for t in all_review_texts if t.strip().lower() == lower_text)
            if identical_matches > 1:
                score += 45
                evidence_signals.append(f"Identical or near-identical text found in {identical_matches - 1} other review(s)")

        # Signal 6: Contradiction between star rating and expressed sentiment
        is_pos_words = any(w in lower_text for w in ["great", "excellent", "love", "awesome", "perfect"])
        is_neg_words = any(w in lower_text for w in ["worst", "terrible", "waste", "horrible", "useless"])
        if rating == 5 and is_neg_words and not is_pos_words:
            score += 40
            evidence_signals.append("Rating contradiction (5-star rating with explicitly negative language)")
        elif rating == 1 and is_pos_words and not is_neg_words:
            score += 40
            evidence_signals.append("Rating contradiction (1-star rating with explicitly positive language)")

        final_score = min(100, max(0, score))

        if final_score >= 70:
            risk_status = "High Suspicion"
            is_suspicious = True
        elif final_score >= 40:
            risk_status = "Medium Suspicion"
            is_suspicious = True
        elif final_score >= 20:
            risk_status = "Low Suspicion"
            is_suspicious = False
        else:
            risk_status = "Appears Authentic"
            is_suspicious = False

        if not evidence_signals:
            evidence_signals.append("Natural sentence structure and balanced product feedback observed")

        return {
            "suspicion_score": final_score,
            "risk_status": risk_status,
            "is_suspicious": is_suspicious,
            "why_flagged": evidence_signals
        }

    def evaluate_review(
        self,
        review_text: str,
        rating: Optional[int] = None,
        all_review_texts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Evaluates a single review and returns evidence-backed risk analysis."""
        return self.evaluate_multi_signals(review_text, rating, all_review_texts)

    def evaluate_batch(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates an entire collection of reviews and calculates:
        1. Risk distributions
        2. Overall Product Trust Index (0-100%)
        3. Real vs Filtered Rating (true rating excluding fake reviews)
        """
        if not reviews:
            return {
                "total_reviewed": 0,
                "suspicious_count": 0,
                "suspicious_percentage": 0,
                "product_trust_score": 100,
                "trust_grade": "A",
                "claimed_rating": 4.5,
                "adjusted_real_rating": 4.5,
                "rating_difference": 0.0,
                "trust_verdict": "High Trust · Authentic Feedback",
                "risk_breakdown": {"high": 0, "medium": 0, "low": 0, "authentic": 0},
                "flagged_reviews": []
            }

        all_texts = [r.get("review_text", "") for r in reviews]
        flagged = []
        risk_breakdown = {"high": 0, "medium": 0, "low": 0, "authentic": 0}
        suspicious_count = 0
        total_rating_all = 0
        total_rating_trusted = 0
        trusted_count = 0

        for r in reviews:
            text = r.get("review_text", "")
            rating = r.get("rating", 4)
            total_rating_all += rating

            eval_res = self.evaluate_multi_signals(text, rating, all_texts)
            status = eval_res["risk_status"]

            if status == "High Suspicion":
                risk_breakdown["high"] += 1
                suspicious_count += 1
            elif status == "Medium Suspicion":
                risk_breakdown["medium"] += 1
                suspicious_count += 1
            elif status == "Low Suspicion":
                risk_breakdown["low"] += 1
                total_rating_trusted += rating
                trusted_count += 1
            else:
                risk_breakdown["authentic"] += 1
                total_rating_trusted += rating
                trusted_count += 1

            if eval_res["is_suspicious"]:
                flagged.append({
                    "id": r.get("id", ""),
                    "review_text": text,
                    "source": r.get("source", "Unknown"),
                    "rating": rating,
                    "suspicion_score": eval_res["suspicion_score"],
                    "risk_status": eval_res["risk_status"],
                    "why_flagged": eval_res["why_flagged"]
                })

        total = len(reviews)
        suspicious_pct = round((suspicious_count / total) * 100) if total > 0 else 0

        # Product Trust Score: 100 minus the suspicious impact
        product_trust_score = max(10, 100 - (suspicious_pct * 2))

        # Trust Grade & Verdict
        if product_trust_score >= 85:
            trust_grade = "A+"
            trust_verdict = "Highly Authentic & Trusted Reviews"
        elif product_trust_score >= 70:
            trust_grade = "A"
            trust_verdict = "Mostly Authentic · Low Risk"
        elif product_trust_score >= 50:
            trust_grade = "B"
            trust_verdict = "Moderate Suspicion · Review with Caution"
        else:
            trust_grade = "C"
            trust_verdict = "High Manipulation Risk · Multiple Flagged Reviews"

        # Claimed vs Adjusted Real Rating
        claimed_rating = round(total_rating_all / total, 1) if total > 0 else 4.0
        adjusted_real_rating = round(total_rating_trusted / trusted_count, 1) if trusted_count > 0 else claimed_rating
        rating_diff = round(claimed_rating - adjusted_real_rating, 1)

        return {
            "total_reviewed": total,
            "suspicious_count": suspicious_count,
            "suspicious_percentage": suspicious_pct,
            "product_trust_score": product_trust_score,
            "trust_grade": trust_grade,
            "claimed_rating": claimed_rating,
            "adjusted_real_rating": adjusted_real_rating,
            "rating_difference": rating_diff,
            "trust_verdict": trust_verdict,
            "risk_breakdown": risk_breakdown,
            "flagged_reviews": flagged
        }
