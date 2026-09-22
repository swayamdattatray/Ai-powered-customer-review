"""
Google Gemini Implementation of BaseLLMProvider.
Configured with safety limits and fast timeouts.
"""

import json
import logging
import re
from typing import Optional, Dict, Any

from google import genai
from google.genai import types
import config
from core.llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Gemini API Provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL_NAME
        self._client: Optional[genai.Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes the Gemini client if API key is provided."""
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("[GeminiProvider] No valid API key found. AI features running in fallback.")
            self._client = None
            return

        try:
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"[GeminiProvider] Initialized successfully with model: {self.model_name}")
        except Exception as err:
            logger.error(f"[GeminiProvider] Failed to initialize client: {err}")
            self._client = None

    def is_available(self) -> bool:
        """Returns True if Gemini client is ready to receive requests."""
        return self._client is not None

    def generate_text(self, prompt: str) -> Optional[str]:
        """Generate text from Gemini model."""
        if not self.is_available():
            return None

        try:
            # Disable AFC warnings and set tight token limits for rapid dashboard rendering
            config_params = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=600
            )
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config_params
            )
            return response.text.strip() if response and response.text else None
        except Exception as err:
            logger.warning(f"[GeminiProvider] generate_text error (using offline fallback): {err}")
            return None

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate and parse structured JSON from Gemini model."""
        raw_text = self.generate_text(prompt)
        if not raw_text:
            return None

        return self._parse_json_from_markdown(raw_text)

    @staticmethod
    def _parse_json_from_markdown(text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON embedded in potential markdown code blocks."""
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        clean_text = match.group(1) if match else text

        try:
            return json.loads(clean_text.strip())
        except json.JSONDecodeError as err:
            logger.warning(f"[GeminiProvider] Failed to parse JSON response: {err}")
            return None
