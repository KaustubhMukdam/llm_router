from typing import Optional

from config import get_config
from classifier.predict import Classifier
from routing.confidence import evaluate_confidence, ConfidenceDecision
from classifier.features import TaskType


def decide_model_tier(
    *,
    features: dict,
    context_token_count: int,
    risk_level: str,
    classifier: Classifier,
) -> Optional[str]:
    """
    Decide model tier using:
    1. Static routing rules (top-down, first match wins)
    2. Classifier + confidence evaluation (if no rule matches)

    Returns:
        "small" | "medium" | "api" | None
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
        if prediction.predicted_task == TaskType.CLASSIFICATION:
            return "small"
        if prediction.predicted_task == TaskType.REASONING:
            return "medium"
        if prediction.predicted_task == TaskType.GENERATION:
            return "api"

        return None

    # ---- 3. Escalation (no fallback yet) ----
    return None
