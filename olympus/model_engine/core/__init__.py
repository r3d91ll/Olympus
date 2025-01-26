"""Core model engine package.

This package provides the main model engine functionality for Olympus.
As the system grows, this package will include:
- Model Engine: Primary interface for model operations
- Engine Factory: For creating specialized engine instances
- Engine Config: For managing engine configuration
- Engine Types: Support for different model types and architectures
"""

from olympus.model_engine.core.engine import ModelEngine

__all__ = ["ModelEngine"]