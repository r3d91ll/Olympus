"""Model engine configuration."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
MODEL_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# Model storage structure
MODEL_STORAGE = {
    "base": MODEL_DIR,
    "downloads": MODEL_DIR / "downloads",  # Raw model files from HF
    "optimized": MODEL_DIR / "optimized",  # Optimized versions (e.g., quantized)
    "cache": CACHE_DIR / "models",  # Fast-access cache
}

# Ensure directories exist
for path in MODEL_STORAGE.values():
    path.mkdir(parents=True, exist_ok=True)

# Environment variable to override HF cache
os.environ["HF_HOME"] = str(MODEL_STORAGE["downloads"])
os.environ["TRANSFORMERS_CACHE"] = str(MODEL_STORAGE["downloads"])
