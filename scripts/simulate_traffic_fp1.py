import random
import time
import requests
from collections import Counter

API_URL = "http://localhost:8000/generate"

TOTAL_REQUESTS = 10

# ---- Workload generators ----

def short_classification():
    return {
        "prompt": f"Classify sentiment: I am feeling great today! id={random.randint(1, 100_000)}",
        "context": [],
    }

def short_generation():
    return {
        "prompt": f"Explain neural networks simply. v={random.randint(1, 50_000)}",
        "context": [],
    }

def long_generation():
    return {
        "prompt": f"Explain neural networks step by step with examples and analogies. run={random.randint(1, 100_000)}",
        "context": [],
    }

def large_context_summary():
    base_context = (
        "This is a long meeting transcript discussing product strategy, "
        "engineering constraints, UX tradeoffs, and business priorities.\n"
    )
    repeated_context = base_context * random.randint(20, 40)

    return {
        "prompt": "Summarize the discussion",
        "context": [repeated_context],
    }

# ---- Traffic mix ----

WORKLOADS = [
    (short_classification, 0.30),
    (short_generation, 0.30),
    (long_generation, 0.25),
    (large_context_summary, 0.15),
]

def choose_workload():
    r = random.random()
    cumulative = 0.0
    for fn, weight in WORKLOADS:
        cumulative += weight
        if r <= cumulative:
            return fn
    return WORKLOADS[-1][0]

# ---- Simulation ----

def simulate():
    routing_counts = Counter()
    cache_hits = 0
    cache_misses = 0

    total_latency = 0.0
    max_latency = 0.0

    routed_cost = 0.0
    api_only_cost = 0.0

    for i in range(TOTAL_REQUESTS):
        workload_fn = choose_workload()
        payload = workload_fn()

        request_body = {
            "prompt": payload["prompt"],
            "context": payload["context"],
            "constraints": {
                "max_latency_ms": 2000,
                "max_cost_usd": 0.01,
                "risk_level": "low",
            },
        }

        start = time.time()
        resp = requests.post(API_URL, json=request_body)
        latency = time.time() - start

        data = resp.json()

        model = data.get("model_used", "unknown")
        routing_counts[model] += 1

        if data.get("cache_hit"):
            cache_hits += 1
        else:
            cache_misses += 1

        total_latency += latency
        max_latency = max(max_latency, latency)

        routed_cost += data.get("estimated_cost_usd", 0.0)

        # ---- Shadow API-only cost estimate ----
        tokens = data.get("tokens_used", {})
        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        # conservative API pricing assumption
        api_only_cost += (input_tokens + output_tokens) * 0.000002

        # Optional: slow down a bit to avoid hammering Ollama
        time.sleep(0.01)

    # ---- Report ----

    print("\n=== Traffic Simulation Results ===")
    print(f"Total requests: {TOTAL_REQUESTS}\n")

    print("Routing distribution:")
    for tier, count in routing_counts.items():
        pct = (count / TOTAL_REQUESTS) * 100
        print(f"  {tier:>6}: {count} ({pct:.1f}%)")

    print("\nCache:")
    hit_pct = (cache_hits / TOTAL_REQUESTS) * 100
    print(f"  Hits:   {cache_hits} ({hit_pct:.1f}%)")
    print(f"  Misses: {cache_misses}")

    print("\nCost:")
    print(f"  Routed total cost: ${routed_cost:.4f}")
    print(f"  API-only estimate: ${api_only_cost:.4f}")
    if api_only_cost > 0:
        saved_pct = (1 - routed_cost / api_only_cost) * 100
        print(f"  Cost saved: {saved_pct:.1f}%")

    print("\nLatency:")
    print(f"  Avg latency: {total_latency / TOTAL_REQUESTS:.2f}s")
    print(f"  Max latency: {max_latency:.2f}s")


if __name__ == "__main__":
    simulate()
