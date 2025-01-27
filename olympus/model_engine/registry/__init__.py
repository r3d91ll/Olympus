"""Model registry implementation."""
from typing import Any, Dict, List, Optional

from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel
from huggingface_hub import HfApi

class ModelRegistry:
    """Registry for managing model access."""
    
    def __init__(self) -> None:
        """Initialize model registry."""
        self._model_cache: Dict[str, PreTrainedModel] = {}
        self._default_model = "Salesforce/codegen-350M-mono"
        
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
                
            # Store tokenizer with model
            model.tokenizer = tokenizer
            self._model_cache[model_name] = model
            
        return self._model_cache[model_name]
        
    def search(self, query: str) -> List[str]:
        """Search for models.
        
        Args:
            query: Search query
            
        Returns:
            List of model names matching the query and having code-generation tag
        """
        hub = HfApi()
        models = hub.list_models(
            search=query,
            filter="code-generation"
        )
        return [model.modelId for model in list(models)]  # Convert iterator to list
        
    def get_default_model(self) -> PreTrainedModel:
        """Get default model.
        
        Returns:
            Default model
        """
        return self.get_model(self._default_model)