"""LLM client contract and abstraction for Phase 2 integration."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMClient(ABC):
    """Abstract client interface for interacting with Language Model APIs."""

    @abstractmethod
    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate raw text completion from the language model."""
        pass

    @abstractmethod
    def parse_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate structured JSON output adhering to a schema."""
        pass


class LLMClient(BaseLLMClient):
    """Production LLM client implementation placeholder (Scheduled for Phase 2)."""

    def __init__(self, api_key: str = "", model_name: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError(
            "LLM integration is scheduled for Phase 2. Core foundation and security architecture are active."
        )

    def parse_structured_output(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "Structured LLM parsing is scheduled for Phase 2."
        )
