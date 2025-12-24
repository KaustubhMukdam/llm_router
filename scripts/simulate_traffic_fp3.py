import requests
import time
from collections import Counter

BASE_URL = "http://localhost:8000/generate"

HEADERS = {
    "Content-Type": "application/json",
}

# -----------------------------
# FP3 Curated Prompt Sets
# -----------------------------

CLASS_A_REASONING = [
    "Compare REST and GraphQL for mobile applications and explain when each is preferable.",
    "Analyze the tradeoffs between multithreading and multiprocessing in Python.",
    "Explain how database indexing improves query performance and when it can hurt.",
    "Compare SQL and NoSQL databases for large-scale analytics workloads.",
    "Explain eventual consistency and where it is acceptable in distributed systems.",
    "Analyze pros and cons of monolith vs microservices architecture.",
    "Explain how caching improves system performance and common pitfalls.",
    "Compare synchronous vs asynchronous APIs and their impact on scalability.",
    "Analyze how load balancers distribute traffic and prevent failures.",
    "Explain the difference between vertical and horizontal scaling."
]

CLASS_B_CONTEXT_REASONING = [
    {
        "prompt": "Based on the context, identify key architectural risks and suggest mitigations.",
        "context": [
            "The system uses a single PostgreSQL instance for all reads and writes. "
            "Traffic has grown 3x in the last 6 months. "
            "No read replicas are configured. "
            "Backups run nightly and block writes for several minutes."
        ]
    },
    {
        "prompt": "Analyze the design issues in the context and propose improvements.",
        "context": [
            "The backend processes requests synchronously. "
            "Each request triggers 4 external API calls. "
            "Timeouts are handled by retries without circuit breakers."
        ]
    },
    {
        "prompt": "Identify scalability concerns and recommend changes.",
        "context": [
            "All user sessions are stored in-memory on a single server. "
            "Auto-scaling is enabled but sessions are not shared."
        ]
    },
    {
        "prompt": "Evaluate the system reliability risks described below.",
        "context": [
            "The deployment pipeline has no automated rollback. "
            "Monitoring alerts are triggered only after 5 minutes of downtime."
        ]
    }
]

CLASS_C_STEPWISE = [
    "Explain step by step how an HTTP request flows through a load balancer, application server, and database.",
    "Explain step by step how authentication works using JWT tokens.",
    "Explain step by step how a CI/CD pipeline deploys code safely.",
    "Explain step by step how DNS resolution works."
]

# -----------------------------
# Traffic Plan
# -----------------------------

TRAFFIC_PLAN = (
    [(p, []) for p in CLASS_A_REASONING[:12]] +
    [(x["prompt"], x["context"]) for x in CLASS_B_CONTEXT_REASONING[:10]] +
    [(p, []) for p in CLASS_C_STEPWISE[:6]] +
    [
        # Edge cases (sanity checks)
        ("Summarize this text briefly.", ["Short text about caching."]),
        ("Explain neural networks simply.", [])
    ]
)

# -----------------------------
# Simulation
# -----------------------------

stats = {
    "latencies": [],
    "cached_latencies": [],
    "uncached_latencies": [],
    "cost": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
}

routing_counter = Counter()

print("\n=== FP3 Traffic Simulation (Controlled) ===\n")

for i, (prompt, context) in enumerate(TRAFFIC_PLAN, start=1):
    payload = {
        "prompt": prompt,
        "context": context,
        "constraints": {
            "max_latency_ms": 2000,
            "max_cost_usd": 0.01,
            "risk_level": "low",
        },
        "debug": True,
    }

    start = time.time()
    resp = requests.post(BASE_URL, json=payload, headers=HEADERS, timeout=300)
    latency = time.time() - start

    data = resp.json()
    tier = data.get("model_used")
    cache_hit = data.get("cache_hit", False)
    cost = data.get("estimated_cost_usd", 0.0)

    routing_counter[tier] += 1
    stats["latencies"].append(latency)
    stats["cost"] += cost

    if cache_hit:
        stats["cache_hits"] += 1
        stats["cached_latencies"].append(latency)
    else:
        stats["cache_misses"] += 1
        stats["uncached_latencies"].append(latency)

    print(
        f"[{i:02d}] tier={tier:<6} "
        f"cache={str(cache_hit):<5} "
        f"latency={latency:6.2f}s "
        f"cost=${cost:.4f}"
    )

# -----------------------------
# Results Summary
# -----------------------------

total = len(TRAFFIC_PLAN)

print("\n=== FP3 Results Summary ===\n")

print("Routing distribution:")
for tier, count in routing_counter.items():
    print(f"  {tier:<6}: {count:3d} ({count / total * 100:.1f}%)")

print("\nCache:")
print(f"  Hits:   {stats['cache_hits']} ({stats['cache_hits'] / total * 100:.1f}%)")
print(f"  Misses: {stats['cache_misses']}")

if stats["cached_latencies"]:
    print(f"\nLatency:")
    print(f"  Avg cached:   {sum(stats['cached_latencies']) / len(stats['cached_latencies']):.2f}s")
    print(f"  Avg uncached: {sum(stats['uncached_latencies']) / max(len(stats['uncached_latencies']),1):.2f}s")

baseline_api_cost = total * 0.02  # rough API-only estimate
saved = baseline_api_cost - stats["cost"]

print("\nCost:")
print(f"  Routed total cost: ${stats['cost']:.4f}")
print(f"  API-only estimate: ${baseline_api_cost:.4f}")
print(f"  Cost saved: {saved / baseline_api_cost * 100:.1f}%")
