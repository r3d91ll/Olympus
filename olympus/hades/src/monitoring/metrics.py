from prometheus_client import Gauge, Counter, start_http_server
from typing import Dict, Any
import json
from pathlib import Path
import time
from loguru import logger

class HADESMetricsExporter:
    def __init__(self, metrics_port: int = 9400):
        self.metrics_port = metrics_port
        
        # Memory metrics
        self.elysium_size = Gauge(
            'hades_elysium_size_bytes',
            'Current size of Elysium tier in bytes'
        )
        self.asphodel_size = Gauge(
            'hades_asphodel_size_bytes',
            'Current size of Asphodel tier in bytes'
        )
        self.lethe_size = Gauge(
            'hades_lethe_size_bytes',
            'Current size of Lethe tier in bytes'
        )
        
        # Operation metrics
        self.memory_utilization = Gauge(
            'hades_memory_utilization_percent',
            'Memory utilization percentage across tiers'
        )
        self.operations_total = Counter(
            'hades_operations_total',
            'Total number of operations',
            ['operation', 'tier']
        )
        
        # Performance metrics
        self.operation_duration = Gauge(
            'hades_operation_duration_seconds',
            'Duration of operations in seconds',
            ['operation']
        )
        
    def start(self):
        """Start the Prometheus metrics server."""
        start_http_server(self.metrics_port)
        logger.info(f"Started HADES metrics server on port {self.metrics_port}")
        
    def update_metrics(self, metrics_file: Path):
        """Update metrics from the JSON log file."""
        try:
            if not metrics_file.exists():
                return
                
            with open(metrics_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        memory_stats = data.get('memory_stats', {})
                        metrics = data.get('metrics', {})
                        
                        # Update memory metrics
                        self.elysium_size.set(memory_stats.get('elysium_size', 0))
                        self.asphodel_size.set(memory_stats.get('asphodel_size', 0))
                        self.lethe_size.set(memory_stats.get('lethe_size', 0))
                        
                        # Update utilization
                        self.memory_utilization.set(metrics.get('memory_utilization', 0))
                        
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            
    def record_operation(self, operation: str, tier: str, duration: float):
        """Record an operation and its duration."""
        self.operations_total.labels(operation=operation, tier=tier).inc()
        self.operation_duration.labels(operation=operation).set(duration)

# Global metrics exporter instance
metrics_exporter = HADESMetricsExporter()

def start_metrics_server():
    """Start the metrics server."""
    metrics_exporter.start()
    
def update_metrics():
    """Update metrics from log files."""
    metrics_file = Path("logs/metrics/hades_metrics.json")
    metrics_exporter.update_metrics(metrics_file)
    
def record_operation(operation: str, tier: str, start_time: float):
    """Record an operation and its duration."""
    duration = time.time() - start_time
    metrics_exporter.record_operation(operation, tier, duration)
