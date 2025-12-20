"""
Response schema for the LLM routing system.
Defines the output structure returned by the /generate endpoint.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class ModelTier(str, Enum):
    """Enumeration of available model tiers."""
    SMALL = "small"
    MEDIUM = "medium"
    API = "api"


class TokenUsage(BaseModel):
    """Token count breakdown for the request."""
    input: int = Field(default=0, ge=0)
    output: int = Field(default=0, ge=0)


class GenerateResponse(BaseModel):
    """Response payload from the /generate endpoint."""
    response: str
    model_used: Optional[ModelTier]
    tokens_used: TokenUsage = Field(default_factory=TokenUsage)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    cache_hit: bool = Field(default=False)