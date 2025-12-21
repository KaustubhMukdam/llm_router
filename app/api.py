from fastapi import APIRouter
import time
import hashlib
import json

from contracts.request import GenerateRequest
from contracts.response import GenerateResponse, TokenUsage
from classifier.features import extract_features
from routing.decision import decide_model_tier
from classifier.predict import Classifier
from classifier.stub import StubClassifier

from inference.small import execute_small
from inference.medium import execute_medium
from inference.api import execute_api

from cache.redis import get as cache_get, set as cache_set
from metrics.prometheus import (
    REQUEST_COUNT,
    ROUTING_DECISIONS,
    INFERENCE_LATENCY,
    TOKEN_USAGE,
    COST_TOTAL,
    CACHE_HITS,
    CACHE_MISSES,
)

router = APIRouter()
_classifier = Classifier(StubClassifier())

def normalize_text(text: str) -> str:
    """
    Canonical text normalization for cache keys.
    - lowercase
    - trim
    - collapse whitespace
    """
    return " ".join(text.strip().lower().split())


def _cache_key(model_tier: str, prompt: str, context: list[str]) -> str:
    normalized_prompt = normalize_text(prompt)

    normalized_context = "\n".join(
        normalize_text(c) for c in context
    )

    raw_key = f"{model_tier}:{normalized_prompt}:{normalized_context}"

    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _cache_ttl(model_tier: str) -> int:
    if model_tier == "small":
        return 3600
    if model_tier == "medium":
        return 1800
    return 300  # api


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

    cache_key = _cache_key(model_tier, request.prompt, request.context or [])
    cached = cache_get(cache_key)

    if cached:
        try:
            payload = json.loads(cached)
            CACHE_HITS.labels(model_tier=model_tier).inc()
            REQUEST_COUNT.labels(model_tier=model_tier).inc()

            return GenerateResponse(
                response=payload["response"],
                model_used=model_tier,
                tokens_used=TokenUsage(
                    input=payload["input_tokens"],
                    output=payload["output_tokens"],
                ),
                estimated_cost_usd=payload["cost"],
                cache_hit=True,
            )
        except Exception:
            pass  # fail open

    CACHE_MISSES.labels(model_tier=model_tier).inc()

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

        try:
            REQUEST_COUNT.labels(model_tier=model_tier).inc()
            INFERENCE_LATENCY.labels(model_tier=model_tier).observe(latency)
            TOKEN_USAGE.labels(model_tier=model_tier, direction="input").inc(input_tokens)
            TOKEN_USAGE.labels(model_tier=model_tier, direction="output").inc(output_tokens)
            COST_TOTAL.labels(model_tier=model_tier).inc(cost)
        except Exception:
            pass

    # Cache only successful inference
    try:
        cache_set(
            cache_key,
            json.dumps(
                {
                    "response": response_text,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost,
                }
            ),
            ttl=_cache_ttl(model_tier),
        )
    except Exception:
        pass

    return GenerateResponse(
        response=response_text,
        model_used=model_tier,
        tokens_used=TokenUsage(input=input_tokens, output=output_tokens),
        estimated_cost_usd=cost,
        cache_hit=False,
    )
