import json
import joblib
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from classifier.vectorizer import FeatureVectorizer


DATA_PATH = Path(r"D:\Programming\portfolio_projects\llm_router\classifier\data\training.jsonl")
MODEL_PATH = Path(r"D:\Programming\portfolio_projects\llm_router\classifier\model.pkl")


def load_training_data():
    prompts = []
    numeric_features = []
    labels = []

    with DATA_PATH.open() as f:
        for line in f:
            row = json.loads(line)

            prompts.append(row["prompt"])
            numeric_features.append([
                row["context_length"],
                row["token_count"],
            ])
            labels.append(row["label"])

    return prompts, numeric_features, labels


def evaluate(model, X, y):
    preds = model.predict(X)
    print("\n=== Training-set Evaluation (sanity only) ===")
    print(classification_report(y, preds))


def train():
    prompts, numeric_features, labels = load_training_data()

    vectorizer = FeatureVectorizer()
    X = vectorizer.fit_transform(prompts, numeric_features)

    model = LogisticRegression(
        max_iter=1000,
        n_jobs=-1,
        random_state=42,
    )

    model.fit(X, labels)

    # Sanity check (training set)
    evaluate(model, X, labels)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "vectorizer": vectorizer,
        },
        MODEL_PATH,
    )

    print("\n✅ Classifier trained and saved to", MODEL_PATH)


if __name__ == "__main__":
    train()
