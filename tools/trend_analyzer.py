"""
Trend and Pattern Analyzer Tool.
Identifies recurring customer complaints, positive patterns, major strengths,
and major concerns across all collected reviews.
"""

import logging
from typing import List, Dict, Any, Optional
import config
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Tool for detecting recurring themes, common complaints, and positive highlights."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    @staticmethod
    def _heuristic_trends(reviews: List[Dict[str, Any]], aspect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts patterns and trends using statistical rules & aspect data."""
        most_liked = []
        most_complained = []

        # Find aspects with highest scores for strengths
        sorted_aspects = sorted(
            aspect_data.items(),
            key=lambda item: item[1].get("score_percent", 0),
            reverse=True
        )

        for aspect, data in sorted_aspects:
            score = data.get("score_percent", 0)
            if score >= 65 and len(most_liked) < 5:
                most_liked.append(f"{aspect.capitalize()} quality and satisfaction")
            elif score <= 50 and len(most_complained) < 5:
                most_complained.append(f"{aspect.capitalize()} issues and concerns")

        # Fallback default items if few aspects were mentioned
        if not most_liked:
            most_liked = ["Overall build quality", "Design and aesthetics", "Core feature reliability"]
        if not most_complained:
            most_complained = ["Battery life under heavy use", "Pricing considerations", "Minor software bugs"]

        return {
            "most_liked": most_liked,
            "most_complained": most_complained,
            "recurring_complaints": most_complained[:3],
            "positive_patterns": most_liked[:3]
        }

    def analyze_trends(self, reviews: List[Dict[str, Any]], aspect_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discovers common topics, recurring complaints, and positive themes.
        
        Returns:
            Dict containing:
            - 'most_liked': List[str]
            - 'most_complained': List[str]
            - 'recurring_complaints': List[str]
            - 'positive_patterns': List[str]
        """
        if not reviews:
            return {
                "most_liked": [],
                "most_complained": [],
                "recurring_complaints": [],
                "positive_patterns": []
            }

        if self.llm and self.llm.is_available():
            # Sample up to MAX_REVIEWS_FOR_LLM_SUMMARY reviews
            sample_texts = [
                f"- {r.get('review_text', '')}"
                for r in reviews[:config.MAX_REVIEWS_FOR_LLM_SUMMARY]
            ]
            joined_reviews = "\n".join(sample_texts)

            prompt = f"""You are a product intelligence analyst.
Analyze these customer reviews and identify the top recurring positive patterns and customer complaints.

Customer Reviews:
{joined_reviews}

Respond ONLY with a JSON object in this exact schema:
{{
    "most_liked": ["<specific positive theme 1>", "<specific positive theme 2>", "<specific positive theme 3>", "<specific positive theme 4>"],
    "most_complained": ["<specific complaint 1>", "<specific complaint 2>", "<specific complaint 3>", "<specific complaint 4>"]
}}

Rules:
- Be concise, specific to the product features (e.g. 'Battery drains quickly', 'Camera low-light clarity', 'Smooth 120Hz display').
- Max 5 items per list.
"""
            result = self.llm.generate_json(prompt)
            if result and "most_liked" in result and "most_complained" in result:
                liked = result.get("most_liked", [])
                complained = result.get("most_complained", [])
                return {
                    "most_liked": liked if isinstance(liked, list) else [],
                    "most_complained": complained if isinstance(complained, list) else [],
                    "recurring_complaints": complained[:3] if isinstance(complained, list) else [],
                    "positive_patterns": liked[:3] if isinstance(liked, list) else []
                }

        # Fallback to rule-based analysis
        return self._heuristic_trends(reviews, aspect_data)
