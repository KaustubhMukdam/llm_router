from fastapi import APIRouter
from contracts.request import GenerateRequest
from contracts.response import GenerateResponse, TokenUsage

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
def generate (request: GenerateRequest) -> GenerateResponse:
    """
    Temporary scaffold endpoint.

    Responsibilities (STEP 1 only):
    - Validate request payload via Pydantic contracts
    - Return a dummy response matching the response schema exactly
    """
    return GenerateResponse(
        response="",
        model_used="small",
        tokens_used=TokenUsage(
            input=0,
            output=0,
        ),
        estimated_cost_usd=0.0,
        cache_hit=False,
    )

