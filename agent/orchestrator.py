"""
Review Intelligence Agent Orchestrator.
Coordinates the autonomous workflow:
1. Multi-source collection
2. Preprocessing & deduplication
3. Fast ML + LLM sentiment classification
4. Granular aspect discovery and scoring
5. Multi-signal fake review & "Why Flagged?" evidence evaluation
6. Review similarity clustering
7. Quantified recurring complaints & emerging issue trends
8. Executive synthesis and strategic recommendations
"""

from datetime import datetime
import logging
from typing import Dict, Any, Optional, List

from core.llm import BaseLLMProvider
from core import get_llm_provider
from tools.collector import ReviewCollector
from tools.preprocessor import ReviewPreprocessor
from tools.sentiment_analyzer import SentimentAnalyzer
from tools.aspect_analyzer import AspectAnalyzer
from tools.fake_detector import FakeReviewDetector
from tools.clustering import ReviewClusterer
from tools.trend_analyzer import TrendAnalyzer
from tools.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ReviewIntelligenceAgent:
    """
    Autonomous AI Agent for Product Customer Review Intelligence.
    Acts as the main orchestrator coordinating all specialized analysis tools.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()
        
        # Instantiate full tool suite
        self.collector = ReviewCollector()
        self.preprocessor = ReviewPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer(self.llm)
        self.aspect_analyzer = AspectAnalyzer(self.llm)
        self.fake_detector = FakeReviewDetector(self.llm)
        self.clusterer = ReviewClusterer(similarity_threshold=0.65)
        self.trend_analyzer = TrendAnalyzer(self.llm)
        self.report_generator = ReportGenerator(self.llm)

    def analyze_product(
        self,
        product_query: str,
        sources: Optional[List[str]] = None,
        max_reviews: int = 50
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end autonomous analysis workflow for a product or URL.
        """
        product_name = product_query.strip()
        logger.info(f"[ReviewIntelligenceAgent] Starting autonomous investigation for: '{product_name}'")

        # Step 1: Collect Reviews across sources
        raw_collection = self.collector.collect_reviews(product_name, sources=sources, limit=max_reviews)
        raw_reviews = raw_collection.get("reviews", [])
        source_type = raw_collection.get("source_type", "Multi-Source Feed")
        sources_summary = raw_collection.get("sources_summary", {})

        # Step 2: Preprocess, normalize, and deduplicate
        cleaned_reviews = self.preprocessor.preprocess_reviews(raw_reviews)
        total_reviews = len(cleaned_reviews)

        if total_reviews == 0:
            return {
                "product_name": product_name,
                "status": "No Reviews Found",
                "error": "No reviews available for this product query across queried sources."
            }

        all_texts = [r.get("review_text", "") for r in cleaned_reviews]

        # Step 3: Fast batch sentiment classification & deep multi-signal risk analysis
        positive_count = 0
        neutral_count = 0
        negative_count = 0

        analyzed_reviews = []
        for r in cleaned_reviews:
            text = r.get("review_text", "")
            rating = r.get("rating", 4)
            
            # Sentiment prediction
            sent_res = self.sentiment_analyzer.analyze_sentiment(text, use_llm=False)
            s = sent_res.get("sentiment", "neutral")
            if s == "positive":
                positive_count += 1
            elif s == "negative":
                negative_count += 1
            else:
                neutral_count += 1

            # Multi-signal fake detection with "Why Flagged?" evidence
            risk_eval = self.fake_detector.evaluate_review(text, rating, all_texts)

            r_item = dict(r)
            r_item["sentiment"] = s
            r_item["confidence"] = sent_res.get("confidence", 85)
            r_item["is_fake"] = risk_eval.get("is_suspicious", False)
            r_item["fake_score"] = risk_eval.get("suspicion_score", 0)
            r_item["risk_status"] = risk_eval.get("risk_status", "Appears Authentic")
            r_item["why_flagged"] = risk_eval.get("why_flagged", [])
            r_item["fake_reason"] = "; ".join(risk_eval.get("why_flagged", []))
            analyzed_reviews.append(r_item)

        pos_pct = round((positive_count / total_reviews) * 100) if total_reviews > 0 else 0
        neu_pct = round((neutral_count / total_reviews) * 100) if total_reviews > 0 else 0
        neg_pct = round((negative_count / total_reviews) * 100) if total_reviews > 0 else 0

        # Customer Satisfaction Metric
        satisfaction_score = round(((positive_count + (0.4 * neutral_count)) / total_reviews) * 100)
        
        if satisfaction_score >= 70:
            overall_perception = "Generally Positive"
            perception_mood = "positive"
        elif satisfaction_score <= 45:
            overall_perception = "Generally Negative"
            perception_mood = "negative"
        else:
            overall_perception = "Mixed / Neutral"
            perception_mood = "neutral"

        # Step 4: Granular Aspect Discovery & Aspect Sentiment
        aspect_breakdown = self.aspect_analyzer.aggregate_aspects(cleaned_reviews)

        # Step 5: Fake Review Batch Evaluation
        fake_analysis = self.fake_detector.evaluate_batch(cleaned_reviews)

        # Step 6: Review Clustering Analysis
        clusters = self.clusterer.find_clusters(analyzed_reviews)

        # Step 7: Quantified Recurring Complaints & Emerging Issues
        trend_analysis = self.trend_analyzer.analyze_trends(cleaned_reviews, aspect_breakdown)

        # Step 8: Executive Report & Recommendations Generation
        report_data = self.report_generator.generate_report(
            product_name=product_name,
            perception=overall_perception,
            satisfaction=satisfaction_score,
            aspect_data=aspect_breakdown,
            trend_data=trend_analysis,
            fake_data=fake_analysis
        )

        category = raw_reviews[0].get("category", "Electronics & Consumer Goods") if raw_reviews else "Consumer Goods"

        # Review Quality Breakdown
        useful_count = sum(1 for r in analyzed_reviews if not r["is_fake"] and len(r.get("review_text", "").split()) > 5)
        low_info_count = sum(1 for r in analyzed_reviews if len(r.get("review_text", "").split()) <= 5 and not r["is_fake"])
        cluster_dup_count = sum(c["size"] for c in clusters)
        suspicious_count = fake_analysis.get("suspicious_count", 0)

        quality_breakdown = {
            "useful_informative": useful_count,
            "low_information": low_info_count,
            "near_duplicate_cluster": cluster_dup_count,
            "potentially_suspicious": suspicious_count
        }

        # Step 9: Assemble Final Product Intelligence Report
        intelligence_report = {
            "product_name": product_name,
            "category": category,
            "source_type": source_type,
            "sources_summary": sources_summary,
            "analysis_date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "status": "Analysis Completed",
            
            # Key Top Metric Cards
            "overall_perception": overall_perception,
            "perception_mood": perception_mood,
            "customer_satisfaction": satisfaction_score,
            "suspicious_percentage": fake_analysis.get("suspicious_percentage", 0),
            "suspicious_count": suspicious_count,
            "risk_breakdown": fake_analysis.get("risk_breakdown", {}),
            "key_takeaway": report_data.get("key_takeaway", ""),
            
            # Sentiment Distribution
            "total_reviews": total_reviews,
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_count": negative_count,
            "positive_percentage": pos_pct,
            "neutral_percentage": neu_pct,
            "negative_percentage": neg_pct,
            
            # Aspect Breakdown (Granular)
            "aspects": aspect_breakdown,
            
            # Common Topics & Recurring Quantified Complaints
            "most_liked": trend_analysis.get("most_liked", []),
            "most_complained": trend_analysis.get("most_complained", []),
            "recurring_complaints": trend_analysis.get("recurring_complaints", []),
            "emerging_issues": trend_analysis.get("emerging_issues", []),
            
            # Review Clusters
            "clusters": clusters,
            "quality_breakdown": quality_breakdown,
            
            # AI Insights & Actionable Recommendations
            "ai_insights": report_data.get("insights", ""),
            "recommendations": report_data.get("recommendations", []),
            
            # Full Analyzed Reviews
            "reviews": analyzed_reviews
        }

        logger.info(f"[ReviewIntelligenceAgent] Analysis complete for '{product_name}'. Satisfaction: {satisfaction_score}%, Suspicious: {suspicious_count}")
        return intelligence_report
