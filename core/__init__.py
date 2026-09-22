"""
Core LLM Factory module.
Instantiates the active LLM provider configured in config.py.
"""

from typing import Optional
import config
from core.llm import BaseLLMProvider
from core.gemini_provider import GeminiProvider


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """
    Factory function to get the configured LLM provider instance.
    
    Args:
        provider_type: Optional string ('gemini', 'openai', etc.) 
                       Defaults to config.LLM_PROVIDER.
                       
    Returns:
        An instance of BaseLLMProvider.
    """
    selected = (provider_type or config.LLM_PROVIDER).lower()

    if selected == "gemini":
        return GeminiProvider()
    
    # Easily extendable for future providers (e.g. OpenAIProvider, OllamaProvider)
    # elif selected == "openai":
    #     return OpenAIProvider()

    # Default fallback to Gemini
    return GeminiProvider()
