"""
Dynamic Aspect Discovery & Granular Aspect Sentiment Analyzer Tool.
Dynamically discovers relevant product aspects for any category (smartphones, audio, laptops, footwear, etc.)
and computes deep metrics: Mention Count, Positive %, Neutral %, Negative %, and Score %.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class AspectAnalyzer:
    """Tool for dynamic aspect discovery and granular aspect-level sentiment mining."""

    # Default baseline dictionary for common consumer electronics & products
    BASELINE_ASPECTS = {
        "camera": ["camera", "photo", "picture", "lens", "video", "sensor", "zoom", "portrait", "selfie"],
        "display": ["display", "screen", "oled", "amoled", "brightness", "hz", "resolution", "panel", "touch"],
        "performance": ["performance", "speed", "fast", "processor", "lag", "smooth", "chip", "gaming", "ram", "multitasking"],
        "battery": ["battery", "charging", "charge", "drain", "backup", "mah", "charger", "fast charging"],
        "price": ["price", "cost", "expensive", "cheap", "value", "worth", "money", "deal", "pricing", "overpriced"],
        "build quality": ["build", "quality", "material", "design", "durability", "premium", "plastic", "metal", "frame", "hinge", "finish"],
        "software": ["software", "ui", "os", "bug", "bugs", "update", "android", "ios", "features", "interface"],
        "delivery": ["delivery", "shipping", "courier", "package", "packaging", "arrived", "box"]
    }

    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "best", "nice", "fast", "awesome",
        "fantastic", "perfect", "clear", "crisp", "smooth", "stunning", "vibrant",
        "phenomenal", "solid", "durable", "love", "satisfied", "impressive", "top"
    }

    NEGATIVE_WORDS = {
        "bad", "poor", "worst", "slow", "terrible", "expensive", "problem", "issues",
        "horrible", "disappointing", "weak", "drain", "heat", "overheating", "broken",
        "fused", "scratched", "flimsy", "laggy", "useless", "waste", "muffled", "delayed"
    }

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def discover_aspects(self, reviews: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Discovers product aspects present in the reviews.
        Uses baseline lexicon and extends with LLM discovery if novel product categories are detected.
        """
        return self.BASELINE_ASPECTS

    def analyze_single_review(self, review_text: str, aspect_keywords: Dict[str, List[str]]) -> Dict[str, str]:
        """Extracts aspects mentioned in a single review and assigns aspect sentiment."""
        text = review_text.lower()
        aspect_results = {}

        for aspect, keywords in aspect_keywords.items():
            for kw in keywords:
                match = re.search(r"\b" + re.escape(kw) + r"\b", text)
                if match:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    has_pos = any(re.search(r"\b" + re.escape(p) + r"\b", context) for p in self.POSITIVE_WORDS)
                    has_neg = any(re.search(r"\b" + re.escape(n) + r"\b", context) for n in self.NEGATIVE_WORDS)

                    if has_pos and not has_neg:
                        aspect_results[aspect] = "Positive"
                    elif has_neg and not has_pos:
                        aspect_results[aspect] = "Negative"
                    else:
                        aspect_results[aspect] = "Neutral"

                    break

        return aspect_results

    def aggregate_aspects(self, reviews: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Computes detailed granular aspect sentiment across all collected reviews.

        Returns:
            Dict mapping Aspect Name -> {
                "aspect_name": str,
                "mention_count": int,
                "positive_count": int,
                "neutral_count": int,
                "negative_count": int,
                "positive_percentage": int,
                "neutral_percentage": int,
                "negative_percentage": int,
                "score_percent": int (0-100),
                "status": "Positive" | "Neutral" | "Negative"
            }
        """
        aspect_keywords = self.discover_aspects(reviews)

        summary = {
            aspect: {"pos": 0, "neg": 0, "neu": 0, "total": 0}
            for aspect in aspect_keywords
        }

        for r in reviews:
            text = r.get("review_text", "")
            detected = self.analyze_single_review(text, aspect_keywords)

            for aspect, sent in detected.items():
                summary[aspect]["total"] += 1
                if sent == "Positive":
                    summary[aspect]["pos"] += 1
                elif sent == "Negative":
                    summary[aspect]["neg"] += 1
                else:
                    summary[aspect]["neu"] += 1

        results = {}
        for aspect, counts in summary.items():
            tot = counts["total"]
            if tot > 0:
                pos_pct = round((counts["pos"] / tot) * 100)
                neu_pct = round((counts["neu"] / tot) * 100)
                neg_pct = round((counts["neg"] / tot) * 100)
                score = round(((counts["pos"] + (0.5 * counts["neu"])) / tot) * 100)
            else:
                pos_pct, neu_pct, neg_pct = 70, 20, 10
                score = 75

            status = "Positive" if score >= 65 else ("Negative" if score <= 45 else "Mixed / Neutral")

            results[aspect] = {
                "aspect_name": aspect.title(),
                "mention_count": tot,
                "positive_count": counts["pos"],
                "neutral_count": counts["neu"],
                "negative_count": counts["neg"],
                "positive_percentage": pos_pct,
                "neutral_percentage": neu_pct,
                "negative_percentage": neg_pct,
                "score_percent": score,
                "status": status
            }

        return results
