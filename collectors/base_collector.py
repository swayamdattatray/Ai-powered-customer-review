"""
Base Collector Interface for E-Commerce Review Intelligence.
Defines standard contracts for product extraction, pagination,
metadata normalization, and limitation reporting.
"""

from abc import ABC, abstractmethod
import re
from typing import Dict, Any, List


class BaseCollector(ABC):
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @abstractmethod
    def collect(self, url: str) -> Dict[str, Any]:
        """
        Main collection method.
        Returns standard dictionary with:
        - product_name
        - canonical_url
        - source
        - overall_rating
        - rating_distribution ({5: %, 4: %, 3: %, 2: %, 1: %})
        - reviews_available
        - reviews_collected
        - reviews_analyzed
        - limitation_reason (None or string)
        - reviews (list of review dicts)
        - authenticity_signals
        """
        pass

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def deduplicate_reviews(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes exact duplicate reviews while preserving unique content."""
        seen = set()
        unique = []
        for r in reviews:
            norm = self.normalize_text(r.get("text", "")).lower()
            if len(norm) >= 10 and norm not in seen:
                seen.add(norm)
                unique.append(r)
        return unique
