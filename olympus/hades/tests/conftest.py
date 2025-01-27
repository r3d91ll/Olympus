"""Test configuration for HADES."""
import sys
from typing import AsyncGenerator, Generator, Any
from unittest.mock import Mock, AsyncMock, patch

import pytest
import pytest_asyncio
import asyncio

# Mock model_engine at package level
mock_model_engine = Mock()
mock_model_engine.ModelEngine = Mock()

@pytest.fixture(autouse=True)
def mock_model_engine_import():
    """Mock model_engine package for all tests."""
    with patch.dict(sys.modules, {'olympus.model_engine': mock_model_engine}):
        yield

@pytest_asyncio.fixture
async def mock_monitor() -> AsyncGenerator[Any, None]:
    """Mock PhoenixMonitor."""
    monitor = AsyncMock()
    monitor.record_metric.return_value = None
    yield monitor

@pytest_asyncio.fixture
async def mock_store() -> AsyncGenerator[Any, None]:
    """Mock ArangoMemoryStore."""
    store = AsyncMock()
    store.store_memory.return_value = None
    store.find_similar_memories.return_value = [
        {
            "content": "test content",
            "similarity": 0.9,
            "metadata": {
                "file_name": "test.txt",
                "file_size": 100,
                "file_type": ".txt"
            }
        }
    ]
    yield store

@pytest_asyncio.fixture
async def mock_model() -> AsyncGenerator[Any, None]:
    """Mock embedding model."""
    model = AsyncMock()
    model.encode.return_value = [[0.1, 0.2, 0.3]]
    yield model

@pytest_asyncio.fixture
async def mock_engine() -> AsyncGenerator[Any, None]:
    """Mock model engine."""
    engine = AsyncMock()
    engine.list_models.return_value = [
        {
            "name": "test-model",
            "version": "1.0.0",
            "type": "encoder",
            "embedding_dim": 768
        }
    ]
    engine.download_model.return_value = None
    engine.load_model.return_value = None
    engine.generate_embeddings.return_value = [[1.0] * 768]
    yield engine

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
