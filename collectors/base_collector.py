"""
Base Review Collector Interface.
Defines the standard schema, source status, and extraction contracts for all review collectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseReviewCollector(ABC):
    """
    Abstract base class for all source-specific review collectors
    (e.g., Amazon, Flipkart, Local Database, Reddit, Uploaded Datasets).
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    def collect(self, query_or_url: str, limit: int = 50) -> Dict[str, Any]:
        """
        Collects customer reviews for a given product query or URL.

        Args:
            query_or_url: Product name or direct e-commerce product URL.
            limit: Maximum number of reviews to retrieve.

        Returns:
            Dict matching the standard collection contract:
            {
                "source": str,
                "status": "AVAILABLE" | "SIMULATED_DEMO" | "LIMITATION_RESTRICTED" | "ERROR",
                "status_message": str,
                "product_name": str,
                "reviews": List[Dict],
                "reviews_count": int,
                "timestamp": str
            }
        """
        pass

    @staticmethod
    def format_review_item(
        review_id: str,
        review_text: str,
        rating: Optional[int] = None,
        source: str = "Unknown",
        product_name: str = "",
        timestamp: Optional[str] = None,
        author: str = "Anonymous Customer",
        verified_purchase: bool = True
    ) -> Dict[str, Any]:
        """Creates a standardized review dictionary item."""
        return {
            "id": str(review_id),
            "product_name": product_name,
            "review_text": str(review_text).strip(),
            "rating": rating if rating is not None else 4,
            "source": source,
            "author": author,
            "verified_purchase": verified_purchase,
            "timestamp": timestamp or datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        }
