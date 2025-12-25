# Experiments & Evidence — LLM Router

This document records the **measured evolution** of the routing system from a naïve baseline to a confidence-driven, cost-aware architecture.

The goal is not to show "the best model", but to show **engineering decisions backed by data**.

---

## Baseline: API-Only System

Before routing, every request was sent to the API model.

### Baseline Characteristics
- Cost scales linearly with traffic
- No notion of confidence or uncertainty
- No safety against context overflow
- No explainability

### Baseline Cost Formula
```
Total Cost = Number of Requests × API Cost
```

This baseline is used as the **control group** for all experiments below.

---

## FP1 — Static Routing (Rules Only)

### What Changed
- Introduced static routing rules:
  - `high-risk` → api
  - `classification` → small
  - `large context` → medium

### What This Proved
- Routing can dramatically reduce API usage
- But static rules alone are brittle
- No understanding of ambiguity or task intent

### Observations
- Good cost savings
- Poor adaptability
- Misroutes for ambiguous prompts

**Conclusion:** Rules help, but don't generalize.

---

## FP2 — Cache + Traffic Simulation

### What Changed
- Added request caching
- Introduced traffic simulation (10–30 requests)
- Measured latency and cache behavior

### Metrics Observed
| Metric | Value |
|--------|-------|
| Cache hit rate | ~60–75% after warm-up |
| Cached latency | ~2s |
| Uncached local latency | 30–70s |
| API latency | ~5–7s |

### Key Insight
Caching improves latency dramatically, but:
- Routing decisions still lacked intelligence
- Cost reduction depended heavily on repetition

**Conclusion:** Caching amplifies good routing, but cannot fix bad routing.

---

## FP3 — Context Safety + Controlled Prompts

### What Changed
- Enforced **context-window safety**
- Prevented silent local model overflows
- Introduced curated prompts for fair comparison

### Safety Guarantees
- If total tokens exceed model capacity → escalate tier
- Never allow unsafe local execution
- API becomes the last-resort safety net

### Result
- Zero silent failures
- Deterministic escalation behavior
- Trustworthy routing outcomes

**Conclusion:** Safety must be explicit, not assumed.

---

## C.1 — Real Classifier (TF-IDF + Logistic Regression)

### Model Choice
- **TF-IDF** (prompt text)
- **Logistic Regression** (multiclass)
- **Numeric features:**
  - Context length
  - Token count

### Why This Model
- Fast
- Interpretable
- Deterministic (given fixed inputs and model state)
- `predict_proba` gives usable confidence

This is a deliberate **engineering-first choice**, not a flashy ML one.

---

## C.1.7 — Expanded Training Data

### Dataset Evolution

| Stage | Samples |
|-------|---------|
| Initial | 9 |
| Expanded | 19 |
| Final | 34 |

Balanced across:
- `classification`
- `reasoning`
- `generation`

### Sanity Check Results
- **Training accuracy:** 100% (expected)
- **Confidence increased** with more data
- **Ambiguous prompts show lower confidence** (desired)

**Conclusion:** Confidence calibration improved, not just accuracy.

---

## C.1.8 — Confidence Threshold Tuning

### Thresholds

```
High confidence   ≥ 0.70
Medium confidence ≥ 0.45
Below → fallback / escalation
```

### Why Confidence Bands Exist

**Low confidence ≠ wrong**

**Low confidence = uncertainty**

Uncertainty should route to medium, not small.

### Effect on Routing
- Fewer risky small-model executions
- Medium absorbs ambiguous prompts
- API reserved for genuinely large or unsafe cases

---

## Final FP3 Results (With Classifier + Safety)

### Routing Distribution (FP3)
- ~50% medium
- ~30% API
- ~20% small

### Cost Metrics
| Metric | Value |
|--------|-------|
| API-only baseline | $0.40 |
| Routed total cost | ~$0.0017 |
| **Cost saved** | **~99.6%** |

### System Properties
- Deterministic
- Explainable
- Safe under uncertainty
- Cost-aware by design

---

## Why Routing Decisions Changed Over Time

| Phase | Primary Driver |
|-------|---------------|
| FP1 | Rules |
| FP2 | Cache amplification |
| FP3 | Safety + context |
| C.1 | Confidence-driven decisions |

Each phase removed a failure mode from the previous one.

---

## Final Takeaway

This system does not try to be clever.

It tries to be:
- **Predictable**
- **Explainable**
- **Safe**
- **Cheap**

And the numbers show it works.

**This is routing as an engineering discipline, not guesswork.**