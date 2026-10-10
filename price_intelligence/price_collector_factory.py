"""
Factory for instantiating and dispatching platform price collectors.
"""

from typing import Dict, List, Type, Optional
from .base_price_collector import BasePriceCollector
from .amazon_price_collector import AmazonPriceCollector
from .flipkart_price_collector import FlipkartPriceCollector


class PriceCollectorFactory:
    """
    Registry and factory for price collectors.
    To add a new platform (e.g. Croma, Reliance Digital):
      PriceCollectorFactory.register("croma", CromaPriceCollector)
    """

    _registry: Dict[str, Type[BasePriceCollector]] = {
        "amazon": AmazonPriceCollector,
        "flipkart": FlipkartPriceCollector,
    }

    @classmethod
    def register(cls, source_name: str, collector_cls: Type[BasePriceCollector]):
        """Register a new e-commerce price collector."""
        cls._registry[source_name.lower().strip()] = collector_cls

    @classmethod
    def get_collector(cls, source_name: str) -> Optional[BasePriceCollector]:
        """Instantiate a collector by platform name."""
        collector_cls = cls._registry.get(source_name.lower().strip())
        if collector_cls:
            return collector_cls()
        return None

    @classmethod
    def get_all_collectors(cls) -> List[BasePriceCollector]:
        """Instantiate all registered collectors."""
        return [collector_cls() for collector_cls in cls._registry.values()]

    @classmethod
    def list_supported_sources(cls) -> List[str]:
        return [s.capitalize() for s in cls._registry.keys()]
