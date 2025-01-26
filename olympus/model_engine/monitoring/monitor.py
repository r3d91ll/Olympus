"""Model monitoring integration with Ladon."""
from contextlib import contextmanager
import time
from typing import Any, Dict, Generator
from prometheus_client import Counter, Histogram, Gauge

class ModelMonitor:
    """Monitor model performance and integrate with Ladon monitoring stack."""
    
    def __init__(self):
        """Initialize monitoring metrics."""
        # Prometheus metrics
        self.inference_count = Counter(
            'model_inference_total',
            'Total number of model inferences',
            ['model_name']
        )
        
        self.inference_latency = Histogram(
            'model_inference_latency_seconds',
            'Model inference latency in seconds',
            ['model_name']
        )
        
        self.error_count = Counter(
            'model_error_total',
            'Total number of model errors',
            ['model_name', 'error_type']
        )
        
        self.memory_usage = Gauge(
            'model_memory_bytes',
            'Model memory usage in bytes',
            ['model_name']
        )
        
        self.cache_hits = Counter(
            'model_cache_hits_total',
            'Total number of cache hits',
            ['model_name']
        )
        
        self.cache_misses = Counter(
            'model_cache_misses_total',
            'Total number of cache misses',
            ['model_name']
        )
    
    def register_model(self, model: Any) -> None:
        """Register a new model for monitoring.
        
        Args:
            model: Model instance to monitor
        """
        model_name = getattr(model, 'name', str(model))
        self.memory_usage.labels(model_name=model_name).set(0)
    
    @contextmanager
    def track_inference(self, model_name: str) -> Generator[None, None, None]:
        """Track model inference performance.
        
        Args:
            model_name: Name of the model being monitored
            
        Yields:
            None
        """
        start_time = time.time()
        try:
            yield
            self.inference_count.labels(model_name=model_name).inc()
        except Exception as e:
            self.error_count.labels(
                model_name=model_name,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            self.inference_latency.labels(model_name=model_name).observe(duration)
    
    def track_memory(self, model_name: str, memory_bytes: int) -> None:
        """Track model memory usage.
        
        Args:
            model_name: Name of the model
            memory_bytes: Memory usage in bytes
        """
        self.memory_usage.labels(model_name=model_name).set(memory_bytes)
    
    def track_cache(self, model_name: str, hit: bool) -> None:
        """Track cache performance.
        
        Args:
            model_name: Name of the model
            hit: Whether the cache lookup was a hit
        """
        if hit:
            self.cache_hits.labels(model_name=model_name).inc()
        else:
            self.cache_misses.labels(model_name=model_name).inc()
