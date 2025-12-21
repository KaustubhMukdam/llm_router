from prometheus_client import Counter, Histogram

# ---- Request & Routing Metrics ----

REQUEST_COUNT = Counter(
    "llm_router_requests_total",
    "Total number of requests per model tier",
    ["model_tier"],
)

ROUTING_DECISIONS = Counter(
    "llm_router_routing_decisions_total",
    "Routing decision counts",
    ["decision_type"],  # static | classifier | fallback
)

# ---- Inference Metrics ----

INFERENCE_LATENCY = Histogram(
    "llm_router_inference_latency_seconds",
    "Inference latency per model tier",
    ["model_tier"],
)

TOKEN_USAGE = Counter(
    "llm_router_tokens_total",
    "Token usage per model tier",
    ["model_tier", "direction"],  # input | output
)

COST_TOTAL = Counter(
    "llm_router_cost_usd_total",
    "Total estimated cost in USD per model tier",
    ["model_tier"],
)
