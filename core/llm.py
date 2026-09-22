"""
Abstract Base LLM Provider Interface.
Allows swapping between different LLMs (Gemini, OpenAI, Anthropic, Local Ollama)
without modifying any agent or analysis logic.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLMProvider(ABC):
    """Abstract class defining the contract for any LLM provider."""

    @abstractmethod
    def generate_text(self, prompt: str) -> Optional[str]:
        """
        Generate raw text response from prompt.
        
        Args:
            prompt: Text prompt to send to the LLM.
            
        Returns:
            Generated response string, or None if failed.
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate structured JSON response from prompt.
        
        Args:
            prompt: Text prompt asking for a JSON response.
            
        Returns:
            Parsed Python dictionary, or None if failed.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is configured and available."""
        pass
