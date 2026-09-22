"""
Sentiment Analyzer Tool.
Performs intelligent sentiment classification.
Leverages fast Scikit-Learn TF-IDF + Classifier for instant batch scoring,
and uses LLM for deep reasoning on sample reviews or single reviews.
"""

import logging
import os
from typing import Dict, Any, Optional
import joblib

import config
from core.llm import BaseLLMProvider
from core import get_llm_provider
from tools.preprocessor import ReviewPreprocessor

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Tool for predicting sentiment with dual-engine (LLM + Offline ML Fallback)."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()
        self._ml_model = None
        self._ml_vectorizer = None
        self._load_fallback_models()

    def _load_fallback_models(self) -> None:
        """Loads offline Scikit-Learn model and vectorizer."""
        try:
            if os.path.exists(config.ML_MODEL_PATH) and os.path.exists(config.VECTORIZER_PATH):
                self._ml_model = joblib.load(config.ML_MODEL_PATH)
                self._ml_vectorizer = joblib.load(config.VECTORIZER_PATH)
                logger.info("[SentimentAnalyzer] Loaded ML model successfully.")
            else:
                logger.warning("[SentimentAnalyzer] Fallback model files not found.")
        except Exception as err:
            logger.error(f"[SentimentAnalyzer] Error loading fallback model: {err}")

    def predict_sentiment_fast(self, review_text: str) -> Dict[str, Any]:
        """Classifies sentiment in microseconds using the local ML pipeline."""
        if not self._ml_model or not self._ml_vectorizer:
            # Fallback simple heuristic
            lower_text = review_text.lower()
            pos = any(w in lower_text for w in ["good", "great", "excellent", "amazing", "love", "best", "perfect"])
            neg = any(w in lower_text for w in ["bad", "poor", "terrible", "worst", "hate", "slow", "drain", "issue"])
            sentiment = "positive" if pos and not neg else ("negative" if neg and not pos else "neutral")
            return {
                "sentiment": sentiment,
                "confidence": 75,
                "explanation": "Classified using text heuristics.",
                "engine": "Heuristic"
            }

        try:
            cleaned = ReviewPreprocessor.clean_text(review_text)
            vector = self._ml_vectorizer.transform([cleaned])
            pred = str(self._ml_model.predict(vector)[0]).strip().lower()

            return {
                "sentiment": pred if pred in ("positive", "neutral", "negative") else "neutral",
                "confidence": 85,
                "explanation": "Classified using trained Machine Learning model (TF-IDF + Classifier).",
                "engine": "Machine Learning Model"
            }
        except Exception as err:
            logger.error(f"[SentimentAnalyzer] Fast prediction failed: {err}")
            return {
                "sentiment": "neutral",
                "confidence": 50,
                "explanation": "Default classification.",
                "engine": "Default"
            }

    def analyze_sentiment(self, review_text: str, use_llm: bool = False) -> Dict[str, Any]:
        """
        Analyzes the sentiment of a single customer review.
        """
        if not review_text or not review_text.strip():
            return {
                "sentiment": "neutral",
                "confidence": 0,
                "explanation": "Empty review.",
                "engine": "None"
            }

        if use_llm and self.llm and self.llm.is_available():
            prompt = f"""You are an expert customer review sentiment analyzer.
Analyze the following customer review and determine its sentiment.

Review:
"{review_text}"

Respond ONLY with a JSON object in this exact schema:
{{
    "sentiment": "positive" or "neutral" or "negative",
    "confidence": <integer 0 to 100>,
    "explanation": "<concise 1-sentence reasoning>"
}}
"""
            result = self.llm.generate_json(prompt)
            if result and "sentiment" in result:
                sentiment = str(result.get("sentiment", "neutral")).strip().lower()
                if sentiment not in ("positive", "neutral", "negative"):
                    sentiment = "neutral"

                confidence = int(result.get("confidence", 85))
                confidence = max(0, min(100, confidence))

                return {
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "explanation": result.get("explanation", "Classified by AI."),
                    "engine": "Gemini AI"
                }

        # Use lightning-fast ML model
        return self.predict_sentiment_fast(review_text)
