"""
Request schema for the LLM routing system.
Defines the incoming payload structure for the /generate endpoint.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class RiskLevel(str, Enum):
    """Risk level enumeration for routing decisions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Constraints(BaseModel):
    """Optional constraints for routing and inference."""
    max_latency_ms: int = Field(default=2000, ge=0)
    max_cost_usd: float = Field(default=0.01, ge=0.0)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)


class GenerateRequest(BaseModel):
    """Request payload for the /generate endpoint."""
    prompt: str = Field(..., min_length=1)
    context: list[str] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    debug: bool = False