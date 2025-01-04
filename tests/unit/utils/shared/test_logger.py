"""Unit tests for the logger utility module."""

import pytest
import logging
import os
from app.utils.shared.logger import setup_logging, get_logger

def test_setup_logging_creates_directory(tmp_path):
    """Test that setup_logging creates the log directory if it doesn't exist."""
    # Arrange
    test_log_dir = tmp_path / "logs"
    test_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": str(test_log_dir / "test.log"),
                "formatter": "simple"
            }
        },
        "root": {
            "handlers": ["file"],
            "level": "DEBUG"
        },
        "loggers": {
            "": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": True
            }
        }
    }

    # Act
    setup_logging(test_config)

    # Assert
    assert test_log_dir.exists()

def test_setup_logging_no_loggers(tmp_path):
    """Test setup_logging with a config that has no loggers section."""
    # Arrange
    test_log_dir = tmp_path / "logs"
    test_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": str(test_log_dir / "test.log"),
                "formatter": "simple"
            }
        },
        "root": {
            "handlers": ["file"],
            "level": "DEBUG"
        }
    }

    # Act
    setup_logging(test_config)
    logger = get_logger("test_logger")
    logger.debug("Test message")
    
    # Ensure all handlers are flushed
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Assert
    assert test_log_dir.exists()
    with open(test_log_dir / "test.log") as f:
        content = f.read().strip()
    assert "Test message" in content

def test_setup_logging_no_root_logger(tmp_path):
    """Test setup_logging with a config that has no root logger in loggers section."""
    # Arrange
    test_log_dir = tmp_path / "logs"
    test_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": str(test_log_dir / "test.log"),
                "formatter": "simple"
            }
        },
        "root": {
            "handlers": ["file"],
            "level": "DEBUG"
        },
        "loggers": {
            "test": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": True
            }
        }
    }

    # Act
    setup_logging(test_config)
    logger = get_logger("test_logger")
    logger.debug("Test message")
    
    # Ensure all handlers are flushed
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Assert
    assert test_log_dir.exists()
    with open(test_log_dir / "test.log") as f:
        content = f.read().strip()
    assert "Test message" in content

def test_get_logger_returns_logger():
    """Test that get_logger returns a Logger instance."""
    # Act
    logger = get_logger("test_logger")

    # Assert
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

def test_logger_writes_to_file(tmp_path):
    """Test that logger properly writes to the log file."""
    # Arrange
    test_log_file = tmp_path / "test.log"
    test_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "test_handler": {
                "class": "logging.FileHandler",
                "filename": str(test_log_file),
                "formatter": "simple",
                "level": "INFO"
            }
        },
        "root": {
            "handlers": ["test_handler"],
            "level": "INFO"
        },
        "loggers": {
            "": {
                "handlers": ["test_handler"],
                "level": "INFO",
                "propagate": True
            }
        }
    }

    # Act
    setup_logging(test_config)
    logger = get_logger("test_logger")
    test_message = "Test log message"
    logger.info(test_message)
    
    # Ensure all handlers are flushed
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Assert
    assert test_log_file.exists()
    with open(test_log_file) as f:
        content = f.read().strip()
    assert content == test_message

def test_logger_respects_log_level(tmp_path):
    """Test that logger respects the configured log level."""
    # Arrange
    test_log_file = tmp_path / "test.log"
    test_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "test_handler": {
                "class": "logging.FileHandler",
                "filename": str(test_log_file),
                "formatter": "simple",
                "level": "INFO"
            }
        },
        "root": {
            "handlers": ["test_handler"],
            "level": "INFO"
        },
        "loggers": {
            "": {
                "handlers": ["test_handler"],
                "level": "INFO",
                "propagate": True
            }
        }
    }

    # Act
    setup_logging(test_config)
    logger = get_logger("test_logger")
    debug_message = "Debug message"
    info_message = "Info message"
    logger.debug(debug_message)
    logger.info(info_message)
    
    # Ensure all handlers are flushed
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Assert
    with open(test_log_file) as f:
        content = f.read()
    assert debug_message not in content  # DEBUG message shouldn't be logged
    assert info_message in content  # INFO message should be logged
