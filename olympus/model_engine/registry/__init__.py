"""Model registry implementation."""
from typing import Any, Dict, Optional

from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel

class ModelRegistry:
    """Registry for managing model access."""
    
    def __init__(self) -> None:
        """Initialize model registry."""
        self._model_cache: Dict[str, PreTrainedModel] = {}
        
    def get_model(self, model_name: str) -> PreTrainedModel:
        """Get model by name.
        
        Args:
            model_name: Name of model to get
            
        Returns:
            Loaded model
        """
        if model_name not in self._model_cache:
            # Load model and tokenizer
            model = AutoModelForCausalLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Configure tokenizer
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                model.config.pad_token_id = tokenizer.pad_token_id
                
            self._model_cache[model_name] = model
            
        return self._model_cache[model_name]