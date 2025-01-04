"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from typing import Dict, Any
from src_new.utils.shared.types import ModelConfig

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_model_client():
    """Create a mock model client for testing."""
    class MockModelClient:
        async def generate(self, prompt: str, config: ModelConfig) -> str:
            return "Mock response"
            
        async def get_model_info(self) -> Dict[str, Any]:
            return {"model": "mock-model", "status": "ready"}
    
    return MockModelClient()

@pytest.fixture
def sample_model_config():
    """Create a sample model configuration for testing."""
    return ModelConfig(
        name="test-model",
        temperature=0.7,
        max_tokens=100
    )
