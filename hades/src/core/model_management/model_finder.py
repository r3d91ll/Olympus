"""
Model Finder - Search for models on Hugging Face Hub based on configurable parameters.
"""
from typing import Dict, List, Any
from pathlib import Path
import time
from loguru import logger
from huggingface_hub import HfApi
from prometheus_client import Summary

from .utils import ModelConfig, authenticate_hf
from ..monitoring.metrics import metrics_exporter, record_operation
from ..config import settings

# Metrics
MODEL_SEARCH_TIME = Summary('model_search_seconds', 'Time spent searching for models')

class ModelFinder:
    """Class for searching and filtering models from HuggingFace Hub."""
    
    def __init__(self, config: ModelConfig):
        """Initialize ModelFinder with search configuration."""
        self.config = config
        self.api = HfApi()
        authenticate_hf()
        
    @MODEL_SEARCH_TIME.time()
    def search_models(self) -> List[Dict[str, Any]]:
        """
        Search for models matching configuration criteria.
        
        Returns:
            List[Dict[str, Any]]: List of matching model information
        """
        start_time = time.time()
        try:
            models = self.api.list_models()
            filtered_models = self._filter_results(models)
            logger.info(f"Found {len(filtered_models)} matching models")
            record_operation("model_search", "api", start_time)
            return filtered_models
        except Exception as e:
            logger.error(f"Error searching models: {str(e)}")
            raise
            
    def _filter_results(self, models: List[Any]) -> List[Dict[str, Any]]:
        """
        Filter models based on configuration criteria.
        
        Args:
            models: List of model information from HuggingFace
            
        Returns:
            List[Dict[str, Any]]: Filtered list of models
        """
        filtered_models = []
        
        for model in models:
            if not self._matches_criteria(model):
                continue
                
            filtered_models.append(self._format_model_info(model))
            
        return filtered_models
        
    def _matches_criteria(self, model: Any) -> bool:
        """Check if model matches the search criteria."""
        # Check required keywords
        if self.config.required_keywords:
            if not any(kw.lower() in model.modelId.lower() for kw in self.config.required_keywords):
                return False
                
        # Check excluded keywords
        if self.config.excluded_keywords:
            if any(kw.lower() in model.modelId.lower() for kw in self.config.excluded_keywords):
                return False
                
        # Check model types
        if self.config.model_types:
            if not any(mt.lower() == model.pipeline_tag.lower() for mt in self.config.model_types):
                return False
                
        return True
        
    def _format_model_info(self, model: Any) -> Dict[str, Any]:
        """Format model information for consistent output."""
        return {
            "id": model.modelId,
            "name": model.modelId.split("/")[-1],
            "author": model.modelId.split("/")[0],
            "type": model.pipeline_tag,
            "downloads": getattr(model, "downloads", 0),
            "likes": getattr(model, "likes", 0),
            "tags": getattr(model, "tags", [])
        }
