"""
Collectors package initialization.
Exports all review collector implementations and factory aggregator.
"""

from collectors.base_collector import BaseReviewCollector
from collectors.amazon_collector import AmazonReviewCollector
from collectors.flipkart_collector import FlipkartReviewCollector
from collectors.dataset_collector import DatasetReviewCollector

__all__ = [
    "BaseReviewCollector",
    "AmazonReviewCollector",
    "FlipkartReviewCollector",
    "DatasetReviewCollector"
]
