"""
Model Config Fetcher - Fetch and manage model configurations from HuggingFace Hub.
"""
from pathlib import Path
import json
import time
from typing import Dict, Any
from loguru import logger
from huggingface_hub import hf_hub_download
from prometheus_client import Summary

from .utils import authenticate_hf
from ..monitoring.metrics import metrics_exporter, record_operation
from ..config import settings

# Metrics
CONFIG_FETCH_TIME = Summary('model_config_fetch_seconds', 'Time spent fetching model configs')

class ModelConfigFetcher:
    """Class for fetching and managing model configurations."""
    
    def __init__(self):
        """Initialize ModelConfigFetcher and authenticate with HuggingFace."""
        authenticate_hf()
        self.cache_dir = settings.HF_CONFIG_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    @CONFIG_FETCH_TIME.time()
    def fetch_config(self, model_id: str) -> Dict[str, Any]:
        """
        Fetch model configuration from HuggingFace.
        
        Args:
            model_id: The HuggingFace model ID
            
        Returns:
            Dict[str, Any]: Model configuration
        """
        start_time = time.time()
        try:
            # Check cache first
            cache_path = self.cache_dir / f"{model_id.replace('/', '_')}_config.json"
            if cache_path.exists():
                logger.info(f"Loading cached config for {model_id}")
                return self._load_cached_config(cache_path)
            
            # Fetch from HuggingFace
            config_path = hf_hub_download(
                model_id,
                "config.json",
                cache_dir=str(settings.HF_MODEL_CACHE_DIR)
            )
            logger.info(f"Successfully fetched config for {model_id}")
            
            # Parse and cache config
            config = self._parse_config(config_path)
            self._cache_config(cache_path, config)
            
            record_operation("config_fetch", "api", start_time)
            return config
            
        except Exception as e:
            logger.error(f"Error fetching config for {model_id}: {str(e)}")
            raise
            
    def _parse_config(self, config_path: str) -> Dict[str, Any]:
        """Parse model configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error parsing config from {config_path}: {str(e)}")
            raise
            
    def _cache_config(self, cache_path: Path, config: Dict[str, Any]) -> None:
        """Cache model configuration."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.debug(f"Cached config to {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to cache config to {cache_path}: {str(e)}")
            
    def _load_cached_config(self, cache_path: Path) -> Dict[str, Any]:
        """Load cached model configuration."""
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cached config from {cache_path}: {str(e)}")
            # If cache is corrupted, remove it
            cache_path.unlink(missing_ok=True)
            raise
