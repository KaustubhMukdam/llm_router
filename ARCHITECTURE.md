# LLM Router — Architecture Overview

## 1. Problem Statement

Modern LLM applications default to a single large API model for all requests. This approach is simple, but it is:

- **Unnecessarily expensive** — high-cost models used for trivial tasks
- **Slow for simple tasks** — latency overhead from oversized models
- **Opaque** — no explanation of why a model was chosen

**Goal**: Build a cost-aware, explainable, and deterministic model routing system without sacrificing response quality.

---

## 2. High-Level Design

The router selects between three tiers:

| Tier | Description |
|------|-------------|
| **small** | Fast, cheap, local model |
| **medium** | Balanced local model for uncertainty |
| **api** | High-cost external model (last resort) |

### Decision Pipeline

Routing decisions are made using a layered pipeline:

1. **Static rules** — hardcoded routing logic for known patterns
2. **Heuristics** — simple rule-based filtering
3. **ML classifier** — task type + confidence prediction
4. **Context window safety** — token limit enforcement
5. **Fallback policy** — conservative default when uncertain

Each stage produces **explainable signals**, exposed to the frontend.

---

## 3. Why TF-IDF + Logistic Regression?

We intentionally chose a **simple, classical ML model** over deep learning.

### Rationale

- **Fast inference** — microseconds, not milliseconds
- **Deterministic behavior** — same input always produces same output
- **Low operational complexity** — no GPU, no framework dependencies
- **Interpretable decision boundaries** — understandable feature weights
- **Reliable confidence scores** — `predict_proba` outputs are calibrated

### Scope

This classifier is **not** trying to generate text. It only answers a narrow question:

> "What kind of task is this prompt?"

For that purpose, TF-IDF + Logistic Regression consistently outperformed more complex approaches in:
- Latency
- Explainability  
- Stability

---

## 4. Task Classification Targets

The classifier predicts one of three task types:

| Task Type | Description |
|-----------|-------------|
| `classification` | Categorization, labeling, yes/no questions |
| `reasoning` | Logic, math, multi-step inference |
| `generation` | Creative writing, summarization, open-ended text |

These labels map directly to routing behavior and are **intentionally coarse**.

Fine-grained task taxonomies were rejected to avoid:
- Overfitting
- Ambiguity
- Classification instability

---

## 5. Why Confidence Bands Exist

Raw model predictions are **not sufficient**.

Instead of trusting the classifier blindly, we introduce **confidence bands**:

| Confidence Level | Threshold | Routing Behavior |
|------------------|-----------|------------------|
| **High** | ≥ 70% | Route aggressively to cheapest valid tier |
| **Medium** | 45–70% | Route conservatively to medium tier |
| **Low** | < 45% | Defer to fallback policy or API |

### Purpose

Confidence is treated as a **risk signal**, not an accuracy metric.

This prevents:
- Overconfident misrouting
- Silent quality degradation
- Brittle decision boundaries

---

## 6. Why the Medium Tier Exists (Uncertainty Buffer)

The medium tier is **not about performance** — it is about **safety**.

### When It's Used

The medium tier serves as a buffer when:
- The classifier is uncertain
- Heuristics partially apply
- The task is complex but not critical
- Context size is moderate

### Why It Matters

Without this tier, the system would oscillate between:
- **Overusing the API** (too expensive)
- **Underusing small models** (quality risk)

The medium tier **absorbs uncertainty** and stabilizes routing behavior.

---

## 7. Context Window Safety

Before final routing, the system enforces a **context window safety check**.

### Behavior

If estimated total tokens exceed a tier's capacity:
- The request is **escalated automatically**
- Escalation is **recorded in the routing explanation**

### Guarantees

- Zero context overflows
- Deterministic escalation paths
- Explainable failures

---

## 8. Fallback Policy

When no rule or classifier decision is acceptable, the system applies a **conservative fallback**:

| Condition | Action |
|-----------|--------|
| High risk | → API |
| Low latency requirement | → medium |
| Otherwise | → API |

The fallback is:
- Explicit
- Conservative
- Explainable

There is **no silent failure path**.

---

## 9. Design Philosophy

This system prioritizes:

1. **Explainability over novelty** — every decision is traceable
2. **Determinism over raw accuracy** — predictable behavior under load
3. **Cost control over theoretical optimality** — practical efficiency
4. **Engineering evidence over heuristics** — data-driven decisions

### Result

A router that behaves **predictably under load** and is suitable for **production environments**.