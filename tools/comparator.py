"""
Product Comparison Tool.
Compares two products side-by-side across customer satisfaction, sentiment breakdown,
aspect scores, common complaints, and review suspicion rates.
"""

from typing import Dict, Any


class ProductComparator:
    """Tool for comparing two analyzed product intelligence reports side-by-side."""

    @staticmethod
    def compare_reports(report_a: Dict[str, Any], report_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured comparative metrics between Product A and Product B.
        """
        name_a = report_a.get("product_name", "Product A")
        name_b = report_b.get("product_name", "Product B")

        aspects_a = report_a.get("aspects", {})
        aspects_b = report_b.get("aspects", {})

        all_aspects = sorted(list(set(list(aspects_a.keys()) + list(aspects_b.keys()))))
        aspect_comparison = []

        for aspect in all_aspects:
            score_a = aspects_a.get(aspect, {}).get("score_percent", 70)
            score_b = aspects_b.get(aspect, {}).get("score_percent", 70)
            aspect_comparison.append({
                "aspect": aspect.title(),
                "product_a_score": score_a,
                "product_b_score": score_b,
                "difference": score_a - score_b
            })

        return {
            "product_a": {
                "name": name_a,
                "satisfaction": report_a.get("customer_satisfaction", 75),
                "perception": report_a.get("overall_perception", "Positive"),
                "suspicious_pct": report_a.get("suspicious_percentage", 0),
                "total_reviews": report_a.get("total_reviews", 0),
                "top_complaints": [c.get("complaint", "") for c in report_a.get("recurring_complaints", [])[:3]]
            },
            "product_b": {
                "name": name_b,
                "satisfaction": report_b.get("customer_satisfaction", 75),
                "perception": report_b.get("overall_perception", "Positive"),
                "suspicious_pct": report_b.get("suspicious_percentage", 0),
                "total_reviews": report_b.get("total_reviews", 0),
                "top_complaints": [c.get("complaint", "") for c in report_b.get("recurring_complaints", [])[:3]]
            },
            "aspect_comparison": aspect_comparison
        }
