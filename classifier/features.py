"""
Feature extraction schema for classifier input.
Defines the feature vector structure used by the routing classifier.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List
import re


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

def simple_token_count(text: str) -> int:
    """
    Deterministic token approximation based on whitespace splitting.
    """
    if not text:
        return 0
    return len(text.split())


def detect_task_type(prompt: str) -> TaskType:
    """
    Detect task type using simple keyword heuristics.
    """
    lower = prompt.lower()

    if any(k in lower for k in ["classify", "label", "tag", "categorize"]):
        return TaskType.CLASSIFICATION

    if any(k in lower for k in ["why", "how", "explain", "reason"]):
        return TaskType.REASONING

    return TaskType.GENERATION


def extract_features(
    *,
    prompt: str,
    context: List[str],
    constraints: dict,
) -> FeatureVector:
    """
    Build a deterministic FeatureVector from request input.
    """
    context_text = " ".join(context) if context else ""
    full_text = f"{prompt} {context_text}".strip()

    token_count = simple_token_count(full_text)
    context_tokens = simple_token_count(context_text)

    constraint_density = min(len(constraints.keys()) / max(len(prompt), 1), 1.0)

    risk_flag = constraints.get("risk_level") == "high"

    return FeatureVector(
        token_count=token_count,
        prompt_length=len(prompt),
        task=detect_task_type(prompt),
        constraint_density=constraint_density,
        context_length=context_tokens,
        risk_flag=risk_flag,
    )

def estimate_output_tokens(
    prompt: str,
    context: list[str],
    predicted_task: TaskType,
) -> int:
    """
    Rough output token estimator.
    Conservative on purpose.
    """

    base = 50  # minimum answer size

    # Prompt length heuristic
    prompt_tokens = len(prompt.split())
    base += prompt_tokens * 1.2

    # Context influence
    context_tokens = sum(len(c.split()) for c in context)
    base += context_tokens * 0.5

    # Task-based scaling
    if predicted_task == TaskType.CLASSIFICATION:
        return int(min(base, 100))

    if predicted_task == TaskType.REASONING:
        return int(base * 2)

    if predicted_task == TaskType.GENERATION:
        keywords = ["explain", "step by step", "detailed", "derive", "how"]
        if any(k in prompt.lower() for k in keywords):
            return int(base * 4)
        return int(base * 2)

    return int(base)
