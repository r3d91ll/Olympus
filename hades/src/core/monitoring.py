"""Monitoring utilities for HADES."""
from typing import Callable
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry
)
import time
from loguru import logger

# Create a new registry
REGISTRY = CollectorRegistry(auto_describe=True)

# Request metrics
REQUEST_COUNT = Counter(
    "hades_request_count",
    "Number of requests received",
    ["method", "endpoint", "status"],
    registry=REGISTRY
)

REQUEST_LATENCY = Histogram(
    "hades_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    registry=REGISTRY
)

# RAG metrics
QUERY_COUNT = Counter(
    "hades_rag_query_count",
    "Number of RAG queries processed",
    ["status"],
    registry=REGISTRY
)

QUERY_LATENCY = Histogram(
    "hades_rag_query_latency_seconds",
    "RAG query latency in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf")],
    registry=REGISTRY
)

DOCUMENT_COUNT = Gauge(
    "hades_document_count",
    "Number of documents in the system",
    registry=REGISTRY
)

EMBEDDING_LATENCY = Histogram(
    "hades_embedding_latency_seconds",
    "Time taken to generate embeddings",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
    registry=REGISTRY
)

CONTEXT_LENGTH = Histogram(
    "hades_context_length_chars",
    "Length of retrieved context in characters",
    buckets=[100, 500, 1000, 2000, 5000],
    registry=REGISTRY
)

MODEL_INFERENCE_LATENCY = Histogram(
    "hades_model_inference_latency_seconds",
    "Time taken for model inference",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
    registry=REGISTRY
)

# GPU metrics
GPU_MEMORY_USAGE = Gauge(
    "hades_gpu_memory_usage_bytes",
    "GPU memory usage in bytes",
    ["device"],
    registry=REGISTRY
)

GPU_UTILIZATION = Gauge(
    "hades_gpu_utilization_percent",
    "GPU utilization percentage",
    ["device"],
    registry=REGISTRY
)

async def metrics_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    """Middleware to collect request metrics."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record request duration
    duration = time.time() - start_time
    
    # Extract endpoint pattern
    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)
    
    return response

async def update_gpu_metrics():
    """Update GPU metrics."""
    try:
        import torch
        if not torch.cuda.is_available():
            return
            
        for i in range(torch.cuda.device_count()):
            memory_allocated = torch.cuda.memory_allocated(i)
            memory_reserved = torch.cuda.memory_reserved(i)
            
            GPU_MEMORY_USAGE.labels(device=f"cuda:{i}").set(
                memory_allocated
            )
            
            # Get GPU utilization using nvidia-smi
            import subprocess
            try:
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        f"--query-gpu=utilization.gpu",
                        "--format=csv,noheader,nounits"
                    ],
                    capture_output=True,
                    text=True
                )
                utilization = float(result.stdout.strip())
                GPU_UTILIZATION.labels(device=f"cuda:{i}").set(
                    utilization
                )
            except Exception as e:
                logger.warning(f"Failed to get GPU utilization: {e}")
                
    except Exception as e:
        logger.warning(f"Failed to update GPU metrics: {e}")

def init_monitoring(app: FastAPI):
    """Initialize monitoring for FastAPI app."""
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics():
        await update_gpu_metrics()
        return Response(
            generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Add middleware
    app.middleware("http")(metrics_middleware)
