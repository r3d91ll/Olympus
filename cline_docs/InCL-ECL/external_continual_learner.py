from typing import Dict, List, Union
import numpy as np

from .tag_generator import TagGenerator
from .gaussian_model import GaussianModel
from ..inference import InContextLearner

class ExternalContinualLearner:
    """External Continual Learner for managing and learning from external knowledge.
    
    This class combines tag generation, Gaussian modeling, and in-context learning
    to provide continual learning capabilities using external knowledge sources.
    
    Attributes:
        tag_generator (TagGenerator): Generates tags from user queries
        gaussian_model (GaussianModel): Models tag distributions for classes
        in_context_learner (InContextLearner): Generates responses using context
    """
    
    def __init__(self, llm, transformer):
        """Initialize the learner with an LLM.
        
        Args:
            llm: Language model for tag generation and response generation
            transformer: Optional SentenceTransformer instance for embeddings
        """
        self.transformer = transformer
        self.tag_generator = TagGenerator(llm)
        self.gaussian_model = GaussianModel(transformer)
        self.in_context_learner = InContextLearner(llm)
        
    def add_class(self, class_name: str, tag_embeddings: np.ndarray) -> None:
        """Add a new class with its tag embeddings.
        
        Args:
            class_name: Name of the class to add
            tag_embeddings: Numpy array of tag embeddings for the class
        """
        self.gaussian_model.add_class(class_name, tag_embeddings)
        
    def generate_tags(self, user_query: str) -> List[str]:
        """Generate tags from a user query.
        
        Args:
            user_query: The query to generate tags for
            
        Returns:
            List of generated tags
        """
        return self.tag_generator.generate_tags(user_query)
        
    def select_top_k_classes(
        self,
        query_tags: List[str],
        k: int = 3
    ) -> List[str]:
        """Select top k most relevant classes for query tags.
        
        Args:
            query_tags: List of tags from the query
            k: Number of classes to select
            
        Returns:
            List of top k class names
        """
        return self.gaussian_model.select_top_k_classes(query_tags, k=k)
        
    def generate_response(
        self,
        query: str,
        class_summaries: Dict[str, str],
        k: int = 3
    ) -> str:
        """Generate a response using relevant class knowledge.
        
        Args:
            query: The user query
            class_summaries: Dictionary mapping class names to their summaries
            k: Number of top classes to consider
            
        Returns:
            Generated response incorporating relevant class knowledge
        """
        tags = self.generate_tags(query)
        top_k_classes = self.select_top_k_classes(tags, k=k)
        response = self.in_context_learner.generate_response(
            query, top_k_classes, class_summaries
        )
        return response
