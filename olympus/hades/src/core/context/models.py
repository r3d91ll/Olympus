"""Models for context analysis and memory allocation."""

from typing import Dict, List, Literal
from pydantic import BaseModel, Field

class ContextMetadata(BaseModel):
    """Metadata for context analysis."""
    tokens: List[str] = Field(default_factory=list)
    semantics: Dict[str, float] = Field(default_factory=dict)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    last_access: float = 0.0
    access_count: int = 0
    relevance_score: float = 0.0
    
    class Config:
        frozen = True  # Immutable to prevent accidental modifications

class AnalysisResult(BaseModel):
    """Result of context analysis."""
    metadata: ContextMetadata
    suggested_tier: Literal["elysium", "asphodel", "tartarus", "lethe"]
    priority: Literal["high", "medium", "low"] = "medium"
    ttl: int = 3600  # Time-to-live in seconds
    
    class Config:
        frozen = True
