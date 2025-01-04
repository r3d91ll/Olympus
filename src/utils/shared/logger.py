"""Centralized logging utility for the Olympus project.

This module provides a consistent logging interface across all components of the application.
It ensures that all logs are properly formatted and directed to appropriate outputs.
"""

import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Constants
LOGS_DIR = Path("logs")
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "INFO"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "olympus_debug.log"),
            "formatter": "detailed",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG"
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True
        }
    }
}

def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """Setup logging configuration.
    
    Args:
        config: Optional custom logging configuration. If None, uses default config.
    """
    if config is None:
        config = LOG_CONFIG
    
    # Ensure log directory exists for all file handlers
    for handler in config.get("handlers", {}).values():
        if handler.get("class") == "logging.FileHandler":
            log_dir = os.path.dirname(handler["filename"])
            os.makedirs(log_dir, exist_ok=True)
    
    # Reset any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Ensure there's a root logger configuration
    if "loggers" not in config:
        config["loggers"] = {}
    if "" not in config["loggers"]:
        config["loggers"][""] = {
            "handlers": config["root"]["handlers"],
            "level": config["root"]["level"],
            "propagate": True
        }
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Name for the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    return logger

# Initialize logging on module import
setup_logging()
