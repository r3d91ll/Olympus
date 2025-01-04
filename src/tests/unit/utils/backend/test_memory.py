"""Tests for memory management utilities."""
import os
import json
import pytest
from pathlib import Path
from src_new.utils.backend.memory import MemoryManager

class NonSerializable:
    """Class for testing non-serializable objects."""
    pass

@pytest.fixture
def memory_manager(tmp_path):
    """Create a memory manager instance with a temporary base directory."""
    return MemoryManager(str(tmp_path / "test_memory"))

def test_init_creates_directory(tmp_path):
    """Test that initialization creates the base directory."""
    base_dir = tmp_path / "test_memory"
    assert not base_dir.exists()
    
    manager = MemoryManager(str(base_dir))
    assert base_dir.exists()
    assert base_dir.is_dir()

def test_store_creates_namespace_directory(memory_manager):
    """Test that storing data creates namespace directory."""
    test_data = {"key": "value"}
    memory_manager.store("test_key", test_data, "test_namespace")
    
    namespace_path = memory_manager.base_dir / "test_namespace"
    assert namespace_path.exists()
    assert namespace_path.is_dir()

def test_store_and_retrieve_data(memory_manager):
    """Test storing and retrieving data."""
    test_data = {"key": "value"}
    memory_manager.store("test_key", test_data)
    
    retrieved_data = memory_manager.retrieve("test_key")
    assert retrieved_data == test_data

def test_retrieve_nonexistent_data(memory_manager):
    """Test retrieving nonexistent data returns None."""
    retrieved_data = memory_manager.retrieve("nonexistent_key")
    assert retrieved_data is None

def test_retrieve_corrupted_data(memory_manager):
    """Test retrieving corrupted data returns None."""
    # Create a corrupted JSON file
    namespace_path = memory_manager._get_namespace_path("default")
    file_path = namespace_path / "corrupted_key"
    with open(file_path, 'w') as f:
        f.write("invalid json{")
    
    retrieved_data = memory_manager.retrieve("corrupted_key")
    assert retrieved_data is None

def test_clear_namespace(memory_manager):
    """Test clearing a namespace."""
    test_data = {"key": "value"}
    memory_manager.store("test_key", test_data, "ns1")
    memory_manager.store("test_key2", test_data, "ns1")
    
    assert memory_manager.clear_namespace("ns1")
    assert not (memory_manager.base_dir / "ns1").exists()

def test_clear_empty_namespace(memory_manager):
    """Test clearing an empty namespace."""
    # Empty namespace should be cleared successfully
    assert memory_manager.clear_namespace("nonexistent")
    assert not (memory_manager.base_dir / "nonexistent").exists()

def test_clear_namespace_error(memory_manager):
    """Test clearing a namespace with permission error."""
    test_data = {"key": "value"}
    memory_manager.store("test_key", test_data, "ns1")
    
    # Make namespace directory read-only
    namespace_path = memory_manager.base_dir / "ns1"
    os.chmod(namespace_path, 0o444)
    
    try:
        assert not memory_manager.clear_namespace("ns1")
    finally:
        # Restore permissions for cleanup
        os.chmod(namespace_path, 0o777)

def test_clear_all(memory_manager):
    """Test clearing all data."""
    test_data = {"key": "value"}
    memory_manager.store("test_key1", test_data, "ns1")
    memory_manager.store("test_key2", test_data, "ns2")
    
    assert memory_manager.clear_all()
    assert not list(memory_manager.base_dir.glob("*"))

def test_clear_all_error(memory_manager):
    """Test clearing all data with permission error."""
    test_data = {"key": "value"}
    memory_manager.store("test_key", test_data, "ns1")
    
    # Make base directory read-only
    os.chmod(memory_manager.base_dir, 0o444)
    
    try:
        assert not memory_manager.clear_all()
    finally:
        # Restore permissions for cleanup
        os.chmod(memory_manager.base_dir, 0o777)

def test_store_invalid_json(memory_manager):
    """Test storing non-serializable data."""
    non_serializable = NonSerializable()
    assert not memory_manager.store("test_key", non_serializable)

def test_store_with_special_characters(memory_manager):
    """Test storing data with special characters in key and namespace."""
    test_data = {"key": "value"}
    memory_manager.store("test/key@123", test_data, "test/ns@123")
    
    # Check that special characters are properly handled
    safe_namespace = "test_ns_123"
    safe_key = "test_key_123"
    namespace_path = memory_manager.base_dir / safe_namespace
    assert namespace_path.exists()
    assert (namespace_path / safe_key).exists()
