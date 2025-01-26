"""Test model engine functionality."""
import pytest
from unittest.mock import MagicMock

from olympus.model_engine.core.engine import ModelEngine
from olympus.model_engine.registry import ModelRegistry
from olympus.model_engine.inference import InferenceEngine
from olympus.model_engine.monitoring import ModelMonitor
from tests.model_engine.test_constants import TEST_MODEL

def test_model_registry_search(model_registry: ModelRegistry, mock_huggingface_hub: MagicMock):
    """Test model search functionality."""
    # Setup mock response
    mock_huggingface_hub.list_models.return_value = [
        {"modelId": TEST_MODEL, "tags": ["code-generation"]}
    ]
    
    # Test search
    results = model_registry.search("test")
    assert len(results) > 0
    assert TEST_MODEL in results

def test_model_registry_load(model_registry: ModelRegistry):
    """Test model loading functionality."""
    model = model_registry.get_model(TEST_MODEL)
    assert model.name_or_path == TEST_MODEL

def test_inference_engine_run(inference_engine: InferenceEngine, model_registry: ModelRegistry):
    """Test model inference functionality."""
    # Setup test input
    test_input = "def hello_world():"
    model = model_registry.get_model(TEST_MODEL)
    
    # Test inference
    output = inference_engine.run(
        model=model,
        input_data=test_input
    )
    assert output == "def hello_world():\n    print('Hello World!')"

def test_model_monitor_track(model_monitor: ModelMonitor, mock_monitoring: MagicMock):
    """Test model monitoring functionality."""
    # Setup mock counter
    counter_mock = MagicMock()
    counter_mock.labels.return_value = counter_mock
    mock_monitoring.return_value = counter_mock
    model_monitor.inference_counter = counter_mock
    
    # Test monitoring
    with model_monitor.track_inference(model_name=TEST_MODEL):
        pass  # Simulate work
    
    # Verify monitoring calls
    counter_mock.labels.assert_called_with(model_name=TEST_MODEL)
    counter_mock.inc.assert_called_once()

def test_model_engine_integration(
    model_engine: ModelEngine,
    mock_monitoring: MagicMock
):
    """Test model engine integration."""
    # Test code generation
    output = model_engine.generate_code("Write a hello world function")
    assert output == "def hello_world():\n    print('Hello World!')"
    
    # Verify monitoring was called
    assert mock_monitoring.return_value.labels.called
    assert mock_monitoring.return_value.labels().inc.called
