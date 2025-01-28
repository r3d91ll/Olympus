import pytest
from olympus.model_engine import ModelEngine, ModelRegistry, InferenceEngine

def test_imports():
    assert isinstance(ModelEngine, type)
    assert isinstance(ModelRegistry, type)
    assert isinstance(InferenceEngine, type)