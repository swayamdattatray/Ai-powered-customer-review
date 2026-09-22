"""
Fake Review Detector Tool.
Evaluates the authenticity of customer reviews and assigns a suspicion risk score (0-100%).
Uses lightning-fast heuristic pattern rules for batch processing,
and utilizes LLM for deep reasoning on sample suspicious reviews.
"""

import logging
import re
from typing import List, Dict, Any, Optional
import config
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class FakeReviewDetector:
    """Tool for analyzing review authenticity and suspicious patterns."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    @staticmethod
    def _heuristic_suspicion_score(review_text: str, rating: Optional[int] = None) -> Dict[str, Any]:
        """Calculates a baseline heuristic suspicion score using pattern rules."""
        text = str(review_text).strip()
        score = 8
        reasons = []

        # Rule 1: Extremely short review with extreme rating
        if len(text.split()) <= 4 and (rating == 5 or rating == 1):
            score += 45
            reasons.append("Extremely short review with extreme rating")

        # Rule 2: Excessive repeated superlatives / hype words
        hype_count = len(re.findall(r"\b(best ever|amazing|perfect|greatest|buy now|love it)\b", text.lower()))
        if hype_count >= 3:
            score += 55
            reasons.append("High density of repetitive superlatives and marketing hype")
        elif hype_count == 2:
            score += 25

        # Rule 3: Excessive exclamation points
        if text.count("!") >= 3:
            score += 20
            reasons.append("Unusual exclamation punctuation patterns")

        final_score = min(100, max(0, score))
        is_suspicious = final_score >= config.SUSPICION_THRESHOLD

        return {
            "is_suspicious": is_suspicious,
            "suspicion_score": final_score,
            "risk_level": "High Suspicion" if final_score >= 60 else ("Moderate Suspicion" if final_score >= 35 else "Low Suspicion"),
            "reasoning": "; ".join(reasons) if reasons else "Review shows standard natural expression patterns."
        }

    def evaluate_review(self, review_text: str, rating: Optional[int] = None, use_llm: bool = False) -> Dict[str, Any]:
        """Evaluates a single review for potential inauthenticity."""
        if not review_text or not review_text.strip():
            return {
                "is_suspicious": False,
                "suspicion_score": 0,
                "risk_level": "Low Suspicion",
                "reasoning": "Empty review."
            }

        if use_llm and self.llm and self.llm.is_available():
            prompt = f"""You are an expert in customer review authenticity.
Evaluate the following review for potential suspicious or inauthentic patterns.

Review:
"{review_text}"

Respond ONLY with a JSON object in this exact schema:
{{
    "is_suspicious": true or false,
    "suspicion_score": <integer from 0 to 100>,
    "reasoning": "<concise 1-2 sentence explanation>"
}}
"""
            result = self.llm.generate_json(prompt)
            if result and "suspicion_score" in result:
                score = int(result.get("suspicion_score", 15))
                score = max(0, min(100, score))
                is_suspicious = score >= config.SUSPICION_THRESHOLD

                return {
                    "is_suspicious": is_suspicious,
                    "suspicion_score": score,
                    "risk_level": "High Suspicion" if score >= 60 else ("Moderate Suspicion" if score >= 35 else "Low Suspicion"),
                    "reasoning": result.get("reasoning", "Assessed by AI authenticity model.")
                }

        # Fast heuristic evaluation
        return self._heuristic_suspicion_score(review_text, rating)

    def evaluate_batch(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates an entire collection of reviews efficiently."""
        if not reviews:
            return {
                "total_reviewed": 0,
                "suspicious_count": 0,
                "suspicious_percentage": 0,
                "average_suspicion_score": 0,
                "flagged_reviews": []
            }

        flagged = []
        total_score = 0

        for r in reviews:
            text = r.get("review_text", "")
            rating = r.get("rating")
            eval_res = self.evaluate_review(text, rating, use_llm=False)

            total_score += eval_res["suspicion_score"]
            if eval_res["is_suspicious"]:
                flagged.append({
                    "review_text": text,
                    "suspicion_score": eval_res["suspicion_score"],
                    "reasoning": eval_res["reasoning"]
                })

        count = len(reviews)
        suspicious_count = len(flagged)
        avg_score = round(total_score / count) if count > 0 else 0
        suspicious_pct = round((suspicious_count / count) * 100) if count > 0 else 0

        return {
            "total_reviewed": count,
            "suspicious_count": suspicious_count,
            "suspicious_percentage": suspicious_pct,
            "average_suspicion_score": avg_score,
            "flagged_reviews": flagged
        }
