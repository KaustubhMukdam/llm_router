import joblib

from features import estimate_output_tokens
from vectorizer import FeatureVectorizer

MODEL_PATH = r"D:\Programming\portfolio_projects\llm_router\classifier\model.pkl"

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
vectorizer = bundle["vectorizer"]

tests = [
    ("Classify this email as spam", 0, 5),
    ("Why is quicksort faster than bubble sort?", 0, 6),
    ("Explain transformers step by step", 0, 6),
    ("Summarize the following meeting", 1200, 4),
]

print("\n=== Sanity Check ===")
for prompt, ctx_len, tok_cnt in tests:
    X = vectorizer.transform(
        [prompt],
        [[ctx_len, tok_cnt]],
    )

    probs = model.predict_proba(X)[0]
    pred = model.classes_[probs.argmax()]
    confidence = probs.max()

    print(f"\nPrompt: {prompt}")
    print(f" → Predicted: {pred}")
    print(f" → Confidence: {confidence:.2f}")
