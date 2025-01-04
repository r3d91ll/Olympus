"""Tests for inference utilities."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src_new.utils.backend.inference import InferenceManager
from src_new.utils.shared.types import Message, ModelConfig

@pytest.fixture
def mock_model_client():
    """Create a mock model client."""
    client = AsyncMock()
    client.get_model_info = AsyncMock(return_value={"model": "test-model"})
    client.generate = AsyncMock(return_value="test response")
    return client

@pytest.fixture
def test_config():
    """Create a test model configuration."""
    return ModelConfig(
        name="test-model",
        temperature=0.7,
        max_tokens=100
    )

@pytest.mark.asyncio
async def test_initialize_success(mock_model_client, test_config):
    """Test successful initialization."""
    manager = InferenceManager(mock_model_client)
    result = await manager.initialize(test_config)
    assert result is True
    mock_model_client.get_model_info.assert_called_once()

@pytest.mark.asyncio
async def test_initialize_failure(mock_model_client, test_config):
    """Test initialization failure."""
    mock_model_client.get_model_info = AsyncMock(return_value={"error": "test error"})
    manager = InferenceManager(mock_model_client)
    result = await manager.initialize(test_config)
    assert result is False

@pytest.mark.asyncio
async def test_initialize_exception(mock_model_client, test_config):
    """Test initialization with exception."""
    mock_model_client.get_model_info = AsyncMock(side_effect=Exception("test error"))
    manager = InferenceManager(mock_model_client)
    result = await manager.initialize(test_config)
    assert result is False

@pytest.mark.asyncio
async def test_generate_response_success(mock_model_client, test_config):
    """Test successful response generation."""
    manager = InferenceManager(mock_model_client)
    await manager.initialize(test_config)
    
    messages = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi")
    ]
    
    response = await manager.generate_response(messages)
    assert response == "test response"
    mock_model_client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_generate_response_no_config(mock_model_client):
    """Test response generation without configuration."""
    manager = InferenceManager(mock_model_client)
    messages = [Message(role="user", content="Hello")]
    response = await manager.generate_response(messages)
    assert response is None

@pytest.mark.asyncio
async def test_generate_response_with_config_override(mock_model_client, test_config):
    """Test response generation with config override."""
    manager = InferenceManager(mock_model_client)
    
    messages = [Message(role="user", content="Hello")]
    override_config = ModelConfig(name="override-model", temperature=0.5, max_tokens=50)
    
    response = await manager.generate_response(messages, override_config)
    assert response == "test response"
    mock_model_client.generate.assert_called_once()

@pytest.mark.asyncio
async def test_generate_response_error(mock_model_client, test_config):
    """Test response generation with error."""
    mock_model_client.generate = AsyncMock(return_value="Error: test error")
    manager = InferenceManager(mock_model_client)
    await manager.initialize(test_config)
    
    messages = [Message(role="user", content="Hello")]
    response = await manager.generate_response(messages)
    assert response is None

@pytest.mark.asyncio
async def test_generate_response_exception(mock_model_client, test_config):
    """Test response generation with exception."""
    mock_model_client.generate = AsyncMock(side_effect=Exception("test error"))
    manager = InferenceManager(mock_model_client)
    await manager.initialize(test_config)
    
    messages = [Message(role="user", content="Hello")]
    response = await manager.generate_response(messages)
    assert response is None

@pytest.mark.asyncio
async def test_get_model_status_success(mock_model_client, test_config):
    """Test successful model status retrieval."""
    manager = InferenceManager(mock_model_client)
    await manager.initialize(test_config)
    
    status = await manager.get_model_status()
    assert status["status"] == "active"
    assert status["config"] == test_config.__dict__
    assert status["info"] == {"model": "test-model"}

@pytest.mark.asyncio
async def test_get_model_status_error(mock_model_client):
    """Test model status retrieval with error."""
    mock_model_client.get_model_info = AsyncMock(return_value={"error": "test error"})
    manager = InferenceManager(mock_model_client)
    
    status = await manager.get_model_status()
    assert status["status"] == "error"

@pytest.mark.asyncio
async def test_get_model_status_exception(mock_model_client):
    """Test model status retrieval with exception."""
    mock_model_client.get_model_info = AsyncMock(side_effect=Exception("test error"))
    manager = InferenceManager(mock_model_client)
    
    status = await manager.get_model_status()
    assert status["status"] == "error"
    assert "test error" in status["error"]

@pytest.mark.asyncio
async def test_get_model_status_not_initialized(mock_model_client):
    """Test model status retrieval when not initialized."""
    manager = InferenceManager(mock_model_client)
    status = await manager.get_model_status()
    assert status["status"] == "active"
    assert status["config"] is None
