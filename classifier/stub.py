from classifier.model import ClassifierProtocol, ClassifierPrediction
from classifier.features import FeatureVector, TaskType


class StubClassifier(ClassifierProtocol):
    """
    Temporary stub classifier.

    Always returns a low-confidence GENERATION prediction.
    This ensures routing remains conservative until a real model is plugged in.
    """

    def predict(self, features: FeatureVector) -> ClassifierPrediction:
        return ClassifierPrediction(
            predicted_task=TaskType.GENERATION,
            confidence=0.0,
        )
