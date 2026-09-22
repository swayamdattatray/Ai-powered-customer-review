"""
Report Generator Tool.
Synthesizes all aggregated tool outputs (sentiment counts, aspects, suspicion risk, trends)
into an authoritative, natural-language executive summary and prioritized strategic recommendations.
"""

import logging
from typing import Dict, Any, Optional
from core.llm import BaseLLMProvider
from core import get_llm_provider

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Tool for creating high-level insights, key takeaways, and recommendations."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    @staticmethod
    def _heuristic_summary_and_recommendations(
        product_name: str,
        perception: str,
        satisfaction: int,
        strengths: list,
        concerns: list
    ) -> Dict[str, Any]:
        """Generates structured natural-language insights using template logic."""
        top_str = ", ".join(strengths[:2]) if strengths else "overall performance"
        top_con = ", ".join(concerns[:2]) if concerns else "minor trade-offs"

        insights = (
            f"{product_name} receives a {perception.lower()} response from customers, with a customer "
            f"satisfaction score of {satisfaction}%. Customers consistently praise {top_str}. "
            f"However, key concerns revolve around {top_con}. Overall, the product is well regarded "
            f"in its category, but targeted refinements in customer pain points would significantly improve retention."
        )

        takeaway = f"Strong customer satisfaction in {top_str}, but {top_con} require attention."

        recommendations = [
            f"Focus on addressing recurring complaints in {concerns[0] if concerns else 'battery/heating'}.",
            f"Highlight verified strengths in {strengths[0] if strengths else 'camera/display'} across marketing channels.",
            "Monitor customer feedback on recent software and quality updates.",
            "Consider competitive pricing or value-bundle promotions.",
            "Maintain proactive customer support for delivery and warranty inquiries."
        ]

        return {
            "insights": insights,
            "key_takeaway": takeaway,
            "recommendations": recommendations
        }

    def generate_report(
        self,
        product_name: str,
        perception: str,
        satisfaction: int,
        aspect_data: Dict[str, Any],
        trend_data: Dict[str, Any],
        fake_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes all analytics data into executive takeaways, detailed insights, and recommendations.
        
        Returns:
            Dict containing:
            - 'insights': str
            - 'key_takeaway': str
            - 'recommendations': List[str]
        """
        liked = trend_data.get("most_liked", [])
        complaints = trend_data.get("most_complained", [])

        if self.llm and self.llm.is_available():
            prompt = f"""You are an executive product intelligence agent.
Review the following aggregated analytical metrics for the product "{product_name}" and generate a comprehensive executive analysis.

Data Summary:
- Product: {product_name}
- Overall Customer Perception: {perception}
- Customer Satisfaction: {satisfaction}%
- Suspicious Reviews: {fake_data.get('suspicious_percentage', 0)}%
- Key Customer Likes: {', '.join(liked)}
- Key Customer Complaints: {', '.join(complaints)}

Respond ONLY with a JSON object in this exact schema:
{{
    "key_takeaway": "<One punchy, impactful takeaway sentence highlighting the core pro and con>",
    "insights": "<A detailed 3-4 sentence paragraph summarizing customer consensus, recurring problems, and nuances>",
    "recommendations": [
        "<Actionable recommendation 1>",
        "<Actionable recommendation 2>",
        "<Actionable recommendation 3>",
        "<Actionable recommendation 4>",
        "<Actionable recommendation 5>"
    ]
}}
"""
            result = self.llm.generate_json(prompt)
            if result and "insights" in result and "recommendations" in result:
                recs = result.get("recommendations", [])
                return {
                    "insights": result.get("insights", ""),
                    "key_takeaway": result.get("key_takeaway", f"{product_name} demonstrates strong customer interest."),
                    "recommendations": recs if isinstance(recs, list) else []
                }

        # Use heuristic generation if LLM is unavailable
        return self._heuristic_summary_and_recommendations(
            product_name, perception, satisfaction, liked, complaints
        )
