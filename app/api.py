from fastapi import APIRouter

from contracts.request import GenerateRequest
from contracts.response import GenerateResponse, TokenUsage
from classifier.features import extract_features
from routing.decision import decide_model_tier
from classifier.predict import Classifier
from classifier.stub import StubClassifier

from inference.small import execute_small
from inference.medium import execute_medium
from inference.api import execute_api

router = APIRouter()

# Temporary classifier instance (real model comes later)
_classifier = Classifier(StubClassifier())


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    features = extract_features(
        prompt=request.prompt,
        context=request.context or [],
        constraints=request.constraints.model_dump(),
    )

    model_tier = decide_model_tier(
        features=features.model_dump(),
        context_token_count=features.context_length,
        risk_level=request.constraints.risk_level,
        classifier=_classifier,
    )

    # Default empty response (no routing decision)
    response_text = ""

    if model_tier == "small":
        response_text, _, _, _ = execute_small(request.prompt, request.context or [])

    elif model_tier == "medium":
        response_text, _, _, _ = execute_medium(request.prompt, request.context or [])

    elif model_tier == "api":
        response_text, _, _, _ = execute_api(request.prompt, request.context or [])

    return GenerateResponse(
        response=response_text,
        model_used=model_tier,
        tokens_used=TokenUsage(input=0, output=0),
        estimated_cost_usd=0.0,
        cache_hit=False,
    )
