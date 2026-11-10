"""Intent parser contract for translating natural language queries to structured operations."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ParsedOperationIntent(BaseModel):
    """Structured representation of a parsed natural-language intent."""

    operation_type: str = Field(..., description="E.g. inventory.read, inventory.update, bills.discount")
    target_resource: str = Field(..., description="E.g. inventory_items, bills, users")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    proposed_changes: Dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = True
    reasoning: Optional[str] = None


class IntentParser:
    """Parser responsible for converting sanitized user prompts into structured operations."""

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    def parse_intent(self, user_query: str) -> ParsedOperationIntent:
        """
        Parse user prompt into a structured operation intent.
        Implementation scheduled for Phase 2.
        """
        raise NotImplementedError(
            "Natural-language intent parsing is scheduled for Phase 2. Foundation architecture is in place."
        )
