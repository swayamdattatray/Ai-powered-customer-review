"""
Collector Factory to instantiate and dispatch platform-specific review collectors.
"""

from urllib.parse import urlparse
from typing import Optional

from .base_collector import BaseCollector
from .amazon_collector import AmazonCollector
from .flipkart_collector import FlipkartCollector


class CollectorFactory:
    @staticmethod
    def get_collector(url: str) -> BaseCollector:
        domain = urlparse(url).netloc.lower()
        
        if any(k in domain for k in ["amazon", "amzn"]):
            return AmazonCollector(max_pages=8)
        elif any(k in domain for k in ["flipkart", "fkrt"]):
            return FlipkartCollector(max_pages=8)
        else:
            # Default to generic Amazon-like collector with standard web parsing
            return AmazonCollector(max_pages=3)
