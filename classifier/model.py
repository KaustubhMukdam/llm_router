"""
Classifier model interface definition.
Defines the protocol for classifier implementations without concrete logic.
"""

from typing import Protocol
from classifier.features import FeatureVector, TaskType


class ClassifierPrediction:
    """
    Result of a classifier prediction.
    
    Attributes:
        predicted_task: The predicted task type
        confidence: Confidence score between 0.0 and 1.0
    """
    
    def __init__(self, predicted_task: TaskType, confidence: float):
        """
        Initialize a classifier prediction.
        
        Args:
            predicted_task: Predicted task type
            confidence: Confidence score (0.0 to 1.0)
            
        Raises:
            ValueError: If confidence is not in valid range
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")
        
        self.predicted_task = predicted_task
        self.confidence = confidence


class ClassifierProtocol(Protocol):
    """
    Protocol defining the interface for classifier implementations.
    
    Any classifier used by the routing system must implement this protocol.
    """
    
    def predict(self, features: FeatureVector) -> ClassifierPrediction:
        """
        Predict task type and confidence from features.
        
        Args:
            features: Extracted feature vector
            
        Returns:
            ClassifierPrediction with task and confidence
        """
        ...