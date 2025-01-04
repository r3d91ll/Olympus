"""Common type definitions used across the application."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class Message(BaseModel):
    """A chat message."""
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ModelConfig(BaseModel):
    """Model configuration settings."""
    name: str
    temperature: float = 0.7
    max_tokens: int = 100
    parameters: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    valid: bool
    errors: List[str] = []
