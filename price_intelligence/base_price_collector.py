"""
Base Collector Interface for E-Commerce Price Intelligence.
"""

from abc import ABC, abstractmethod
import re
from typing import Optional, Any
from .models import PriceResult


class BasePriceCollector(ABC):
    """Abstract base class that all platform price collectors must implement."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_price(
        self,
        product_url: Optional[str] = None,
        product_name: Optional[str] = None
    ) -> PriceResult:
        """
        Fetch current price from the official API.
        Must return a normalized PriceResult.
        """
        pass

    def clean_price_value(self, val: Any) -> Optional[float]:
        """Convert various price representations into a clean positive float."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val) if val > 0 else None
        
        # Clean string like "₹ 79,999.00" or "79999"
        text = str(val).strip()
        cleaned = re.sub(r"[^\d.]", "", text)
        if not cleaned:
            return None
        try:
            res = float(cleaned)
            return res if res > 0 else None
        except (ValueError, TypeError):
            return None

    def assess_product_match(self, target_name: Optional[str], candidate_name: Optional[str]) -> str:
        """
        Assess whether candidate product matches the target product.
        Checks for storage (128GB/256GB/512GB/1TB), RAM (8GB/12GB/16GB), 
        color, and key model tokens.
        
        Returns: 'exact', 'high', 'uncertain', or 'none'
        """
        if not target_name or not candidate_name:
            return "uncertain"

        t_clean = target_name.lower().strip()
        c_clean = candidate_name.lower().strip()

        # If identical
        if t_clean == c_clean:
            return "exact"

        # Check storage configuration mismatch (e.g. 128 GB vs 256 GB)
        storage_pattern = r"\b(\d{1,3})\s*(gb|tb)\b"
        t_storage = set(re.findall(storage_pattern, t_clean))
        c_storage = set(re.findall(storage_pattern, c_clean))
        if t_storage and c_storage and t_storage != c_storage:
            return "uncertain"  # Storage variant mismatch detected!

        # Check generation/model numbers (e.g., iPhone 16 vs iPhone 17)
        model_nums_t = set(re.findall(r"\b\d{1,3}[a-z]?\b", t_clean))
        model_nums_c = set(re.findall(r"\b\d{1,3}[a-z]?\b", c_clean))
        
        # Keyword intersection
        words_t = set(re.findall(r"\b[a-z0-9]{3,}\b", t_clean))
        words_c = set(re.findall(r"\b[a-z0-9]{3,}\b", c_clean))

        if not words_t:
            return "uncertain"

        intersection = words_t.intersection(words_c)
        ratio = len(intersection) / len(words_t)

        if ratio >= 0.8:
            return "exact"
        elif ratio >= 0.6:
            return "high"
        elif ratio >= 0.35:
            return "uncertain"
        else:
            return "none"
