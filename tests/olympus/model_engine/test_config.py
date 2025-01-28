import pytest
from olympus.model_engine.config import MODEL_STORAGE

def test_model_storage():
    assert isinstance(MODEL_STORAGE, dict)
    assert "base" in MODEL_STORAGE
    assert "downloads" in MODEL_STORAGE
    assert "optimized" in MODEL_STORAGE
    assert "cache" in MODEL_STORAGE

    base_path = MODEL_STORAGE["base"]
    downloads_path = MODEL_STORAGE["downloads"]
    optimized_path = MODEL_STORAGE["optimized"]
    cache_path = MODEL_STORAGE["cache"]

    assert base_path.exists()
    assert downloads_path.exists()
    assert optimized_path.exists()
    assert cache_path.exists()