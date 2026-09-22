from google import genai
import json
import os
import re

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CONFIGURE GEMINI
# ============================================================

_client = None


def _get_client():
    """
    Initialize and return the Gemini client.
    Returns None if the API key is not set.
    """

    global _client

    if _client is not None:
        return _client

    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        print("[Gemini] No valid API key found. AI features disabled.")
        return None

    try:
        _client = genai.Client(api_key=GEMINI_API_KEY)

        print("[Gemini] Client initialized successfully.")

        return _client

    except Exception as error:
        print(f"[Gemini] Failed to initialize: {error}")
        return None


def _parse_json_response(text):
    """
    Extract and parse JSON from Gemini's response.
    Handles cases where the response includes markdown code blocks.
    """

    # Try to extract JSON from markdown code block
    json_match = re.search(
        r"```(?:json)?\s*\n?(.*?)\n?```",
        text,
        re.DOTALL
    )

    if json_match:
        text = json_match.group(1)

    # Try to parse the text as JSON
    try:
        return json.loads(text.strip())

    except json.JSONDecodeError:
        return None


# ============================================================
# ANALYZE REVIEW WITH AI
# ============================================================

def analyze_review_with_ai(review_text):
    """
    Use Gemini to analyze the sentiment of a customer review.

    Returns a dictionary:
    {
        "sentiment": "positive" | "neutral" | "negative",
        "confidence": 0-100,
        "explanation": "AI reasoning..."
    }

    Returns None if Gemini is not available.
    """

    client = _get_client()

    if client is None:
        return None

    prompt = f"""You are an expert customer review sentiment analyzer.

Analyze the following customer review and determine its sentiment.

Customer Review:
"{review_text}"

Respond ONLY with a valid JSON object in this exact format:
{{
    "sentiment": "positive" or "neutral" or "negative",
    "confidence": <number from 0 to 100>,
    "explanation": "<brief 1-2 sentence explanation of why you classified it this way>"
}}

Rules:
- "sentiment" must be exactly one of: "positive", "neutral", "negative" (lowercase)
- "confidence" must be an integer from 0 to 100
- "explanation" should be concise and insightful
- Consider the overall tone, specific words, and context
- Mixed reviews with both positive and negative aspects should be classified based on the dominant sentiment
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        result = _parse_json_response(
            response.text
        )

        if result and "sentiment" in result:

            # Validate sentiment value
            if result["sentiment"] not in [
                "positive", "neutral", "negative"
            ]:
                result["sentiment"] = "neutral"

            # Validate confidence
            result["confidence"] = max(
                0,
                min(100, int(result.get("confidence", 50)))
            )

            return result

        return None

    except Exception as error:
        print(f"[Gemini] Sentiment analysis error: {error}")
        return None


# ============================================================
# DETECT FAKE REVIEW
# ============================================================

def detect_fake_review(review_text):
    """
    Use Gemini to detect if a customer review is potentially fake.

    Returns a dictionary:
    {
        "is_fake": True | False,
        "fake_score": 0-100 (higher = more likely fake),
        "reasoning": "explanation of red flags or authenticity signals"
    }

    Returns None if Gemini is not available.
    """

    client = _get_client()

    if client is None:
        return None

    prompt = f"""You are an expert at detecting fake customer reviews.

Analyze the following customer review for signs of being fake or inauthentic.

Customer Review:
"{review_text}"

Consider these fake review indicators:
1. Overly generic praise without specific details
2. Unnatural or robotic language patterns
3. Excessive use of superlatives ("best ever", "absolutely perfect")
4. Lack of specific product experience or features mentioned
5. Suspiciously short reviews with extreme ratings
6. Repetitive phrases or patterns common in paid reviews
7. Grammar/spelling patterns typical of mass-produced reviews
8. No mention of actual product usage or experience

Also consider these authenticity signals:
1. Specific details about product features or experience
2. Mention of both pros and cons
3. Personal anecdotes or context
4. Natural conversational tone
5. Specific use cases or scenarios

Respond ONLY with a valid JSON object in this exact format:
{{
    "is_fake": true or false,
    "fake_score": <number from 0 to 100>,
    "reasoning": "<brief 2-3 sentence explanation of why you think it's fake or authentic>"
}}

Rules:
- "is_fake" should be true if fake_score >= 60
- "fake_score" of 0 means definitely authentic, 100 means definitely fake
- Be fair and balanced — not every short review is fake
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        result = _parse_json_response(
            response.text
        )

        if result and "is_fake" in result:

            # Validate fake_score
            result["fake_score"] = max(
                0,
                min(100, int(result.get("fake_score", 0)))
            )

            # Ensure is_fake is consistent with score
            result["is_fake"] = result["fake_score"] >= 60

            return result

        return None

    except Exception as error:
        print(f"[Gemini] Fake detection error: {error}")
        return None


# ============================================================
# GENERATE REVIEW SUMMARY
# ============================================================

def generate_review_summary(reviews_list):
    """
    Use Gemini to generate a natural language summary
    of multiple customer reviews.

    Args:
        reviews_list: list of review text strings

    Returns a dictionary:
    {
        "summary": "natural language summary...",
        "key_strengths": ["strength1", "strength2"],
        "key_weaknesses": ["weakness1", "weakness2"],
        "recommendation": "brief recommendation..."
    }

    Returns None if Gemini is not available.
    """

    client = _get_client()

    if client is None:
        return None

    if not reviews_list:
        return None

    # Limit to 20 reviews to stay within token limits
    reviews_subset = reviews_list[:20]

    reviews_text = ""

    for i, review in enumerate(reviews_subset, 1):
        reviews_text += f"{i}. \"{review}\"\n"

    prompt = f"""You are an expert customer review analyst.

Analyze the following {len(reviews_subset)} customer reviews and provide a comprehensive summary.

Customer Reviews:
{reviews_text}

Respond ONLY with a valid JSON object in this exact format:
{{
    "summary": "<2-3 sentence overall summary of what customers are saying>",
    "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "key_weaknesses": ["<weakness 1>", "<weakness 2>"],
    "recommendation": "<1 sentence recommendation for the product team>"
}}

Rules:
- "summary" should capture the overall customer sentiment and main themes
- "key_strengths" should list 2-4 most mentioned positive aspects
- "key_weaknesses" should list 1-3 most mentioned negative aspects
- "recommendation" should be actionable advice based on the reviews
- If there are no weaknesses found, use an empty list []
- Be concise and insightful
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        result = _parse_json_response(
            response.text
        )

        if result and "summary" in result:
            return result

        return None

    except Exception as error:
        print(f"[Gemini] Summary generation error: {error}")
        return None
