from fastapi import APIRouter

from contracts.request import GenerateRequest
from contracts.response import GenerateResponse, TokenUsage
from classifier.features import extract_features
from routing.decision import decide_model_tier
from classifier.predict import Classifier
from classifier.stub import StubClassifier

router = APIRouter()

# Temporary classifier instance (real model comes later)
_classifier = Classifier(StubClassifier())


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    """
    Routing-only generate endpoint.

    STEP 7 responsibilities:
    - Parse request
    - Extract deterministic features
    - Call routing decision
    - Populate model_used
    """
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

    return GenerateResponse(
        response="",
        model_used=model_tier,
        tokens_used=TokenUsage(
            input=0,
            output=0,
        ),
        estimated_cost_usd=0.0,
        cache_hit=False,
    )
