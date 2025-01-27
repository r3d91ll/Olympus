"""Tests for CLI main module."""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typer.testing import CliRunner
import asyncio
import yaml
from pathlib import Path

# Mock model_engine module
with patch("olympus.hades.src.model.manager"):
    from olympus.hades.src.cli.main import app

# Test runner
runner = CliRunner()

@pytest.fixture
def event_loop():
    """Create event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config(tmp_path):
    """Create mock config file."""
    config = {
        "model_engine": {
            "model_dir": str(tmp_path / "models"),
            "device": "cpu",
            "max_sequence_length": 512,
            "embedding_dim": 768
        }
    }
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "model_engine.yaml"
    with config_file.open("w") as f:
        yaml.dump(config, f)
    
    with patch("olympus.hades.src.model.manager.CONFIG_PATH", str(config_file)):
        yield config_file

@pytest.fixture
def mock_arango_client():
    """Mock ArangoDB client."""
    with patch("olympus.hades.src.memory_management.arangodb_store.ArangoClient") as mock:
        # Mock the database and collection operations
        mock_db = MagicMock()
        mock_db.collection.return_value = MagicMock()
        mock.return_value.db.return_value = mock_db
        yield mock

@pytest.fixture
def mock_metrics_writer():
    """Mock metrics writer."""
    with patch("olympus.hades.src.monitoring.phoenix_monitor.write_to_textfile") as mock:
        yield mock

@pytest.fixture
def mock_store():
    """Mock ArangoMemoryStore."""
    store = Mock()
    store.initialize = AsyncMock()
    store.store_memory = AsyncMock(return_value={"_id": "test-id"})
    store.find_similar_memories = AsyncMock(return_value=[{
        "content": "Test content",
        "similarity": 0.95,
        "_id": "test-id"
    }])
    return store

@pytest.fixture
def mock_monitor():
    """Mock PhoenixMonitor."""
    monitor = Mock()
    monitor._start_metrics_writer = AsyncMock()
    monitor.initialize = AsyncMock()
    monitor.record_metric = AsyncMock()
    return monitor

@pytest.fixture
def mock_engine():
    """Mock model engine."""
    engine = Mock()
    engine.list_models = AsyncMock(return_value=[{
        "name": "test-model",
        "version": "1.0",
        "type": "embedding",
        "embedding_dim": 768,
        "max_sequence_length": 512,
        "device": "cpu"
    }])
    engine.download_model = AsyncMock(return_value=True)
    engine.load_model = AsyncMock(return_value=Mock())
    return engine

def test_setup_command(event_loop, mock_config, mock_monitor, mock_store, mock_engine, mock_arango_client, mock_metrics_writer):
    """Test setup command."""
    # Set up mocks with proper async behavior
    mock_store.initialize = AsyncMock()
    mock_monitor.initialize = AsyncMock()
    
    with patch("olympus.hades.src.monitoring.phoenix_monitor.PhoenixMonitor") as mock_monitor_cls, \
         patch("olympus.hades.src.memory_management.arangodb_store.ArangoMemoryStore") as mock_store_cls, \
         patch("olympus.hades.src.model.manager.init_model_engine", AsyncMock(return_value=mock_engine)):

        mock_monitor_cls.return_value = mock_monitor
        mock_store_cls.return_value = mock_store

        # Run command
        result = runner.invoke(app, ["setup"])
        assert result.exit_code == 0

def test_model_list_command(event_loop, mock_config, mock_engine):
    """Test model list command."""
    # Set global state with proper async validation
    app.engine = mock_engine
    app.validate_setup = Mock(return_value=True)  # Change back to sync

    # Mock async functions
    mock_engine.list_models = AsyncMock(return_value=[{
        "name": "test-model",
        "version": "1.0",
        "type": "embedding",
        "embedding_dim": 768,
        "max_sequence_length": 512,
        "device": "cpu"
    }])

    # Run command
    result = runner.invoke(app, ["model", "list"])
    assert result.exit_code == 0

def test_model_download_command(event_loop, mock_config, mock_engine):
    """Test model download command."""
    # Set global state with proper async validation
    app.engine = mock_engine
    app.validate_setup = Mock(return_value=True)  # Change back to sync

    # Mock async functions with proper return values
    mock_engine.download_model = AsyncMock(return_value=True)

    # Run command
    result = runner.invoke(app, ["model", "download", "test-model"])
    assert result.exit_code == 0

def test_model_load_command(event_loop, mock_config, mock_engine):
    """Test model load command."""
    # Set global state with proper async validation
    app.engine = mock_engine
    app.validate_setup = Mock(return_value=True)  # Change back to sync

    # Mock async functions with proper return value
    mock_engine.load_model = AsyncMock(return_value=Mock())

    # Run command
    result = runner.invoke(app, ["model", "load", "test-model"])
    assert result.exit_code == 0

def test_embed_command(event_loop, mock_config, mock_engine, mock_store, tmp_path):
    """Test embed command."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    # Set global state with proper async validation
    app.store = mock_store
    app.engine = mock_engine
    app.validate_setup = Mock(return_value=True)  # Change back to sync
    app.current_model = Mock()

    # Mock async functions
    mock_store.store_memory = AsyncMock(return_value={"_id": "test-id"})
    
    with patch("olympus.hades.src.processing.text.process_file", AsyncMock(return_value=[{"content": "Test content", "metadata": {}}])), \
         patch("olympus.hades.src.model.manager.generate_embeddings", AsyncMock(return_value=[[1.0, 2.0, 3.0]])):

        # Run command
        result = runner.invoke(app, ["embed", str(test_file)])
        assert result.exit_code == 0

def test_query_command(event_loop, mock_config, mock_engine, mock_store):
    """Test query command."""
    # Set global state with proper async validation
    app.store = mock_store
    app.engine = mock_engine
    app.validate_setup = Mock(return_value=True)  # Change back to sync
    app.current_model = Mock()

    # Mock async functions with proper return values
    mock_store.find_similar_memories = AsyncMock(return_value=[{
        "content": "Test content",
        "similarity": 0.95,
        "_id": "test-id"
    }])

    with patch("olympus.hades.src.model.manager.generate_embeddings", AsyncMock(return_value=[[1.0, 2.0, 3.0]])):
        # Run command
        result = runner.invoke(app, ["query", "test query"])
        assert result.exit_code == 0

def test_error_handling(event_loop, mock_config, mock_metrics_writer):
    """Test CLI error handling."""
    # Test setup error with proper async behavior
    with patch("olympus.hades.src.monitoring.phoenix_monitor.PhoenixMonitor", side_effect=Exception("Test error")):
        result = runner.invoke(app, ["setup"])
        assert result.exit_code == 1
        assert "Error: Test error" in result.stdout
