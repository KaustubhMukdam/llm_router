from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
import numpy as np


class FeatureVectorizer:
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3000,
            stop_words="english",
        )

    def fit_transform(self, prompts, numeric_features):
        """
        Used during training.
        """
        text_features = self.text_vectorizer.fit_transform(prompts)
        numeric_array = np.array(numeric_features, dtype=float)

        return hstack([text_features, numeric_array])

    def transform(self, prompts, numeric_features):
        """
        Used during inference.
        """
        text_features = self.text_vectorizer.transform(prompts)
        numeric_array = np.array(numeric_features, dtype=float)

        return hstack([text_features, numeric_array])
