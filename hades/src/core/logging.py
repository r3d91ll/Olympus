import sys
from loguru import logger
from pathlib import Path
from typing import Dict, Any
import json

from .config import settings

def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Format for console logging
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Format for JSON logging (for Prometheus/Grafana)
    json_format = lambda record: json.dumps({
        "timestamp": record["time"].timestamp(),
        "level": record["level"].name,
        "message": record["message"],
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "memory_stats": {
            "elysium_size": record["extra"].get("elysium_size", 0),
            "asphodel_size": record["extra"].get("asphodel_size", 0),
            "lethe_size": record["extra"].get("lethe_size", 0)
        },
        "metrics": record["extra"].get("metrics", {})
    })
    
    # Console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        colorize=True
    )
    
    # JSON file handler for metrics
    log_path = Path("logs/metrics")
    log_path.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_path / "hades_metrics.json"),
        format=json_format,
        level="INFO",
        rotation="1 day",
        retention="7 days",
        filter=lambda record: "metrics" in record["extra"]
    )
    
    # Error file handler
    error_path = Path("logs/errors")
    error_path.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(error_path / "error.log"),
        format=console_format,
        level="ERROR",
        rotation="1 day",
        retention="30 days"
    )

def log_memory_stats(
    elysium_size: int = 0,
    asphodel_size: int = 0,
    lethe_size: int = 0,
    metrics: Dict[str, Any] = None
):
    """Log memory statistics for monitoring."""
    logger.bind(
        elysium_size=elysium_size,
        asphodel_size=asphodel_size,
        lethe_size=lethe_size,
        metrics=metrics or {}
    ).info("Memory statistics updated")
