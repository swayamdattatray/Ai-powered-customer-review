"""
Centralized AI Prompt Templates.
All prompts used across the Agent, sentiment analysis, fake review detection,
trend extraction, and report generation are organized here for easy modification.
"""

# Prompt for single review sentiment classification
SENTIMENT_ANALYSIS_PROMPT = """You are an expert customer review sentiment analyzer.
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

# Prompt for single review authenticity and suspicion evaluation
FAKE_DETECTION_PROMPT = """You are an expert in customer review authenticity and fraud detection.
Evaluate the following review for potential suspicious or inauthentic patterns.

Review:
"{review_text}"

Respond ONLY with a JSON object in this exact schema:
{{
    "is_suspicious": true or false,
    "suspicion_score": <integer from 0 to 100>,
    "reasoning": "<concise 1-2 sentence explanation evaluating specific details vs generic hype>"
}}
"""

# Prompt for extracting recurring trends, top likes, and complaints
TREND_EXTRACTION_PROMPT = """You are a product intelligence analyst.
Analyze these customer reviews and identify the top recurring positive patterns and customer complaints.

Customer Reviews:
{reviews_text}

Respond ONLY with a JSON object in this exact schema:
{{
    "most_liked": ["<specific positive theme 1>", "<specific positive theme 2>", "<specific positive theme 3>", "<specific positive theme 4>"],
    "most_complained": ["<specific complaint 1>", "<specific complaint 2>", "<specific complaint 3>", "<specific complaint 4>"]
}}
"""

# Prompt for generating executive summary and strategic recommendations
EXECUTIVE_REPORT_PROMPT = """You are an executive product intelligence agent.
Review the following aggregated analytical metrics for the product "{product_name}" and generate a comprehensive executive analysis.

Data Summary:
- Product: {product_name}
- Overall Customer Perception: {perception}
- Customer Satisfaction: {satisfaction}%
- Suspicious Reviews: {suspicious_pct}%
- Key Customer Likes: {liked_str}
- Key Customer Complaints: {complaints_str}

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
