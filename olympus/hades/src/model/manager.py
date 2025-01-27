"""Model manager module for HADES."""
from typing import Dict, List, Optional, Any
import asyncio
from pathlib import Path
import yaml
from loguru import logger
from pydantic import BaseModel
from olympus.model_engine import ModelEngine, ModelRegistry, InferenceEngine
from olympus.model_engine.monitoring import ModelMonitor

class ModelMetadata(BaseModel):
    """Model metadata."""
    name: str
    version: str
    type: str
    embedding_dim: int = 768
    max_sequence_length: int = 512
    device: str = "cuda"

async def init_model_engine(config_path: str) -> ModelEngine:
    """Initialize model engine with config."""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
        
    try:
        # Load config
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        model_config = config.get("model_engine", {})
        
        # Initialize components with appropriate config subsets
        registry = ModelRegistry(
            config_dir=str(Path(model_config.get("model_dir", "models")) / "configs")
        )
        
        inference = InferenceEngine()
        
        monitor = ModelMonitor()
        
        # Create engine
        engine = ModelEngine(
            registry=registry,
            inference=inference,
            monitor=monitor
        )
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize model engine: {str(e)}")
        raise

async def list_available_models(engine: ModelEngine) -> List[ModelMetadata]:
    """List available models in the registry."""
    try:
        models = await engine.list_models()
        return [ModelMetadata(**model) for model in models]
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise

async def download_model(
    engine: ModelEngine,
    model_name: str,
    version: Optional[str] = None
) -> None:
    """Download model from registry."""
    try:
        await engine.download_model(model_name, version)
    except Exception as e:
        logger.error(f"Failed to download model {model_name}: {str(e)}")
        raise

async def load_model(
    engine: ModelEngine,
    model_name: str,
    version: Optional[str] = None
) -> Any:
    """Load model into memory."""
    try:
        model = await engine.load_model(model_name, version)
        return model
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {str(e)}")
        raise

async def generate_embeddings(
    model: Any,
    texts: List[str],
    batch_size: int = 32
) -> List[List[float]]:
    """Generate embeddings for texts in batches."""
    if not texts:
        return []
        
    try:
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await model.generate_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
        return all_embeddings
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        raise
