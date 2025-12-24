import random
import time
import requests
from collections import defaultdict

API_URL = "http://localhost:8000/generate"

TOTAL_REQUESTS = 30
TIMEOUT = 300  # long local model safety

# -------------------------------
# Prompt pools (balanced on purpose)
# -------------------------------

SMALL_PROMPTS = [
    "Explain neural networks simply",
    "What is backpropagation?",
    "Summarize this paragraph",
]

MEDIUM_PROMPTS = [
    "Explain backpropagation step by step",
    "Compare neural networks and decision trees",
    "Analyze tradeoffs between offline-first and real-time sync",
    "Explain how gradient descent works with intuition",
]

API_PROMPTS = [
    "Provide a deep technical review of offline sync architectures with risks",
    "Analyze product, engineering, and marketing alignment issues in detail",
]

SMALL_CONTEXT = []

MEDIUM_CONTEXT = [
    "Technical design notes discussing architecture constraints, "
    "performance considerations, and tradeoffs." * 6
]

LONG_CONTEXT = [
    "Large meeting transcript about product strategy, engineering constraints, "
    "design tradeoffs, security reviews, and marketing timelines. " * 25
]

# -------------------------------
# Deterministic distribution
# -------------------------------

def pick_prompt(i: int):
    """
    Force a realistic routing mix:
    - 40% small
    - 35% medium
    - 25% api
    """
    r = i / TOTAL_REQUESTS

    if r < 0.40:
        return random.choice(SMALL_PROMPTS), SMALL_CONTEXT
    elif r < 0.75:
        return random.choice(MEDIUM_PROMPTS), MEDIUM_CONTEXT
    else:
        return random.choice(API_PROMPTS), LONG_CONTEXT


def simulate():
    stats = {
        "routing": defaultdict(int),
        "cache_hits": 0,
        "cache_misses": 0,
        "latencies_cached": [],
        "latencies_uncached": [],
        "cost_total": 0.0,
        "api_only_cost": 0.0,
    }

    for i in range(TOTAL_REQUESTS):
        prompt, context = pick_prompt(i)

        payload = {
            "prompt": prompt,
            "context": context,
            "constraints": {
                "max_latency_ms": 2000,
                "max_cost_usd": 0.02,
                "risk_level": "low",
            },
            "debug": False,
        }

        start = time.time()
        resp = requests.post(API_URL, json=payload, timeout=TIMEOUT)
        elapsed = time.time() - start

        if resp.status_code != 200:
            print(f"[{i+1:02d}] FAILED")
            continue

        data = resp.json()

        tier = data["model_used"]
        cache_hit = data["cache_hit"]
        cost = data["estimated_cost_usd"]

        stats["routing"][tier] += 1
        stats["cost_total"] += cost
        stats["api_only_cost"] += 0.02  # fair baseline

        if cache_hit:
            stats["cache_hits"] += 1
            stats["latencies_cached"].append(elapsed)
        else:
            stats["cache_misses"] += 1
            stats["latencies_uncached"].append(elapsed)

        print(
            f"[{i+1:02d}] tier={tier:6} "
            f"cache={str(cache_hit):5} "
            f"latency={elapsed:6.2f}s "
            f"cost=${cost:.4f}"
        )

    print("\n=== FP2 Traffic Simulation Results ===")
    print(f"Total requests: {TOTAL_REQUESTS}\n")

    print("Routing distribution:")
    for tier, count in stats["routing"].items():
        pct = (count / TOTAL_REQUESTS) * 100
        print(f"  {tier:6}: {count:3d} ({pct:.1f}%)")

    print("\nCache:")
    hit_pct = (stats["cache_hits"] / TOTAL_REQUESTS) * 100
    print(f"  Hits:   {stats['cache_hits']} ({hit_pct:.1f}%)")
    print(f"  Misses: {stats['cache_misses']}")

    print("\nLatency:")
    if stats["latencies_cached"]:
        print(f"  Avg cached:   {sum(stats['latencies_cached'])/len(stats['latencies_cached']):.2f}s")
    if stats["latencies_uncached"]:
        print(f"  Avg uncached: {sum(stats['latencies_uncached'])/len(stats['latencies_uncached']):.2f}s")

    print("\nCost:")
    saved = stats["api_only_cost"] - stats["cost_total"]
    saved_pct = (saved / stats["api_only_cost"]) * 100 if stats["api_only_cost"] else 0
    print(f"  Routed total cost: ${stats['cost_total']:.4f}")
    print(f"  API-only estimate: ${stats['api_only_cost']:.4f}")
    print(f"  Cost saved: {saved_pct:.1f}%")


if __name__ == "__main__":
    simulate()
