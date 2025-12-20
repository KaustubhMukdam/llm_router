"""
Feature extraction schema for classifier input.
Defines the feature vector structure used by the routing classifier.
"""

from enum import Enum
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Valid task types for classification."""
    CLASSIFICATION = "classification"
    REASONING = "reasoning"
    GENERATION = "generation"


class FeatureVector(BaseModel):
    """
    Feature vector for classifier input.
    
    Represents extracted characteristics of a prompt used to determine
    the appropriate model tier for routing.
    """
    token_count: int = Field(ge=0, description="Total token count of the prompt")
    prompt_length: int = Field(ge=0, description="Character length of the prompt")
    task: TaskType = Field(description="Detected task type")
    constraint_density: float = Field(ge=0.0, le=1.0, description="Density of constraints in prompt")
    context_length: int = Field(ge=0, description="Total context token count")
    risk_flag: bool = Field(description="Whether high-risk indicators are present")