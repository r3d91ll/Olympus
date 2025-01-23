from pydantic import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HADES"
    
    # Database Settings
    ARANGO_HOST: str = "localhost"
    ARANGO_PORT: int = 8529
    ARANGO_DB: str = "hades"
    ARANGO_USER: str = "root"
    ARANGO_PASSWORD: Optional[str] = None
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Memory Management Settings
    ELYSIUM_MAX_SIZE: int = 1024 * 1024 * 1024  # 1GB
    ASPHODEL_MAX_SIZE: int = 10 * 1024 * 1024 * 1024  # 10GB
    ASPHODEL_WINDOW_SIZE: int = 1000  # Number of items
    TARTARUS_RELEVANCE_THRESHOLD: float = 0.2
    LETHE_PROMOTION_THRESHOLD: float = 0.5
    
    # Vector Store Settings
    VECTOR_DIMENSION: int = 768  # Dimension of vectors (e.g., for BERT embeddings)
    VECTOR_SIMILARITY: str = "euclidean"  # or "cosine"
    VECTOR_INDEX_TYPE: str = "faiss"
    
    # Embedding Model Settings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_POOLING: str = "mean"
    EMBEDDING_CACHE_SIZE: int = 1024
    
    # HuggingFace Settings
    HF_TOKEN: Optional[str] = None
    HF_MODEL_CACHE_DIR: Path = Path("cache/models")
    HF_CONFIG_CACHE_DIR: Path = Path("cache/configs")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
