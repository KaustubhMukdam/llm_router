from typing import Optional

from config import get_config
from classifier.predict import Classifier
from routing.confidence import evaluate_confidence, ConfidenceDecision
from classifier.features import TaskType


def apply_fallback(
    *,
    risk_level: str,
    max_latency_ms: int,
) -> str:
    """
    Deterministic fallback policy.
    """
    if risk_level == "high":
        return "api"

    if max_latency_ms < 1000:
        return "medium"

    return "api"


def decide_model_tier(
    *,
    features: dict,
    context_token_count: int,
    risk_level: str,
    max_latency_ms: int,
    classifier: Classifier,
) -> Optional[str]:
    """
    Decide model tier using:
    1. Static routing rules
    2. Classifier + confidence
    3. Explicit fallback (if still undecided)
    """
    # ---- 1. Static routing rules ----
    config = get_config()
    rules = config.routing.rules

    for rule in rules:
        matched = True

        for key, expected in rule.condition.items():

            if key == "risk_level":
                if risk_level != expected:
                    matched = False
                    break

            elif key == "min_context_tokens":
                if context_token_count < expected:
                    matched = False
                    break

            elif key == "max_tokens":
                token_count = features.get("token_count")
                if token_count is None or token_count > expected:
                    matched = False
                    break

            else:
                if features.get(key) != expected:
                    matched = False
                    break

        if matched:
            return rule.route_to

    # ---- 2. Classifier path ----
    prediction = classifier.predict(features)
    confidence_decision = evaluate_confidence(prediction)

    if confidence_decision == ConfidenceDecision.ACCEPT:
        # High-risk is never allowed locally
        if risk_level == "high":
            return "api"

        if prediction.predicted_task == TaskType.CLASSIFICATION:
            return "small"

        if prediction.predicted_task == TaskType.REASONING:
            return "medium"

        if prediction.predicted_task == TaskType.GENERATION:
            # Allow local generation when safe
            if context_token_count <= config.routing.thresholds.small_max_tokens:
                return "small"
            return "medium"

    # ---- 3. Fallback ----
    return apply_fallback(
        risk_level=risk_level,
        max_latency_ms=max_latency_ms,
    )
