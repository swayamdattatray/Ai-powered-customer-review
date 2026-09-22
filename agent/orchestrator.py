"""
Review Intelligence Agent Orchestrator.
Coordinates the autonomous workflow of understanding requests, collecting reviews,
running preprocessing, executing sentiment, aspect, fake detection, and trend tools,
and generating a comprehensive product intelligence report.
"""

from datetime import datetime
import logging
from typing import Dict, Any, Optional

from core.llm import BaseLLMProvider
from core import get_llm_provider
from tools.collector import ReviewCollector
from tools.preprocessor import ReviewPreprocessor
from tools.sentiment_analyzer import SentimentAnalyzer
from tools.aspect_analyzer import AspectAnalyzer
from tools.fake_detector import FakeReviewDetector
from tools.trend_analyzer import TrendAnalyzer
from tools.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ReviewIntelligenceAgent:
    """
    Autonomous AI Agent for Product Customer Review Intelligence.
    Acts as the main orchestrator directing specialized tools.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()
        
        # Instantiate tool suite
        self.collector = ReviewCollector()
        self.preprocessor = ReviewPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer(self.llm)
        self.aspect_analyzer = AspectAnalyzer()
        self.fake_detector = FakeReviewDetector(self.llm)
        self.trend_analyzer = TrendAnalyzer(self.llm)
        self.report_generator = ReportGenerator(self.llm)

    def analyze_product(self, product_query: str, max_reviews: int = 50) -> Dict[str, Any]:
        """
        Executes the end-to-end product analysis workflow.
        
        Steps:
        1. Collect available reviews for the product
        2. Clean, filter, and deduplicate reviews
        3. Analyze sentiment across reviews & compute distribution
        4. Extract product aspects and aspect-level scores
        5. Evaluate review authenticity and suspicious patterns
        6. Identify recurring complaints & top positive themes
        7. Synthesize findings into executive insights and recommendations
        8. Return structured product intelligence report
        """
        product_name = product_query.strip()
        logger.info(f"[ReviewIntelligenceAgent] Starting autonomous analysis for product: '{product_name}'")

        # Step 1: Collect Reviews
        raw_collection = self.collector.collect_reviews(product_name, limit=max_reviews)
        raw_reviews = raw_collection.get("reviews", [])
        source_type = raw_collection.get("source_type", "Multi-Source")

        # Step 2: Preprocess & Deduplicate
        cleaned_reviews = self.preprocessor.preprocess_reviews(raw_reviews)
        total_reviews = len(cleaned_reviews)

        if total_reviews == 0:
            return {
                "product_name": product_name,
                "status": "No Reviews Found",
                "error": "No reviews available for this product query."
            }

        # Step 3: Sentiment Analysis & Aggregate Counts
        positive_count = 0
        neutral_count = 0
        negative_count = 0

        analyzed_reviews = []
        for r in cleaned_reviews:
            text = r.get("review_text", "")
            sent_res = self.sentiment_analyzer.analyze_sentiment(text)
            
            s = sent_res.get("sentiment", "neutral")
            if s == "positive":
                positive_count += 1
            elif s == "negative":
                negative_count += 1
            else:
                neutral_count += 1

            r_copy = dict(r)
            r_copy["sentiment"] = s
            r_copy["confidence"] = sent_res.get("confidence", 75)
            r_copy["explanation"] = sent_res.get("explanation", "")
            analyzed_reviews.append(r_copy)

        pos_pct = round((positive_count / total_reviews) * 100) if total_reviews > 0 else 0
        neu_pct = round((neutral_count / total_reviews) * 100) if total_reviews > 0 else 0
        neg_pct = round((negative_count / total_reviews) * 100) if total_reviews > 0 else 0

        # Customer Satisfaction Metric
        satisfaction_score = round(((positive_count + (0.4 * neutral_count)) / total_reviews) * 100)
        
        # Overall Perception Classification
        if satisfaction_score >= 70:
            overall_perception = "Generally Positive"
            perception_mood = "positive"
        elif satisfaction_score <= 45:
            overall_perception = "Generally Negative"
            perception_mood = "negative"
        else:
            overall_perception = "Mixed / Neutral"
            perception_mood = "neutral"

        # Step 4: Aspect Analysis
        aspect_breakdown = self.aspect_analyzer.aggregate_aspects(cleaned_reviews)

        # Step 5: Fake & Suspicious Review Analysis
        fake_analysis = self.fake_detector.evaluate_batch(cleaned_reviews)

        # Step 6: Trend & Pattern Extraction
        trend_analysis = self.trend_analyzer.analyze_trends(cleaned_reviews, aspect_breakdown)

        # Step 7: Executive Report & Recommendations Generation
        report_data = self.report_generator.generate_report(
            product_name=product_name,
            perception=overall_perception,
            satisfaction=satisfaction_score,
            aspect_data=aspect_breakdown,
            trend_data=trend_analysis,
            fake_data=fake_analysis
        )

        # Extract Category
        category = raw_reviews[0].get("category", "Electronics & Consumer Goods") if raw_reviews else "Consumer Goods"

        # Step 8: Build Final Intelligence Report Payload
        intelligence_report = {
            "product_name": product_name,
            "category": category,
            "source_type": source_type,
            "analysis_date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "status": "Analysis Completed",
            
            # Key Top Metric Cards
            "overall_perception": overall_perception,
            "perception_mood": perception_mood,
            "customer_satisfaction": satisfaction_score,
            "suspicious_percentage": fake_analysis.get("suspicious_percentage", 0),
            "suspicious_count": fake_analysis.get("suspicious_count", 0),
            "key_takeaway": report_data.get("key_takeaway", ""),
            
            # Sentiment Distribution
            "total_reviews": total_reviews,
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_count": negative_count,
            "positive_percentage": pos_pct,
            "neutral_percentage": neu_pct,
            "negative_percentage": neg_pct,
            
            # Aspect Breakdown
            "aspects": aspect_breakdown,
            
            # Common Topics & Patterns
            "most_liked": trend_analysis.get("most_liked", []),
            "most_complained": trend_analysis.get("most_complained", []),
            
            # AI Insights & Actionable Recommendations
            "ai_insights": report_data.get("insights", ""),
            "recommendations": report_data.get("recommendations", []),
            
            # Raw Analyzed Reviews Collection
            "reviews": analyzed_reviews
        }

        logger.info(f"[ReviewIntelligenceAgent] Analysis complete for '{product_name}'. Satisfaction: {satisfaction_score}%")
        return intelligence_report
