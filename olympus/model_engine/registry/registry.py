"""Model Registry for managing model lifecycle and metadata."""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import yaml
from huggingface_hub import HfApi, login, hf_hub_download

class ModelRegistry:
    """Registry for managing model lifecycle and metadata."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the model registry.
        
        Args:
            config_dir: Directory for storing model configs
        """
        self.config_dir = Path(config_dir) if config_dir else Path("model_configs")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.hf_api = HfApi()
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with HuggingFace."""
        token = os.getenv('HF_TOKEN')
        if token:
            try:
                login(token)
            except Exception as e:
                print(f"Warning: HF authentication failed: {e}")
    
    def get_model(self, model_name: str, version: Optional[str] = None) -> Any:
        """Get a model from the registry.
        
        Args:
            model_name: Name/ID of the model
            version: Optional version string
            
        Returns:
            Model instance
        """
        config = self._get_model_config(model_name)
        return self._load_model(model_name, config, version)
    
    def _get_model_config(self, model_id: str) -> Dict[str, Any]:
        """Get model configuration.
        
        Args:
            model_id: HuggingFace model ID
            
        Returns:
            Model configuration dictionary
        """
        config_path = self.config_dir / f"{model_id.replace('/', '_')}_config.json"
        
        # Download if not exists
        if not config_path.exists():
            try:
                downloaded_path = hf_hub_download(
                    repo_id=model_id,
                    filename="config.json",
                    local_dir=self.config_dir,
                    local_dir_use_symlinks=False
                )
                # Rename to our convention
                os.rename(downloaded_path, config_path)
            except Exception as e:
                raise Exception(f"Error downloading config for {model_id}: {e}")
        
        # Load config
        with open(config_path) as f:
            return json.load(f)
    
    def _load_model(self, model_id: str, config: Dict[str, Any], version: Optional[str]) -> Any:
        """Load model based on configuration.
        
        Args:
            model_id: HuggingFace model ID
            config: Model configuration
            version: Optional version string
            
        Returns:
            Loaded model instance
        """
        # Import here to avoid circular imports
        from transformers import AutoModel, AutoModelForCausalLM
        
        model_type = config.get('model_type', '')
        architectures = config.get('architectures', [])
        
        if any('CausalLM' in arch for arch in architectures):
            return AutoModelForCausalLM.from_pretrained(
                model_id,
                revision=version,
                trust_remote_code=True
            )
        else:
            return AutoModel.from_pretrained(
                model_id,
                revision=version,
                trust_remote_code=True
            )
    
    def search_models(self, 
                     filters: Optional[Dict[str, Any]] = None,
                     min_size: float = 0,
                     max_size: float = float('inf')) -> List[Dict[str, Any]]:
        """Search for models matching criteria.
        
        Args:
            filters: Dictionary of filter criteria
            min_size: Minimum model size in GB
            max_size: Maximum model size in GB
            
        Returns:
            List of matching model metadata
        """
        # Convert filters to lowercase for case-insensitive matching
        if filters:
            filters = {k: [v.lower() if isinstance(v, str) else v 
                         for v in vals] 
                     for k, vals in filters.items()}
        
        models = []
        for model in self.hf_api.list_models():
            if self._matches_filters(model, filters):
                # Check size constraints
                size_gb = model.siblings_rpartition_size / (1024 * 1024 * 1024)
                if min_size <= size_gb <= max_size:
                    models.append({
                        'id': model.id,
                        'downloads': model.downloads,
                        'likes': model.likes,
                        'tags': model.tags,
                        'pipeline_tags': model.pipeline_tags,
                        'size_gb': size_gb
                    })
        
        return sorted(models, key=lambda x: x['downloads'], reverse=True)
    
    def _matches_filters(self, model: Any, filters: Optional[Dict[str, Any]]) -> bool:
        """Check if model matches filter criteria.
        
        Args:
            model: Model metadata
            filters: Filter criteria
            
        Returns:
            True if model matches all criteria
        """
        if not filters:
            return True
            
        model_id = model.id.lower()
        model_tags = [t.lower() for t in (model.tags or [])]
        pipeline_tags = [t.lower() for t in (model.pipeline_tags or [])]
        
        for key, values in filters.items():
            if key == 'require_all':
                # All values must be present
                for val in values:
                    if not (val in model_id or 
                           val in model_tags or 
                           val in pipeline_tags):
                        return False
            elif key == 'require_any':
                # At least one value must be present
                if not any(val in model_id or 
                          val in model_tags or 
                          val in pipeline_tags 
                          for val in values):
                    return False
        
        return True
