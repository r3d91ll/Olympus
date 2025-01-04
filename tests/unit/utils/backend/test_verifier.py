"""Test suite for verifier module."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, PropertyMock
from pydantic import ValidationError
from app.utils.backend.verifier import Verifier
from app.utils.shared.types import Message, ModelConfig, ValidationResult

def test_validate_message_success():
    """Test successful message validation."""
    message = Message(role="user", content="test")
    result = Verifier.validate_message(message)
    assert result.valid
    assert not result.errors

def test_validate_message_invalid_type():
    """Test message validation with invalid type."""
    result = Verifier.validate_message({"role": "user", "content": "test"})
    assert not result.valid
    assert "Input must be a Message object" in result.errors[0]

def test_validate_message_missing_role():
    """Test message validation with missing role."""
    message = Message(role="", content="test")
    result = Verifier.validate_message(message)
    assert not result.valid
    assert "Message must have a valid role string" in result.errors[0]

def test_validate_message_missing_content():
    """Test message validation with missing content."""
    message = Message(role="user", content="")
    result = Verifier.validate_message(message)
    assert not result.valid
    assert "Message must have valid content string" in result.errors[0]

def test_validate_message_validation_error():
    """Test message validation with validation error."""
    message = None
    result = Verifier.validate_message(message)
    assert not result.valid
    assert "Input must be a Message object" in result.errors[0]

def test_validate_message_exception():
    """Test message validation with exception."""
    # Create a mock message that raises an exception when accessing role
    mock_message = Mock(spec=Message)
    type(mock_message).role = PropertyMock(side_effect=Exception("test error"))
    type(mock_message).content = PropertyMock(return_value="test")
    
    result = Verifier.validate_message(mock_message)
    assert not result.valid
    assert "Validation error: test error" in result.errors[0]

def test_validate_model_config_success():
    """Test successful model config validation."""
    config = ModelConfig(name="test", temperature=0.7, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert result.valid
    assert not result.errors

def test_validate_model_config_invalid_type():
    """Test model config validation with invalid type."""
    result = Verifier.validate_model_config({"name": "test"})
    assert not result.valid
    assert "Input must be a ModelConfig object" in result.errors[0]

def test_validate_model_config_temperature_boundary():
    """Test model config validation with boundary temperature values."""
    # Test temperature = 0
    config = ModelConfig(name="test", temperature=0, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert result.valid

    # Test temperature = 1
    config = ModelConfig(name="test", temperature=1, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert result.valid

    # Test temperature = 0.5 (middle value)
    config = ModelConfig(name="test", temperature=0.5, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert result.valid

    # Test temperature = "0.5" (string value)
    config = Mock(spec=ModelConfig)
    config.name = "test"
    config.max_tokens = 100
    config.temperature = "0.5"
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Validation error: '<=' not supported between instances of 'int' and 'str'" in result.errors[0]

    # Test temperature = float('nan')
    config = Mock(spec=ModelConfig)
    config.name = "test"
    config.max_tokens = 100
    config.temperature = float('nan')
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Temperature must be a finite float between 0 and 1" in result.errors[0]

def test_validate_model_config_invalid_temperature():
    """Test model config validation with invalid temperature."""
    config = ModelConfig(name="test", temperature=1.5, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Temperature must be a finite float between 0 and 1" in result.errors[0]

def test_validate_model_config_invalid_temperature_negative():
    """Test model config validation with negative temperature."""
    config = ModelConfig(name="test", temperature=-0.5, max_tokens=100)
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Temperature must be a finite float between 0 and 1" in result.errors[0]

def test_validate_model_config_invalid_temperature_none():
    """Test model config validation with None temperature."""
    config = Mock(spec=ModelConfig)
    config.name = "test"
    config.max_tokens = 100
    config.temperature = None
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Validation error: '<=' not supported between instances of 'int' and 'NoneType'" in result.errors[0]

def test_validate_model_config_invalid_max_tokens():
    """Test model config validation with invalid max_tokens."""
    config = ModelConfig(name="test", temperature=0.7, max_tokens=0)
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "max_tokens must be a positive integer" in result.errors[0]

def test_validate_model_config_invalid_name():
    """Test model config validation with invalid name."""
    # Test empty name
    config = Mock(spec=ModelConfig)
    config.name = ""
    config.temperature = 0.5
    config.max_tokens = 100
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Config must have a valid model name" in result.errors[0]

    # Test None name
    config = Mock(spec=ModelConfig)
    config.name = None
    config.temperature = 0.5
    config.max_tokens = 100
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Config must have a valid model name" in result.errors[0]

def test_validate_model_config_validation_error():
    """Test model config validation with validation error."""
    config = None
    result = Verifier.validate_model_config(config)
    assert not result.valid
    assert "Input must be a ModelConfig object" in result.errors[0]

def test_validate_model_config_exception():
    """Test model config validation with exception."""
    # Create a mock config that raises an exception when accessing name
    mock_config = Mock(spec=ModelConfig)
    type(mock_config).name = PropertyMock(side_effect=Exception("test error"))
    type(mock_config).temperature = PropertyMock(return_value=0.7)
    type(mock_config).max_tokens = PropertyMock(return_value=100)
    
    result = Verifier.validate_model_config(mock_config)
    assert not result.valid
    assert "Validation error: test error" in result.errors[0]

def test_sanitize_string():
    """Test string sanitization."""
    input_str = 'Test<script>alert("xss")</script>'
    sanitized = Verifier.sanitize_string(input_str)
    assert '<script>' not in sanitized
    assert '&lt;script&gt;' in sanitized

def test_sanitize_string_with_control_chars():
    """Test string sanitization with control characters."""
    input_str = "Test\x00string\x1F"
    sanitized = Verifier.sanitize_string(input_str)
    assert "\x00" not in sanitized
    assert "\x1F" not in sanitized
    assert sanitized == "Teststring"

def test_sanitize_string_error():
    """Test string sanitization with error."""
    result = Verifier.sanitize_string(None)
    assert result == ""

def test_validate_path_success():
    """Test successful path validation."""
    path = "test/path/file.txt"
    result = Verifier.validate_path(path)
    assert result.valid
    assert not result.errors

def test_validate_path_traversal_attempt():
    """Test path validation with traversal attempt."""
    path = "../test/path"
    result = Verifier.validate_path(path)
    assert not result.valid
    assert "Invalid path: potential path traversal" in result.errors[0]

def test_validate_path_invalid_chars():
    """Test path validation with invalid characters."""
    path = "test/path$file.txt"
    result = Verifier.validate_path(path)
    assert not result.valid
    assert "Path contains invalid characters" in result.errors[0]

def test_validate_path_empty():
    """Test path validation with empty path."""
    result = Verifier.validate_path("")
    assert not result.valid
    assert "Path must be a non-empty string" in result.errors[0]

def test_validate_path_validation_error():
    """Test path validation with validation error."""
    path = None
    result = Verifier.validate_path(path)
    assert not result.valid
    assert "Path must be a non-empty string" in result.errors[0]

def test_validate_path_exception():
    """Test path validation with exception."""
    # Create a mock path that raises an exception
    mock_path = Mock(spec=str)
    mock_path.__str__ = Mock(side_effect=Exception("test error"))
    mock_path.__contains__ = Mock(return_value=False)
    
    result = Verifier.validate_path(mock_path)
    assert not result.valid
    assert "Validation error: test error" in result.errors[0]
