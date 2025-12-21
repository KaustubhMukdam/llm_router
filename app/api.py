from fastapi import APIRouter
import time

from contracts.request import GenerateRequest
from contracts.response import GenerateResponse, TokenUsage
from classifier.features import extract_features
from routing.decision import decide_model_tier
from classifier.predict import Classifier
from classifier.stub import StubClassifier

from inference.small import execute_small
from inference.medium import execute_medium
from inference.api import execute_api

from metrics.prometheus import (
    REQUEST_COUNT,
    ROUTING_DECISIONS,
    INFERENCE_LATENCY,
    TOKEN_USAGE,
    COST_TOTAL,
)

router = APIRouter()

_classifier = Classifier(StubClassifier())


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    features = extract_features(
        prompt=request.prompt,
        context=request.context or [],
        constraints=request.constraints.model_dump(),
    )

    start_time = time.time()

    model_tier = decide_model_tier(
        features=features.model_dump(),
        context_token_count=features.context_length,
        risk_level=request.constraints.risk_level,
        max_latency_ms=request.constraints.max_latency_ms,
        classifier=_classifier,
    )

    # Record routing decision source
    # (best-effort, never break request)
    try:
        if model_tier == "small" or model_tier == "medium":
            ROUTING_DECISIONS.labels(decision_type="static").inc()
        else:
            ROUTING_DECISIONS.labels(decision_type="fallback").inc()
    except Exception:
        pass

    response_text = ""
    input_tokens = 0
    output_tokens = 0
    cost = 0.0

    try:
        if model_tier == "small":
            response_text, input_tokens, output_tokens, cost = execute_small(
                request.prompt, request.context or []
            )

        elif model_tier == "medium":
            response_text, input_tokens, output_tokens, cost = execute_medium(
                request.prompt, request.context or []
            )

        else:
            response_text, input_tokens, output_tokens, cost = execute_api(
                request.prompt, request.context or []
            )

    finally:
        latency = time.time() - start_time

        # Metrics must never fail the request
        try:
            REQUEST_COUNT.labels(model_tier=model_tier).inc()
            INFERENCE_LATENCY.labels(model_tier=model_tier).observe(latency)
            TOKEN_USAGE.labels(model_tier=model_tier, direction="input").inc(input_tokens)
            TOKEN_USAGE.labels(model_tier=model_tier, direction="output").inc(output_tokens)
            COST_TOTAL.labels(model_tier=model_tier).inc(cost)
        except Exception:
            pass

    return GenerateResponse(
        response=response_text,
        model_used=model_tier,
        tokens_used=TokenUsage(input=input_tokens, output=output_tokens),
        estimated_cost_usd=cost,
        cache_hit=False,
    )
