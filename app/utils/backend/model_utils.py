"""Model client utilities for the Olympus project."""
import aiohttp
from typing import Dict, Any, Optional

class ModelClient:
    """Base class for model clients."""
    
    def __init__(self, model_name: str, api_url: str):
        """Initialize the model client.
        
        Args:
            model_name: Name of the model to use.
            api_url: URL of the model API endpoint.
        """
        self.model_name = model_name
        self.api_url = api_url
        self.session = None

    async def __aenter__(self):
        """Create and return an aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: Input prompt for the model.
            config: Optional model configuration parameters.
            
        Returns:
            Generated response from the model.
            
        Raises:
            RuntimeError: If the session is not initialized or request fails.
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with context.")
            
        try:
            async with self.session.post(
                self.api_url,
                json={"prompt": prompt, "config": config or {}}
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result["response"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")

class LMStudioClient(ModelClient):
    """Client for LM Studio API."""
    
    def __init__(self, model_name: str, api_url: str = "http://localhost:1234/v1/completions"):
        """Initialize the LM Studio client.
        
        Args:
            model_name: Name of the model to use.
            api_url: URL of the LM Studio API endpoint.
        """
        super().__init__(model_name, api_url)
