"""Utility module for validating inputs."""

import re
import html
import logging
import math
from typing import Optional, Any
from app.utils.shared.types import Message, ModelConfig, ValidationResult

# Get logger
logger = logging.getLogger(__name__)

class Verifier:
    """Class for validating inputs."""

    @staticmethod
    def validate_message(message: Any) -> ValidationResult:
        """Validate a message object.

        Args:
            message: Message object to validate

        Returns:
            ValidationResult indicating if message is valid
        """
        try:
            # Check type first
            if not isinstance(message, Message):
                return ValidationResult(
                    valid=False,
                    errors=["Input must be a Message object"]
                )

            # Access properties to validate
            role = message.role
            content = message.content

            # Check role
            if not role:
                return ValidationResult(
                    valid=False,
                    errors=["Message must have a valid role string"]
                )

            # Check content
            if not content:
                return ValidationResult(
                    valid=False,
                    errors=["Message must have valid content string"]
                )

            return ValidationResult(valid=True)

        except Exception as e:
            logger.error(f"Message validation error: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )

    @staticmethod
    def validate_model_config(config: Any) -> ValidationResult:
        """Validate a model configuration.

        Args:
            config: ModelConfig object to validate

        Returns:
            ValidationResult indicating if config is valid
        """
        try:
            # Check type first
            if not isinstance(config, ModelConfig):
                return ValidationResult(
                    valid=False,
                    errors=["Input must be a ModelConfig object"]
                )

            # Access properties to validate
            name = config.name
            temperature = config.temperature
            max_tokens = config.max_tokens

            # Check name
            if not name:
                return ValidationResult(
                    valid=False,
                    errors=["Config must have a valid model name"]
                )

            # Check temperature
            if not 0 <= temperature <= 1 or not isinstance(temperature, (int, float)) or not math.isfinite(temperature):
                return ValidationResult(
                    valid=False,
                    errors=["Temperature must be a finite float between 0 and 1"]
                )

            # Check max_tokens
            if max_tokens <= 0:
                return ValidationResult(
                    valid=False,
                    errors=["max_tokens must be a positive integer"]
                )

            return ValidationResult(valid=True)

        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )

    @staticmethod
    def sanitize_string(input_str: Optional[str]) -> str:
        """Sanitize a string by escaping HTML and removing control characters.

        Args:
            input_str: String to sanitize

        Returns:
            Sanitized string
        """
        if not input_str:
            return ""

        # Escape HTML
        escaped = html.escape(input_str)

        # Remove control characters
        sanitized = "".join(char for char in escaped if ord(char) >= 32)

        return sanitized

    @staticmethod
    def validate_path(path: str) -> ValidationResult:
        """Validate a file system path.

        Args:
            path: Path string to validate

        Returns:
            ValidationResult indicating if path is valid
        """
        try:
            # Check type first
            if not path or not isinstance(path, str):
                return ValidationResult(
                    valid=False,
                    errors=["Path must be a non-empty string"]
                )

            # Convert to string to validate
            path_str = str(path)

            # Check for common path traversal attempts
            if ".." in path_str or "//" in path_str:
                return ValidationResult(
                    valid=False,
                    errors=["Invalid path: potential path traversal"]
                )

            # Check for invalid characters
            if re.search(r'[<>:"|?*$]', path_str):
                return ValidationResult(
                    valid=False,
                    errors=["Path contains invalid characters"]
                )

            return ValidationResult(valid=True)

        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return ValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
