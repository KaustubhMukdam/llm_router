"""
Confidence evaluation logic for classifier predictions.
Determines whether to accept a prediction or escalate based on confidence threshold.
"""

from enum import Enum
from classifier.model import ClassifierPrediction
from config import get_config


class ConfidenceDecision(str, Enum):
    """Decision result from confidence evaluation."""
    ACCEPT = "accept"
    ESCALATE = "escalate"


def evaluate_confidence(prediction: ClassifierPrediction) -> ConfidenceDecision:
    """
    Evaluate whether a classifier prediction meets the confidence threshold.
    
    Compares the prediction confidence against the configured minimum threshold
    from routing.yaml. If confidence is sufficient, accepts the prediction.
    Otherwise, signals escalation to a higher model tier.
    
    Args:
        prediction: ClassifierPrediction with confidence score
        
    Returns:
        ConfidenceDecision.ACCEPT if confidence >= threshold
        ConfidenceDecision.ESCALATE if confidence < threshold
    """
    config = get_config()
    threshold = config.routing.thresholds.classifier_confidence_min
    
    if prediction.confidence >= threshold:
        return ConfidenceDecision.ACCEPT
    else:
        return ConfidenceDecision.ESCALATE