import numpy as np
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer

class GaussianModel:
    def __init__(self, transformer=None, model_name="all-MiniLM-L6-v2"):
        self.transformer = transformer if transformer is not None else SentenceTransformer(model_name)
        self.class_models = {}
        self.shared_covariance = np.eye(2)  # Initialize with 2D identity matrix
        self.epsilon = 1e-6  # Small constant for numerical stability

    def add_class(self, class_name: str, tag_embeddings: np.ndarray) -> None:
        """Add a new class to the model with its tag embeddings."""
        mean_vector = np.mean(tag_embeddings, axis=0)
        if self.shared_covariance is None:
            self.shared_covariance = np.cov(tag_embeddings.T)
        else:
            new_covariance = np.cov(tag_embeddings.T)
            n_previous_classes = len(self.class_models)
            self.shared_covariance = (
                (n_previous_classes * self.shared_covariance + new_covariance) / (n_previous_classes + 1)
            )
        
        # Add small regularization term to ensure matrix is invertible
        self.shared_covariance += np.eye(self.shared_covariance.shape[0]) * self.epsilon
        
        self.class_models[class_name] = {
            "mean_vector": mean_vector,
            "tag_embeddings": tag_embeddings
        }

    def mahalanobis_distance(self, query_embedding: np.ndarray, mean_vector: np.ndarray) -> float:
        """Calculate the Mahalanobis distance between a query embedding and a class mean vector."""
        inv_covariance = np.linalg.inv(self.shared_covariance)
        diff = query_embedding - mean_vector
        return np.sqrt(diff.T @ inv_covariance @ diff)

    def select_top_k_classes(self, query_tags: List[str], k: int = 3) -> List[str]:
        """Select top k classes based on average Mahalanobis distance to query tags."""
        if not query_tags:
            raise ValueError("Query tags cannot be empty")
            
        query_embeddings = self.transformer.encode(query_tags)
        distances = {}
        for class_name, model in self.class_models.items():
            avg_distance = np.mean([
                self.mahalanobis_distance(embedding, model["mean_vector"])
                for embedding in query_embeddings
            ])
            distances[class_name] = avg_distance
        sorted_classes = sorted(distances.items(), key=lambda x: x[1])
        return [cls for cls, _ in sorted_classes[:k]]
