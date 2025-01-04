"""Inference utility for model operations.

This module handles all model inference operations, providing a clean interface
for model interactions while maintaining separation from business logic.
"""

from typing import Dict, Any, Optional, List
from ..shared.logger import get_logger
from ..shared.types import Message, ModelConfig
from .model_utils import ModelClient, LMStudioClient

logger = get_logger(__name__)

class InferenceManager:
    """Manages model inference operations."""
    
    def __init__(self, model_client: Optional[ModelClient] = None):
        """Initialize the inference manager.
        
        Args:
            model_client: Optional model client instance. If None, uses LMStudioClient.
        """
        self.model_client = model_client or LMStudioClient()
        self._current_config: Optional[ModelConfig] = None
    
    async def initialize(self, config: ModelConfig) -> bool:
        """Initialize the inference manager with model configuration.
        
        Args:
            config: Model configuration settings
            
        Returns:
            bool: True if initialization was successful
        """
        try:
            model_info = await self.model_client.get_model_info()
            if "error" in model_info:
                logger.error(f"Failed to initialize model: {model_info['error']}")
                return False
                
            self._current_config = config
            logger.info(f"Initialized inference manager with model {config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize inference manager: {e}")
            return False
    
    async def generate_response(self, 
                              messages: List[Message], 
                              config: Optional[ModelConfig] = None) -> Optional[str]:
        """Generate a response from the model.
        
        Args:
            messages: List of conversation messages
            config: Optional configuration override
            
        Returns:
            Generated response or None if generation failed
        """
        try:
            if not self._current_config and not config:
                logger.error("No model configuration available")
                return None
                
            config = config or self._current_config
            
            # Format messages into prompt
            prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
            
            response = await self.model_client.generate(prompt, config)
            if response.startswith("Error:"):
                logger.error(f"Model generation error: {response}")
                return None
                
            logger.debug("Successfully generated model response")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return None
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and information.
        
        Returns:
            Dictionary containing model status information
        """
        try:
            info = await self.model_client.get_model_info()
            return {
                "status": "active" if not info.get("error") else "error",
                "config": self._current_config.__dict__ if self._current_config else None,
                "info": info
            }
        except Exception as e:
            logger.error(f"Failed to get model status: {e}")
            return {"status": "error", "error": str(e)}
