from typing import Optional

from config import get_config


def decide_model_tier(
    *,
    features: dict,
    context_token_count: int,
    risk_level: str,
) -> Optional[str]:
    """
    Decide model tier based on static routing rules.

    Rules are evaluated top-down.
    First matching rule wins.
    If no rule matches, return None.
    """
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
                # Feature-based exact match (e.g. task)
                if features.get(key) != expected:
                    matched = False
                    break

        if matched:
            return rule.route_to

    return None
