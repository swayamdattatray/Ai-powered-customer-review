"""
Review Collector Tool.
Coordinates multi-source review collectors (Amazon, Flipkart, Local DB, Datasets),
aggregates collected reviews, and reports detailed source metadata.
"""

import logging
from typing import Dict, Any, List, Optional
import config
from collectors.amazon_collector import AmazonReviewCollector
from collectors.flipkart_collector import FlipkartReviewCollector
from collectors.dataset_collector import DatasetReviewCollector

logger = logging.getLogger(__name__)


class ReviewCollector:
    """Orchestrates multi-source review collection across various platforms."""

    def __init__(self):
        self.amazon_collector = AmazonReviewCollector()
        self.flipkart_collector = FlipkartReviewCollector()
        self.dataset_collector = DatasetReviewCollector()

    def collect_reviews(
        self,
        product_identifier: str,
        sources: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Gathers customer reviews from multiple sources.

        Args:
            product_identifier: Product name (e.g. 'iPhone 18 Pro Max') or URL.
            sources: List of target sources ['amazon', 'flipkart', 'database'] or None for auto.
            limit: Total review limit.

        Returns:
            Dict containing aggregated reviews and per-source status.
        """
        query = product_identifier.strip()
        all_reviews: List[Dict[str, Any]] = []
        sources_summary: Dict[str, Any] = {}

        # 1. Query Local Database first
        db_res = self.dataset_collector.collect(query, limit=limit)
        if db_res["reviews_count"] > 0:
            all_reviews.extend(db_res["reviews"])
            sources_summary["Local Database"] = {
                "status": "AVAILABLE",
                "count": db_res["reviews_count"],
                "message": "Retrieved stored reviews from database."
            }

        # 2. Collect Amazon reviews
        if not sources or "amazon" in [s.lower() for s in sources] or "auto" in [s.lower() for s in (sources or [])]:
            amz_res = self.amazon_collector.collect(query, limit=limit)
            all_reviews.extend(amz_res["reviews"])
            sources_summary["Amazon"] = {
                "status": amz_res["status"],
                "count": amz_res["reviews_count"],
                "message": amz_res["status_message"]
            }

        # 3. Collect Flipkart reviews
        if not sources or "flipkart" in [s.lower() for s in sources] or "auto" in [s.lower() for s in (sources or [])]:
            flp_res = self.flipkart_collector.collect(query, limit=limit)
            all_reviews.extend(flp_res["reviews"])
            sources_summary["Flipkart"] = {
                "status": flp_res["status"],
                "count": flp_res["reviews_count"],
                "message": flp_res["status_message"]
            }

        # Deduplicate by review ID or content
        seen_texts = set()
        unique_reviews = []
        for r in all_reviews:
            t = r.get("review_text", "").strip().lower()
            if t not in seen_texts:
                seen_texts.add(t)
                unique_reviews.append(r)

        final_reviews = unique_reviews[:limit]
        source_labels = [k for k, v in sources_summary.items() if v["count"] > 0]
        source_display = ", ".join(source_labels) if source_labels else "Multi-Source Feed"

        return {
            "product_name": query,
            "source_type": source_display,
            "sources_summary": sources_summary,
            "reviews_count": len(final_reviews),
            "reviews": final_reviews
        }
