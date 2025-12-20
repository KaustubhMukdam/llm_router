"""
Classifier prediction wrapper.
Provides a unified interface for obtaining predictions from classifier implementations.
"""

from classifier.features import FeatureVector
from classifier.model import ClassifierProtocol, ClassifierPrediction


class Classifier:
    """
    Wrapper for classifier predictions.
    
    This class provides a stable interface for the routing system to obtain
    predictions from any classifier implementation that follows ClassifierProtocol.
    """
    
    def __init__(self, model: ClassifierProtocol):
        """
        Initialize the classifier wrapper.
        
        Args:
            model: A classifier implementation following ClassifierProtocol
        """
        self._model = model
    
    def predict(self, features: FeatureVector) -> ClassifierPrediction:
        """
        Get prediction from the underlying classifier model.
        
        Args:
            features: Extracted feature vector
            
        Returns:
            ClassifierPrediction containing predicted_task and confidence
        """
        return self._model.predict(features)