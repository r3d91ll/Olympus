"""Model monitoring implementation."""
import time
from contextlib import contextmanager
from typing import Generator

from prometheus_client import Counter

class ModelMonitor:
    """Monitor for tracking model usage."""
    
    def __init__(self) -> None:
        """Initialize model monitor."""
        self.inference_counter = Counter(
            'model_inference_count',
            'Number of model inferences',
            ['model_name']
        )
        self.error_counter = Counter(
            'model_inference_errors',
            'Number of model inference errors',
            ['model_name']
        )
        
    @contextmanager
    def track_inference(self, model_name: str) -> Generator[None, None, None]:
        """Track model inference.
        
        Args:
            model_name: Name of model being used
            
        Yields:
            None
        """
        try:
            yield
            self.inference_counter.labels(model_name=model_name).inc()
        except Exception as e:
            self.error_counter.labels(model_name=model_name).inc()
            raise