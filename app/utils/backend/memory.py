"""Memory management utility for temporary data storage using tmpfs.

This module handles all temporary data storage operations using a tmpfs-based system,
ensuring the application remains stateless by default.
"""

import os
import json
from pathlib import Path
from typing import Any, Optional

from ..shared.logger import get_logger

logger = get_logger(__name__)

class MemoryManager:
    """Manages temporary storage using tmpfs."""

    def __init__(self, base_dir: str = "ramdisk"):
        """Initialize the memory manager.

        Args:
            base_dir: Base directory for temporary storage.
        """
        self.base_dir = Path(base_dir)
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)

    def _get_namespace_path(self, namespace: str) -> Path:
        """Get the path for a namespace, creating directories as needed.

        Args:
            namespace: Namespace for the data.

        Returns:
            Path object for the namespace directory.
        """
        # Convert namespace to a safe path
        safe_namespace = namespace.replace('/', '_').replace('@', '_')
        namespace_path = self.base_dir / safe_namespace
        namespace_path.mkdir(parents=True, exist_ok=True)
        return namespace_path

    def store(self, key: str, data: Any, namespace: str = "default") -> bool:
        """Store data in temporary storage.

        Args:
            key: Key to store the data under.
            data: Data to store.
            namespace: Optional namespace for the data.

        Returns:
            True if storage was successful, False otherwise.
        """
        try:
            namespace_path = self._get_namespace_path(namespace)
            # Convert key to a safe filename
            safe_key = key.replace('/', '_').replace('@', '_')
            file_path = namespace_path / safe_key

            with open(file_path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Failed to store data: {str(e)}")
            return False

    def retrieve(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Retrieve data from temporary storage.

        Args:
            key: Key to retrieve data for.
            namespace: Optional namespace for the data.

        Returns:
            Retrieved data or None if not found.
        """
        try:
            namespace_path = self._get_namespace_path(namespace)
            safe_key = key.replace('/', '_').replace('@', '_')
            file_path = namespace_path / safe_key

            if not file_path.exists():
                return None

            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to retrieve data: {str(e)}")
            return None

    def clear_namespace(self, namespace: str) -> bool:
        """Clear all data in a namespace.

        Args:
            namespace: Namespace to clear.

        Returns:
            True if clearing was successful, False otherwise.
        """
        try:
            namespace_path = self._get_namespace_path(namespace)
            for file_path in namespace_path.glob('*'):
                file_path.unlink()
            namespace_path.rmdir()
            logger.info(f"Cleared namespace {namespace} data")
            return True
        except Exception as e:
            logger.error(f"Failed to clear namespace: {str(e)}")
            return False

    def clear_all(self) -> bool:
        """Clear all data in all namespaces.

        Returns:
            True if clearing was successful, False otherwise.
        """
        try:
            for namespace_path in self.base_dir.glob('*'):
                if namespace_path.is_dir():
                    for file_path in namespace_path.glob('*'):
                        file_path.unlink()
                    namespace_path.rmdir()
            logger.info("Cleared all data")
            return True
        except Exception as e:
            logger.error(f"Failed to clear all data: {str(e)}")
            return False
