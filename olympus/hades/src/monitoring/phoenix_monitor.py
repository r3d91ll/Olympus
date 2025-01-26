from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import json
from pathlib import Path
import asyncio
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, write_to_textfile

class PhoenixMonitor:
    """Phoenix Arize integration for memory system monitoring."""
    
    def __init__(
        self,
        node_exporter_path: str = "/var/lib/node_exporter/textfile",
        metrics_prefix: str = "olympus_hades"
    ):
        self.node_exporter_path = Path(node_exporter_path)
        self.prefix = metrics_prefix
        self.registry = CollectorRegistry()
        
        # Memory usage metrics
        self.memory_usage = Gauge(
            f"{self.prefix}_memory_usage_bytes",
            "Memory usage by tier in bytes",
            ["component", "tier"],
            registry=self.registry
        )
        
        # Operation counters
        self.operations = Counter(
            f"{self.prefix}_operations_total",
            "Total number of memory operations",
            ["component", "operation", "tier"],
            registry=self.registry
        )
        
        # Latency histograms
        self.operation_latency = Histogram(
            f"{self.prefix}_operation_duration_seconds",
            "Operation latency in seconds",
            ["component", "operation", "tier"],
            buckets=[.001, .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0],
            registry=self.registry
        )
        
        # Vector similarity metrics
        self.similarity_scores = Histogram(
            f"{self.prefix}_similarity_score",
            "Distribution of similarity scores",
            ["component", "tier"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99],
            registry=self.registry
        )
        
        # Cache hit ratios
        self.cache_stats = Gauge(
            f"{self.prefix}_cache_ratio",
            "Cache hit/miss ratio",
            ["component", "tier", "status"],
            registry=self.registry
        )
        
        # Graph metrics
        self.graph_metrics = Gauge(
            f"{self.prefix}_graph_info",
            "Memory graph statistics",
            ["component", "metric"],
            registry=self.registry
        )
        
        # Start background metrics writer
        self.should_run = True
        self._start_metrics_writer()
        
    def _start_metrics_writer(self):
        """Start background task to write metrics periodically."""
        async def write_metrics():
            while self.should_run:
                try:
                    # Write metrics to node-exporter directory
                    metrics_file = self.node_exporter_path / f"{self.prefix}_metrics.prom"
                    write_to_textfile(str(metrics_file), self.registry)
                    await asyncio.sleep(15)  # Write every 15 seconds
                except Exception as e:
                    logger.error(f"Error writing metrics: {str(e)}")
                    await asyncio.sleep(30)  # Back off on error
                    
        asyncio.create_task(write_metrics())
        
    def record_memory_usage(self, component: str, tier: str, bytes_used: int):
        """Record memory usage for a tier."""
        self.memory_usage.labels(component=component, tier=tier).set(bytes_used)
        
    def record_operation(self, component: str, operation: str, tier: str):
        """Record a memory operation."""
        self.operations.labels(component=component, operation=operation, tier=tier).inc()
        
    async def time_operation(self, component: str, operation: str, tier: str):
        """Context manager to time operations."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.operation_latency.labels(
                component=component,
                operation=operation,
                tier=tier
            ).observe(duration)
            
    def record_similarity_score(self, component: str, tier: str, score: float):
        """Record a similarity score."""
        self.similarity_scores.labels(component=component, tier=tier).observe(score)
        
    def update_cache_stats(self, component: str, tier: str, hits: int, misses: int):
        """Update cache hit/miss statistics."""
        total = hits + misses
        if total > 0:
            hit_ratio = hits / total
            miss_ratio = misses / total
            self.cache_stats.labels(component=component, tier=tier, status="hit").set(hit_ratio)
            self.cache_stats.labels(component=component, tier=tier, status="miss").set(miss_ratio)
            
    def update_graph_metrics(self, component: str, stats: Dict[str, float]):
        """Update memory graph statistics."""
        for metric, value in stats.items():
            self.graph_metrics.labels(component=component, metric=metric).set(value)
            
    def stop(self):
        """Stop the metrics writer."""
        self.should_run = False
