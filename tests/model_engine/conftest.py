"""Test fixtures for model engine."""
import pytest
from unittest.mock import MagicMock, patch

from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi

from olympus.model_engine.core.engine import ModelEngine
from olympus.model_engine.registry import ModelRegistry
from olympus.model_engine.inference import InferenceEngine
from olympus.model_engine.monitoring import ModelMonitor
from tests.model_engine.test_constants import TEST_MODEL

@pytest.fixture
def mock_model():
    """Mock transformer model."""
    model = MagicMock()
    model.name_or_path = TEST_MODEL
    model.generate.return_value = [[1, 2, 3, 4]]  # Mock token IDs
    return model

@pytest.fixture
def mock_tokenizer():
    """Mock transformer tokenizer."""
    tokenizer = MagicMock()
    tokenizer.name_or_path = TEST_MODEL
    tokenizer.encode.return_value = [1, 2, 3]
    tokenizer.decode.return_value = "def hello_world():\n    print('Hello World!')"
    tokenizer.pad_token = "[PAD]"
    tokenizer.pad_token_id = 0
    tokenizer.__call__ = MagicMock(return_value={"input_ids": [[1, 2, 3]]})
    return tokenizer

@pytest.fixture
def mock_huggingface_hub():
    """Mock huggingface hub."""
    hub = MagicMock(spec=HfApi)
    hub.list_models.return_value = [{"modelId": TEST_MODEL, "tags": ["code-generation"]}]
    return hub

@pytest.fixture
def mock_monitoring():
    """Mock prometheus monitoring."""
    counter = MagicMock()
    counter.labels.return_value = counter
    mock = MagicMock()
    mock.return_value = counter
    return mock

@pytest.fixture
def model_registry(mock_model, mock_tokenizer, mock_huggingface_hub):
    """Create model registry instance."""
    with patch("transformers.AutoModelForCausalLM.from_pretrained", return_value=mock_model), \
         patch("transformers.AutoTokenizer.from_pretrained", return_value=mock_tokenizer), \
         patch("huggingface_hub.HfApi", return_value=mock_huggingface_hub):
        registry = ModelRegistry()
        registry.search = MagicMock(return_value=[TEST_MODEL])  # Add search method
        return registry

@pytest.fixture
def inference_engine(mock_model, mock_tokenizer):
    """Create inference engine instance."""
    with patch("transformers.AutoModelForCausalLM.from_pretrained", return_value=mock_model), \
         patch("transformers.AutoTokenizer.from_pretrained", return_value=mock_tokenizer):
        engine = InferenceEngine()
        return engine

@pytest.fixture
def model_monitor(mock_monitoring):
    """Create model monitor instance."""
    with patch("prometheus_client.Counter", mock_monitoring):
        monitor = ModelMonitor()
        monitor.inference_counter = mock_monitoring.return_value  # Set counter directly
        return monitor

@pytest.fixture
def model_engine(model_registry, inference_engine, model_monitor):
    """Create model engine instance."""
    return ModelEngine(
        registry=model_registry,
        inference=inference_engine,
        monitor=model_monitor
    )
