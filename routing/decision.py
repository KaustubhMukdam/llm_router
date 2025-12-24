from typing import Dict, Any
from types import SimpleNamespace

from config import get_config
from classifier.predict import Classifier
from classifier.features import TaskType, estimate_output_tokens


# --------------------------------------------------
# Confidence thresholds (C.1.8)
# --------------------------------------------------
HIGH_CONFIDENCE = 0.70
MEDIUM_CONFIDENCE = 0.45


# --------------------------------------------------
# Fallback policy
# --------------------------------------------------
def apply_fallback(
    *,
    risk_level: str,
    max_latency_ms: int,
) -> str:
    if risk_level == "high":
        return "api"

    if max_latency_ms < 1000:
        return "medium"

    return "api"


# --------------------------------------------------
# Heuristic helpers
# --------------------------------------------------
def context_dominance_ratio(context_tokens: int, total_tokens: int) -> float:
    if total_tokens == 0:
        return 0.0
    return context_tokens / total_tokens


def estimated_generation_weight(prompt: str) -> str:
    p = prompt.lower()

    if any(k in p for k in ["step by step", "in detail", "explain", "derive"]):
        return "heavy"

    if any(k in p for k in ["summarize", "list", "compare"]):
        return "medium"

    return "light"


# --------------------------------------------------
# B.3a — Context-window safety
# --------------------------------------------------
def enforce_context_window_safety(
    *,
    proposed_tier: str,
    features: dict,
    prompt: str,
    context: list[str],
    explanation: Dict[str, Any],
) -> str:
    config = get_config()

    input_tokens = features.get("token_count", 0)
    context_tokens = features.get("context_length", 0)

    estimated_output = estimate_output_tokens(
        prompt=prompt,
        context=context,
        predicted_task=features.get("task", TaskType.GENERATION),
    )

    total_tokens = input_tokens + context_tokens + estimated_output
    max_allowed = config.models.models[proposed_tier].max_context_tokens

    if total_tokens <= max_allowed:
        explanation["context_window"] = {
            "total_tokens": total_tokens,
            "max_allowed": max_allowed,
            "overflow": False,
        }
        return proposed_tier

    explanation["context_window"] = {
        "total_tokens": total_tokens,
        "max_allowed": max_allowed,
        "overflow": True,
        "escalated_from": proposed_tier,
    }

    if proposed_tier == "small":
        return enforce_context_window_safety(
            proposed_tier="medium",
            features=features,
            prompt=prompt,
            context=context,
            explanation=explanation,
        )

    if proposed_tier == "medium":
        return enforce_context_window_safety(
            proposed_tier="api",
            features=features,
            prompt=prompt,
            context=context,
            explanation=explanation,
        )

    explanation["context_window"]["warning"] = "api_context_limit_exceeded"
    return "api"


# --------------------------------------------------
# Main routing decision
# --------------------------------------------------
def decide_model_tier(
    *,
    features: dict,
    prompt: str,
    context: list[str],
    context_token_count: int,
    risk_level: str,
    max_latency_ms: int,
    classifier: Classifier,
) -> tuple[str, Dict[str, Any]]:

    explanation: Dict[str, Any] = {
        "static_rule": None,
        "classifier": None,
        "heuristics": None,
        "fallback": None,
    }

    config = get_config()
    rules = config.routing.rules

    # ---- 1. Static routing rules ----
    for rule in rules:
        matched = True

        for key, expected in rule.condition.items():
            if key == "risk_level" and risk_level != expected:
                matched = False
                break

            if key == "min_context_tokens" and context_token_count < expected:
                matched = False
                break

            if key == "max_tokens":
                token_count = features.get("token_count")
                if token_count is None or token_count > expected:
                    matched = False
                    break

            if key not in {"risk_level", "min_context_tokens", "max_tokens"}:
                if features.get(key) != expected:
                    matched = False
                    break

        if matched:
            explanation["static_rule"] = {
                "rule_name": rule.name,
                "matched_condition": rule.condition,
                "route_to": rule.route_to,
            }

            safe_tier = enforce_context_window_safety(
                proposed_tier=rule.route_to,
                features=features,
                prompt=prompt,
                context=context,
                explanation=explanation,
            )
            return safe_tier, explanation

    # ---- 2. Heuristics ----
    total_tokens = features.get("token_count", 0)
    context_ratio = context_dominance_ratio(context_token_count, total_tokens)
    gen_weight = estimated_generation_weight(prompt)

    explanation["heuristics"] = {
        "context_ratio": round(context_ratio, 2),
        "generation_weight": gen_weight,
    }

    if context_ratio > 0.8:
        explanation["heuristics"]["override"] = "context_too_large"
        return enforce_context_window_safety(
            proposed_tier="api",
            features=features,
            prompt=prompt,
            context=context,
            explanation=explanation,
        ), explanation

    if context_ratio > 0.6 and gen_weight == "heavy":
        explanation["heuristics"]["override"] = "heavy_context_generation"
        return enforce_context_window_safety(
            proposed_tier="medium",
            features=features,
            prompt=prompt,
            context=context,
            explanation=explanation,
        ), explanation

    # ---- 3. Classifier path (C.1.8) ----
    feature_obj = SimpleNamespace(**features)
    setattr(feature_obj, "prompt", prompt)

    prediction = classifier.predict(feature_obj)
    confidence = prediction.confidence
    predicted_task = prediction.predicted_task

    explanation["classifier"] = {
        "predicted_task": predicted_task.value,
        "confidence": round(confidence, 2),
    }

    # High confidence → trust classifier
    if confidence >= HIGH_CONFIDENCE:
        if risk_level == "high":
            tier = "api"
        elif predicted_task == TaskType.CLASSIFICATION:
            tier = "small"
        elif predicted_task == TaskType.REASONING:
            tier = "medium"
        else:
            tier = "small"

    # Medium confidence → medium tier
    elif confidence >= MEDIUM_CONFIDENCE:
        explanation["classifier"]["confidence_band"] = "medium_uncertainty"
        tier = "medium"

    # Low confidence → API
    else:
        explanation["classifier"]["confidence_band"] = "low_uncertainty"
        tier = "api"

    safe_tier = enforce_context_window_safety(
        proposed_tier=tier,
        features=features,
        prompt=prompt,
        context=context,
        explanation=explanation,
    )
    return safe_tier, explanation
