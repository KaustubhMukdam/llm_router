import joblib
import numpy as np
from pathlib import Path

from classifier.model import ClassifierProtocol, ClassifierPrediction
from classifier.features import TaskType
from classifier.vectorizer import FeatureVectorizer

MODEL_PATH = Path(r"D:\Programming\portfolio_projects\llm_router\classifier\model.pkl")


class RealClassifier(ClassifierProtocol):
    def __init__(self):
        bundle = joblib.load(MODEL_PATH)
        self.model = bundle["model"]
        self.vectorizer = bundle["vectorizer"]

    def predict(self, features: FeatureVectorizer) -> ClassifierPrediction:
        # Convert FeatureVector → model input
        X = self.vectorizer.transform(
            [features.prompt],
            [[features.context_length, features.token_count]],
        )

        probs = self.model.predict_proba(X)[0]
        classes = self.model.classes_

        idx = int(np.argmax(probs))
        label = classes[idx]
        confidence = float(probs[idx])

        return ClassifierPrediction(
            predicted_task=TaskType(label),
            confidence=confidence,
        )
