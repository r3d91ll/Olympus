"""
Common utilities for model management operations.
"""
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
from huggingface_hub import login
from pydantic import BaseModel

from ..config import settings

class ModelConfig(BaseModel):
    """Pydantic model for model search configuration."""
    min_size: float = 0.0
    max_size: float = float('inf')
    required_keywords: List[str] = []
    excluded_keywords: List[str] = []
    model_types: List[str] = []
    
def authenticate_hf() -> None:
    """Authenticate with HuggingFace using token from environment."""
    token = settings.HF_TOKEN
    if not token:
        logger.warning("HF_TOKEN not found in environment variables. Some features may be limited.")
        return
        
    try:
        login(token)
        logger.info("Successfully authenticated with HuggingFace")
    except Exception as e:
        logger.error(f"Error authenticating with HuggingFace: {str(e)}")
        raise

def load_config(config_path: Path) -> ModelConfig:
    """Load and validate model configuration."""
    try:
        return ModelConfig.parse_file(config_path)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {str(e)}")
        raise
