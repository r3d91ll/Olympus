"""Tests for configuration module."""
import os
from pathlib import Path
import pytest
from app.utils.shared.config import (
    BASE_DIR,
    LOGS_DIR,
    RAMDISK_DIR,
    MODELS_DIR,
    DEFAULT_MODEL_CONFIG,
    LOG_CONFIG
)

def test_base_directories():
    """Test base directory paths are set correctly."""
    assert isinstance(BASE_DIR, Path)
    assert isinstance(LOGS_DIR, Path)
    assert isinstance(RAMDISK_DIR, Path)
    assert isinstance(MODELS_DIR, Path)
    
    # Test relative paths
    assert LOGS_DIR.parent == BASE_DIR
    assert MODELS_DIR.parent == BASE_DIR
    assert str(RAMDISK_DIR) == "ramdisk"

def test_directory_creation():
    """Test required directories are created."""
    assert LOGS_DIR.exists()
    assert LOGS_DIR.is_dir()
    assert MODELS_DIR.exists()
    assert MODELS_DIR.is_dir()

def test_model_config():
    """Test default model configuration."""
    assert isinstance(DEFAULT_MODEL_CONFIG, dict)
    assert DEFAULT_MODEL_CONFIG["temperature"] == 0.7
    assert DEFAULT_MODEL_CONFIG["max_tokens"] == 150

def test_log_config():
    """Test logging configuration."""
    assert isinstance(LOG_CONFIG, dict)
    assert LOG_CONFIG["version"] == 1
    assert not LOG_CONFIG["disable_existing_loggers"]
    
    # Test formatters
    formatters = LOG_CONFIG["formatters"]
    assert "standard" in formatters
    assert "format" in formatters["standard"]
    
    # Test handlers
    handlers = LOG_CONFIG["handlers"]
    assert "default" in handlers
    assert "file" in handlers
    
    # Test default handler config
    default_handler = handlers["default"]
    assert default_handler["level"] == "INFO"
    assert default_handler["formatter"] == "standard"
    assert default_handler["class"] == "logging.StreamHandler"
    
    # Test file handler config
    file_handler = handlers["file"]
    assert file_handler["level"] == "DEBUG"
    assert file_handler["formatter"] == "standard"
    assert file_handler["class"] == "logging.FileHandler"
    assert file_handler["filename"] == str(LOGS_DIR / "olympus_debug.log")
    
    # Test loggers
    loggers = LOG_CONFIG["loggers"]
    assert "" in loggers  # Root logger
    root_logger = loggers[""]
    assert set(root_logger["handlers"]) == {"default", "file"}
    assert root_logger["level"] == "DEBUG"
    assert root_logger["propagate"] is True
