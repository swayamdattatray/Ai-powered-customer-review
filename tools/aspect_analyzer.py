"""
Aspect Analyzer Tool.
Discovers product aspects (Camera, Battery, Display, Performance, Price, Build Quality, etc.)
and computes aspect-level sentiment ratings and score percentages.
"""

import re
from typing import List, Dict, Any


class AspectAnalyzer:
    """Tool for extracting product aspects and computing aspect-specific sentiment."""

    DEFAULT_KEYWORDS = {
        "camera": ["camera", "photo", "picture", "lens", "video", "sensor", "zoom", "portrait"],
        "display": ["display", "screen", "oled", "amoled", "brightness", "hz", "resolution", "panel"],
        "performance": ["performance", "speed", "fast", "processor", "lag", "smooth", "chip", "gaming", "ram"],
        "battery": ["battery", "charging", "charge", "drain", "backup", "mah", "charger"],
        "price": ["price", "cost", "expensive", "cheap", "value", "worth", "money", "deal", "pricing"],
        "software": ["software", "ui", "os", "bug", "bugs", "update", "android", "ios", "features"],
        "build quality": ["build", "quality", "material", "design", "durability", "premium", "plastic", "metal", "frame", "hinge"],
        "delivery": ["delivery", "shipping", "courier", "package", "packaging", "arrived"]
    }

    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "best", "nice", "fast", "awesome",
        "fantastic", "perfect", "clear", "crisp", "smooth", "stunning", "vibrant",
        "phenomenal", "solid", "durable", "love", "satisfied", "impressive"
    }

    NEGATIVE_WORDS = {
        "bad", "poor", "worst", "slow", "terrible", "expensive", "problem", "issues",
        "horrible", "disappointing", "weak", "drain", "heat", "overheating", "broken",
        "fused", "scratched", "flimsy", "laggy", "useless", "waste"
    }

    @classmethod
    def analyze_single_review(cls, review_text: str) -> Dict[str, str]:
        """
        Analyzes a single review and returns a dictionary of detected aspects
        with their sentiment (e.g. {"camera": "Positive", "battery": "Negative"}).
        """
        text = review_text.lower()
        aspect_results = {}

        for aspect, keywords in cls.DEFAULT_KEYWORDS.items():
            for kw in keywords:
                match = re.search(r"\b" + re.escape(kw) + r"\b", text)
                if match:
                    # Take context window around the matched keyword
                    start = max(0, match.start() - 45)
                    end = min(len(text), match.end() + 45)
                    context = text[start:end]

                    has_pos = any(re.search(r"\b" + re.escape(p) + r"\b", context) for p in cls.POSITIVE_WORDS)
                    has_neg = any(re.search(r"\b" + re.escape(n) + r"\b", context) for n in cls.NEGATIVE_WORDS)

                    if has_pos and not has_neg:
                        aspect_results[aspect] = "Positive"
                    elif has_neg and not has_pos:
                        aspect_results[aspect] = "Negative"
                    else:
                        aspect_results[aspect] = "Neutral"

                    break  # Found match for this aspect, move to next aspect

        return aspect_results

    @classmethod
    def aggregate_aspects(cls, reviews: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregates aspect ratings across an entire collection of reviews.
        
        Returns:
            Dict mapping aspect name -> {
                "positive": int,
                "negative": int,
                "neutral": int,
                "total_mentions": int,
                "score_percent": int (0-100)
            }
        """
        summary: Dict[str, Dict[str, int]] = {
            aspect: {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
            for aspect in cls.DEFAULT_KEYWORDS
        }

        for item in reviews:
            text = item.get("review_text", "")
            detected = cls.analyze_single_review(text)

            for aspect, sentiment in detected.items():
                summary[aspect]["total"] += 1
                if sentiment == "Positive":
                    summary[aspect]["positive"] += 1
                elif sentiment == "Negative":
                    summary[aspect]["negative"] += 1
                else:
                    summary[aspect]["neutral"] += 1

        # Format percentages and scores
        results = {}
        for aspect, counts in summary.items():
            total = counts["total"]
            if total > 0:
                # Score formula: (pos + 0.5*neutral) / total * 100
                score = round(((counts["positive"] + (0.5 * counts["neutral"])) / total) * 100)
            else:
                # Baseline default if not mentioned
                score = 70

            results[aspect] = {
                "positive": counts["positive"],
                "negative": counts["negative"],
                "neutral": counts["neutral"],
                "total_mentions": total,
                "score_percent": score,
                "status": "Positive" if score >= 65 else ("Negative" if score <= 45 else "Neutral")
            }

        return results
