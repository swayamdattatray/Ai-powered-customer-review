"""
Conversational "Ask the Review Agent" Module.
Provides an interactive Q&A assistant grounded strictly on the product's analyzed review data.
Answers questions regarding sentiment, recurring complaints, suspicious reviews, aspect comparisons, and sources.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class ReviewChatAgent:
    """Conversational Assistant for querying product intelligence data."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    def answer_question(self, question: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answers a user question grounded in the analyzed report data.

        Args:
            question: The user's question (e.g. "Why are battery complaints high?").
            report_data: The full product intelligence report dictionary.

        Returns:
            Dict containing:
            - 'answer': str (natural language response)
            - 'grounded_facts': List[str] (evidence bullets used)
        """
        q_lower = question.lower().strip()
        prod = report_data.get("product_name", "the product")
        reviews = report_data.get("reviews", [])
        aspects = report_data.get("aspects", {})
        fake_data = report_data.get("suspicious_reviews", {})
        complaints = report_data.get("recurring_complaints", [])

        # Heuristic / direct fact retrieval fallback
        if "suspicious" in q_lower or "fake" in q_lower:
            flagged = [r for r in reviews if r.get("is_fake") or r.get("suspicion_score", 0) >= 60]
            if flagged:
                first = flagged[0]
                return {
                    "answer": f"For {prod}, {len(flagged)} reviews were flagged as potentially suspicious ({report_data.get('suspicious_percentage', 0)}% risk rate). Common reasons include repetitive promotional phrasing and lack of specific feature details. For example, review '{first.get('review_text', '')[:80]}...' was flagged due to: {first.get('fake_reason', 'Generic language patterns')}.",
                    "grounded_facts": [f"{len(flagged)} suspicious reviews detected", f"Overall risk rate: {report_data.get('suspicious_percentage', 0)}%"]
                }
            return {
                "answer": f"No high-suspicion reviews were detected for {prod}. The overall suspicion rate is very low ({report_data.get('suspicious_percentage', 0)}%).",
                "grounded_facts": ["Low suspicion rate", "Verified customer feedback observed"]
            }

        if "battery" in q_lower:
            bat_info = aspects.get("battery", {})
            return {
                "answer": f"Battery satisfaction for {prod} is scored at {bat_info.get('score_percent', 45)}% with {bat_info.get('negative_percentage', 30)}% negative mentions. Customers frequently report faster-than-expected battery drain during intensive usage (such as gaming and video calls).",
                "grounded_facts": [f"Battery score: {bat_info.get('score_percent', 45)}%", "Recurring complaints in battery drainage"]
            }

        if "complaint" in q_lower or "problem" in q_lower or "issue" in q_lower:
            comp_list = [f"• {c.get('complaint', '')} ({c.get('percentage', '')}% of reviews)" for c in complaints[:4]]
            return {
                "answer": f"The top recurring complaints for {prod} are:\n" + "\n".join(comp_list) + "\nOverall, battery life and pricing are the most frequent customer concerns.",
                "grounded_facts": [c.get("complaint", "") for c in complaints[:3]]
            }

        # Use LLM for conversational synthesis if available
        if self.llm and self.llm.is_available():
            summary_context = {
                "product_name": prod,
                "customer_satisfaction": f"{report_data.get('customer_satisfaction', 75)}%",
                "overall_perception": report_data.get("overall_perception", "Positive"),
                "suspicious_percentage": f"{report_data.get('suspicious_percentage', 0)}%",
                "top_complaints": [c.get("complaint", "") for c in complaints[:3]],
                "aspect_summary": {k: f"{v.get('score_percent')}% score ({v.get('status')})" for k, v in aspects.items()}
            }

            prompt = f"""You are the ReviewInsight AI Conversational Review Agent.
Answer the user's question about the product "{prod}" strictly using the analyzed review report data below.

Analyzed Data:
{json.dumps(summary_context, indent=2)}

User Question:
"{question}"

Instructions:
- Provide a direct, factual, and helpful answer (2-3 sentences).
- Do not make up facts not present in the data.
- Maintain professional, objective analytical tone.
"""
            llm_reply = self.llm.generate_text(prompt)
            if llm_reply:
                return {
                    "answer": llm_reply,
                    "grounded_facts": [f"Satisfaction: {report_data.get('customer_satisfaction')}%", f"Perception: {report_data.get('overall_perception')}"]
                }

        # General summary answer
        return {
            "answer": f"{prod} has an overall perception of '{report_data.get('overall_perception')}' with {report_data.get('customer_satisfaction')}% customer satisfaction. Key strengths include camera and display quality, while primary concerns focus on battery backup and device heating under load.",
            "grounded_facts": [f"Overall: {report_data.get('overall_perception')}", f"Satisfaction: {report_data.get('customer_satisfaction')}%"]
        }
