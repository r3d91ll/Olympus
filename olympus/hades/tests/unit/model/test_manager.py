"""Tests for model manager module."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import yaml

# Import the module under test
from olympus.hades.src.model.manager import (
    init_model_engine,
    list_available_models,
    download_model,
    load_model,
    generate_embeddings,
    ModelMetadata
)

@pytest.fixture
def mock_engine() -> Mock:
    """Create mock model engine."""
    engine = Mock()
    engine.list_models = AsyncMock(return_value=[{
        "name": "test-model",
        "version": "1.0.0",
        "type": "encoder",
        "embedding_dim": 768,
        "max_sequence_length": 512,
        "device": "cuda"
    }])
    engine.download_model = AsyncMock(return_value={
        "name": "test-model",
        "version": "1.0.0",
        "type": "encoder",
        "embedding_dim": 768,
        "max_sequence_length": 512,
        "device": "cuda"
    })
    engine.load_model = AsyncMock(return_value=Mock())
    engine.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])
    return engine

@pytest.fixture
def mock_model() -> Mock:
    """Create mock model."""
    model = Mock()
    model.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])
    return model

@pytest.fixture
def config_file(tmp_path) -> Path:
    """Create a test config file."""
    config = {
        "model_engine": {
            "model_dir": str(tmp_path / "models"),
            "metrics_dir": str(tmp_path / "metrics"),
            "device": "cpu",
            "max_sequence_length": 512,
            "embedding_dim": 768
        }
    }
    config_path = tmp_path / "config" / "model_engine.yaml"
    config_path.parent.mkdir(exist_ok=True)
    with config_path.open("w") as f:
        yaml.dump(config, f)
    return config_path

@pytest.mark.asyncio
async def test_init_model_engine_success(config_file):
    """Test successful model engine initialization."""
    with patch("olympus.hades.src.model.manager.ModelRegistry") as mock_registry_cls, \
         patch("olympus.hades.src.model.manager.InferenceEngine") as mock_inference_cls, \
         patch("olympus.hades.src.model.manager.ModelMonitor") as mock_monitor_cls, \
         patch("olympus.hades.src.model.manager.ModelEngine") as mock_engine_cls:
        
        # Set up mocks
        mock_registry = Mock()
        mock_inference = Mock()
        mock_monitor = Mock()
        mock_engine = Mock()
        
        mock_registry_cls.return_value = mock_registry
        mock_inference_cls.return_value = mock_inference
        mock_monitor_cls.return_value = mock_monitor
        mock_engine_cls.return_value = mock_engine
        
        # Run test
        engine = await init_model_engine(str(config_file))
        
        # Verify
        assert engine == mock_engine
        mock_registry_cls.assert_called_once_with(
            config_dir=str(Path(str(Path(config_file).parent.parent / "models")) / "configs")
        )
        mock_inference_cls.assert_called_once_with()
        mock_monitor_cls.assert_called_once_with()
        mock_engine_cls.assert_called_once_with(
            registry=mock_registry,
            inference=mock_inference,
            monitor=mock_monitor
        )

@pytest.mark.asyncio
async def test_init_model_engine_missing_config():
    """Test model engine initialization with missing config."""
    with pytest.raises(FileNotFoundError) as exc_info:
        await init_model_engine("/nonexistent/config.yaml")
    assert "Config not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_init_model_engine_invalid_config(tmp_path):
    """Test model engine initialization with invalid config."""
    # Create invalid config file
    config_path = tmp_path / "invalid_config.yaml"
    config_path.write_text("invalid: yaml: :")
    
    with pytest.raises(Exception):
        await init_model_engine(str(config_path))

@pytest.mark.asyncio
async def test_list_models(mock_engine):
    """Test model listing."""
    models = await list_available_models(mock_engine)
    assert len(models) == 1
    assert isinstance(models[0], ModelMetadata)
    assert models[0].name == "test-model"
    assert models[0].version == "1.0.0"
    assert models[0].type == "encoder"
    assert models[0].embedding_dim == 768
    assert models[0].max_sequence_length == 512
    assert models[0].device == "cuda"

@pytest.mark.asyncio
async def test_download_model(mock_engine):
    """Test model download."""
    await download_model(mock_engine, "test-model", version="1.0.0")
    mock_engine.download_model.assert_called_once_with("test-model", "1.0.0")

@pytest.mark.asyncio
async def test_download_model_no_version(mock_engine):
    """Test model download without version."""
    await download_model(mock_engine, "test-model")
    mock_engine.download_model.assert_called_once_with("test-model", None)

@pytest.mark.asyncio
async def test_load_model(mock_engine):
    """Test model loading."""
    model = await load_model(mock_engine, "test-model", version="1.0.0")
    assert model is not None
    mock_engine.load_model.assert_called_once_with("test-model", "1.0.0")

@pytest.mark.asyncio
async def test_load_model_no_version(mock_engine):
    """Test model loading without version."""
    model = await load_model(mock_engine, "test-model")
    assert model is not None
    mock_engine.load_model.assert_called_once_with("test-model", None)

@pytest.mark.asyncio
async def test_generate_embeddings(mock_model):
    """Test embedding generation."""
    texts = ["test text 1", "test text 2"]
    embeddings = await generate_embeddings(mock_model, texts)
    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(len(emb) == 3 for emb in embeddings)
    mock_model.generate_embeddings.assert_called_once_with(texts[:32])

@pytest.mark.asyncio
async def test_generate_embeddings_empty_texts(mock_model):
    """Test embedding generation with empty texts."""
    embeddings = await generate_embeddings(mock_model, [])
    assert len(embeddings) == 0
    mock_model.generate_embeddings.assert_not_called()

@pytest.mark.asyncio
async def test_generate_embeddings_large_batch(mock_model):
    """Test embedding generation with large batch."""
    texts = [f"test text {i}" for i in range(100)]
    mock_model.generate_embeddings.side_effect = lambda batch: [[0.1, 0.2, 0.3]] * len(batch)
    
    embeddings = await generate_embeddings(mock_model, texts, batch_size=32)
    
    assert len(embeddings) == 100
    assert len(mock_model.generate_embeddings.mock_calls) == 4  # ceil(100/32) = 4 batches
