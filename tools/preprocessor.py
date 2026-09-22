"""
Review Preprocessor Tool.
Cleans raw text, strips noise/URLs/special characters, standardizes formatting,
and handles deduplication of customer reviews.
"""

import hashlib
import re
from typing import List, Dict, Any


class ReviewPreprocessor:
    """Independent tool to sanitize, clean, and deduplicate customer reviews."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans a single review string.
        - Lowercases
        - Removes URLs
        - Removes special symbols while preserving basic words
        - Normalizes whitespace
        """
        if not text:
            return ""

        text = str(text).lower()

        # Remove URLs (http, https, www)
        text = re.sub(r"http\S+|www\S+", "", text)

        # Remove special characters and numbers, keeping letters and spaces
        text = re.sub(r"[^a-z\s]", " ", text)

        # Collapse multiple spaces into single space
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @classmethod
    def preprocess_reviews(cls, raw_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of raw review dictionaries.
        
        Expected item format:
        {
            "review_text": str,
            "product_name": str (optional),
            "rating": int/float (optional),
            "source": str (optional),
            ...
        }
        
        Returns:
            Cleaned and deduplicated list of review dicts with 'cleaned_text' added.
        """
        seen_hashes = set()
        cleaned_list = []

        for item in raw_reviews:
            original_text = item.get("review_text", "")
            if not original_text or not isinstance(original_text, str):
                continue

            cleaned = cls.clean_text(original_text)
            if not cleaned or len(cleaned) < 3:
                # Skip empty or negligible reviews (e.g. single symbols)
                continue

            # Check duplicate hash based on cleaned content
            content_hash = hashlib.md5(cleaned.encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)

            processed_item = dict(item)
            processed_item["cleaned_text"] = cleaned
            cleaned_list.append(processed_item)

        return cleaned_list
