"""
Dataset & Local Database Collector.
Fetches reviews stored in the local SQLite database or uploaded datasets.
"""

import sqlite3
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import config
from collectors.base_collector import BaseReviewCollector

logger = logging.getLogger(__name__)


class DatasetReviewCollector(BaseReviewCollector):
    """Collector for local SQLite database and custom review datasets."""

    def __init__(self, db_path: Optional[str] = None):
        super().__init__(source_name="Local Database / Stored Reviews")
        self.db_path = db_path or config.DATABASE_PATH

    def collect(self, query_or_url: str, limit: int = 50) -> Dict[str, Any]:
        """Queries the SQLite database for existing reviews matching the product query."""
        product_name = query_or_url.strip()
        reviews: List[Dict[str, Any]] = []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, product_name, review_text, rating, sentiment, source, created_at
                FROM reviews
                WHERE LOWER(product_name) LIKE LOWER(?)
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{product_name}%", limit))

            rows = cursor.fetchall()
            for row in rows:
                reviews.append(self.format_review_item(
                    review_id=str(row["id"]),
                    review_text=row["review_text"],
                    rating=row["rating"] or 4,
                    source=row["source"] or "Direct Entry",
                    product_name=row["product_name"] or product_name,
                    timestamp=str(row["created_at"])[:10] if row["created_at"] else "2026-03-01"
                ))
            conn.close()

            status = "AVAILABLE" if reviews else "NO_RECORDS"
            status_msg = f"Retrieved {len(reviews)} reviews from local database." if reviews else "No matching reviews found in database."

        except Exception as err:
            logger.error(f"[DatasetCollector] Error reading database: {err}")
            status = "ERROR"
            status_msg = f"Database read error: {err}"

        return {
            "source": "Local Database",
            "status": status,
            "status_message": status_msg,
            "product_name": product_name,
            "reviews": reviews,
            "reviews_count": len(reviews),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
