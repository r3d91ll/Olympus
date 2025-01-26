"""Core model engine implementation."""
from typing import Optional

from olympus.model_engine.registry import ModelRegistry
from olympus.model_engine.inference import InferenceEngine
from olympus.model_engine.monitoring import ModelMonitor


class ModelEngine:
    """Main model engine class for managing model operations.
    
    This class serves as the primary interface for model operations including:
    - Model inference and code generation
    - Model registry management
    - Usage monitoring and metrics tracking
    
    As the engine grows, it will support:
    - Different model types (language, vision, multi-modal)
    - Various inference patterns (streaming, batched)
    - Advanced monitoring and telemetry
    - Model versioning and lifecycle management
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        inference: InferenceEngine,
        monitor: ModelMonitor
    ) -> None:
        """Initialize model engine.
        
        Args:
            registry: Registry for model management
            inference: Engine for running inference
            monitor: Monitor for tracking model usage
        """
        self._registry = registry
        self._inference = inference
        self._monitor = monitor

    def run(self, model_name: str, input_data: str) -> str:
        """Run inference on input data.
        
        Args:
            model_name: Name of model to use
            input_data: Input data for inference
            
        Returns:
            Model output
        """
        with self._monitor.track_inference(model_name=model_name):
            model = self._registry.get_model(model_name)
            return self._inference.run(model=model, input_data=input_data)

    def generate_code(self, prompt: str, model_name: Optional[str] = None) -> str:
        """Generate code from prompt.
        
        Args:
            prompt: Input prompt
            model_name: Optional model name to use, defaults to configured default
            
        Returns:
            Generated code
        """
        model = self._registry.get_model(model_name) if model_name else self._registry.get_default_model()
        
        with self._monitor.track_inference(model_name=model.name_or_path):
            return self._inference.run(model=model, input_data=prompt)
