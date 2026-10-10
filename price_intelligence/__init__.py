"""
Price Intelligence Package
==========================
Modular, credential-gated price comparison across e-commerce platforms.

Supported sources (initial):
  - Amazon  (via Amazon PA-API 5.0 — requires Associates credentials)
  - Flipkart (via Flipkart Affiliate API — requires affiliate token)

Architecture:
  price_service.PriceService
      └── price_collector_factory.PriceCollectorFactory
              ├── amazon_price_collector.AmazonPriceCollector
              └── flipkart_price_collector.FlipkartPriceCollector

Adding a new source later:
  1. Create  price_intelligence/croma_price_collector.py
  2. Register it in  price_collector_factory.py
  3. Done — no other changes needed.
"""

from .models import PriceResult
from .base_price_collector import BasePriceCollector
from .amazon_price_collector import AmazonPriceCollector
from .flipkart_price_collector import FlipkartPriceCollector
from .price_collector_factory import PriceCollectorFactory
from .price_service import PriceService

__all__ = [
    "PriceResult",
    "BasePriceCollector",
    "AmazonPriceCollector",
    "FlipkartPriceCollector",
    "PriceCollectorFactory",
    "PriceService",
]
