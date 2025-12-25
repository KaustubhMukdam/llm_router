# LLM Router — Cost-Aware, Confidence-Driven Model Routing

Most LLM systems face a bad tradeoff:
- **Always use API models** → great quality, terrible cost  
- **Always use local models** → cheap, but risky and unpredictable  

This project solves that by making **model selection an engineering decision**, not a guess.

Each request is routed to **small, medium, or API models** based on:
- Task type
- Confidence
- Context size
- Safety constraints

**The result**: Near-API quality at a fraction of the cost, with full explainability.

---

## 🚨 The Problem

Naive LLM systems usually:
- Send everything to an API
- Or rely on brittle rules like "short → local, long → API"

These approaches fail when:
- The task is ambiguous
- Confidence is low
- Context silently overflows
- Quality degrades without warning

**This router explicitly models uncertainty.**

---

## 🧠 How Routing Works (Mental Model)

Routing is a deterministic decision pipeline:

```
       Request
          │
  ┌───────┴────────┐
  │ Static Rules   │  (risk level, context size)
  └───────┬────────┘
          │
  ┌───────┴────────┐
  │ ML Classifier  │  (task + confidence)
  └───────┬────────┘
          │
  ┌───────┴────────┐
  │ Heuristics     │  (context dominance, generation weight)
  └───────┬────────┘
          │
  ┌───────┴────────┐
  │ Safety Layer   │  (context-window enforcement)
  └───────┬────────┘
          │
       Final Tier
    (small / medium / api)
```

### Why **medium** exists

**Medium** is the uncertainty buffer:
- Too risky for small
- Not expensive enough to justify API
- Absorbs ambiguity safely

---

## ⚖️ Why This Is Different From "Always API"

| Naive System | This System |
|-------------|-------------|
| Cost scales linearly | Cost scales with confidence |
| No explainability | Every decision is explained |
| Silent failures | Context-window safety |
| No metrics | Traffic simulation + baselines |

This is not "prompt engineering".  
It's **decision engineering around LLMs**.

---

## 📊 Key Results (FP3)

From controlled traffic simulation:

- **~99.6% cost saved** vs API-only baseline
- Balanced routing across tiers:
  - `small` → confident, cheap tasks
  - `medium` → uncertain but safe
  - `api` → large or risky contexts
- Deterministic behavior (golden routing test)

**Example FP3 distribution:**
- ~50% medium  
- ~30% API  
- ~20% small  

---

## ▶️ Run the Demo Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API

```bash
uvicorn app.main:app --reload
```

### 3. Run traffic simulation

```bash
python scripts/simulate_traffic_fp3.py
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🖼️ Frontend

The UI visualizes:
- Chosen model tier
- Confidence score
- Routing explanation
- Latency and cost signals

*Screenshots go here*

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Routing** | Deterministic rules + heuristics + ML |
| **Classifier** | TF-IDF + Logistic Regression |
| **API** | FastAPI |
| **Cache** | Redis |
| **Metrics** | Prometheus |
| **Frontend** | React + Tailwind |

---

## 🎯 Who This Is For

- LLM engineers
- MLOps / infra engineers
- Teams building cost-sensitive AI systems

**This project is intentionally boring, explainable, and reliable.**  
That's how real systems win.

---

## 📖 Documentation

- [Architecture Overview](./ARCHITECTURE.md) — deep dive into design decisions
- API documentation — available at `/docs` when running locally

---

## 🤝 Contributing

Contributions are welcome. Please open an issue first to discuss major changes.

---

## 🔗 Related Resources

- [Experiments & Evidence](./EXPERIMENTS.md)