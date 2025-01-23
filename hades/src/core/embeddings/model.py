"""Text embedding model using transformers."""

# TODO: Future Improvements
# 1. Implement Redis-based distributed cache for embeddings:
#    - Use Redis as a distributed cache layer
#    - Add TTL for cached embeddings
#    - Implement cache invalidation strategy
#    - Add cache stats monitoring
#
# 2. Implement batch embedding generation:
#    - Add batch processing methods
#    - Implement dynamic batching based on input lengths
#    - Add queue system for batch collection
#    - Optimize batch size based on available GPU memory
#    - Add batch processing metrics

import torch
from typing import List, Optional
from loguru import logger
from prometheus_client import Summary, Counter
from transformers import AutoTokenizer, AutoModel
from functools import lru_cache

from core.config import settings

# Metrics
EMBEDDING_TIME = Summary('embedding_generation_seconds', 'Time spent generating embeddings')
EMBEDDING_OPS = Counter('embedding_operations_total', 'Total embedding operations')
EMBEDDING_ERRORS = Counter('embedding_errors_total', 'Total embedding errors')

class EmbeddingModel:
    """Manages text embedding generation using transformers."""
    
    def __init__(self):
        """Initialize embedding model."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the model and tokenizer."""
        try:
            if self._initialized:
                return True
                
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.HF_MODEL_CACHE_DIR,
                use_auth_token=settings.HF_TOKEN
            )
            
            self.model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=settings.HF_MODEL_CACHE_DIR,
                use_auth_token=settings.HF_TOKEN
            ).to(self.device)
            
            # Set to evaluation mode
            self.model.eval()
            
            self._initialized = True
            logger.info(f"Embedding model {self.model_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            EMBEDDING_ERRORS.inc()
            return False
            
    @torch.no_grad()
    async def generate(
        self,
        text: str,
        pooling: str = 'mean'
    ) -> Optional[List[float]]:
        """
        Generate embeddings for input text.
        
        Args:
            text: Input text to embed
            pooling: Pooling strategy ('mean' or 'cls')
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            with EMBEDDING_TIME.time():
                # Ensure model is initialized
                if not self._initialized:
                    if not await self.initialize():
                        return None
                
                # Tokenize text
                inputs = self.tokenizer(
                    text,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors='pt'
                ).to(self.device)
                
                # Generate embeddings
                outputs = self.model(**inputs)
                
                # Pool embeddings
                if pooling == 'cls':
                    embeddings = outputs.last_hidden_state[:, 0]
                else:  # mean pooling
                    attention_mask = inputs['attention_mask']
                    embeddings = mean_pooling(
                        outputs.last_hidden_state,
                        attention_mask
                    )
                
                # Normalize embeddings
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
                
                # Convert to list and return
                embedding_list = embeddings[0].cpu().tolist()
                
                EMBEDDING_OPS.inc()
                return embedding_list
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            EMBEDDING_ERRORS.inc()
            return None
            
    @lru_cache(maxsize=1024)
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text if available."""
        return None  # Placeholder for actual cache implementation

def mean_pooling(token_embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """
    Perform mean pooling on token embeddings.
    
    Args:
        token_embeddings: Model output embeddings
        attention_mask: Attention mask from tokenizer
        
    Returns:
        Pooled embeddings
    """
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
