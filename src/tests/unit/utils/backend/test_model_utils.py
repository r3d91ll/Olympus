"""Tests for model utilities."""
import pytest
import aiohttp
from unittest.mock import AsyncMock
from aioresponses import aioresponses
from src_new.utils.backend.model_utils import ModelClient, LMStudioClient

@pytest.mark.asyncio
async def test_model_client_context_manager():
    """Test ModelClient context manager functionality."""
    client = ModelClient("test-model", "http://test-url")
    assert client.session is None
    
    async with client:
        assert isinstance(client.session, aiohttp.ClientSession)
        assert not client.session.closed
    
    assert client.session is None

@pytest.mark.asyncio
async def test_model_client_generate_no_session():
    """Test ModelClient generate without session raises error."""
    client = ModelClient("test-model", "http://test-url")
    with pytest.raises(RuntimeError, match="Session not initialized"):
        await client.generate("test prompt")

@pytest.mark.asyncio
async def test_model_client_generate_success():
    """Test ModelClient generate success case."""
    with aioresponses() as m:
        m.post(
            "http://test-url",
            payload={"response": "test response"},
            status=200
        )
        
        async with ModelClient("test-model", "http://test-url") as client:
            response = await client.generate("test prompt")
            assert response == "test response"

@pytest.mark.asyncio
async def test_model_client_generate_failure():
    """Test ModelClient generate failure case."""
    with aioresponses() as m:
        m.post(
            "http://test-url",
            status=500
        )
        
        async with ModelClient("test-model", "http://test-url") as client:
            with pytest.raises(RuntimeError, match="Failed to generate response"):
                await client.generate("test prompt")

def test_lm_studio_client_init():
    """Test LMStudioClient initialization."""
    client = LMStudioClient("test-model")
    assert client.model_name == "test-model"
    assert client.api_url == "http://localhost:1234/v1/completions"
    
    custom_url = "http://custom-url"
    client = LMStudioClient("test-model", custom_url)
    assert client.api_url == custom_url
