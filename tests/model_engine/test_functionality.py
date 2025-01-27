"""Test model engine functionality."""
import pytest
from unittest.mock import MagicMock, patch
import subprocess
import signal
from pathlib import Path

from olympus.model_engine.core.engine import ModelEngine

TEST_MODEL = "Salesforce/codegen-350M-mono"

@pytest.fixture
def model_engine():
    """Create model engine instance."""
    return ModelEngine(model_path=Path("/tmp/test_models"))

def test_server_start_and_stop(model_engine):
    """Test server start and stop."""
    # Mock subprocess.Popen
    mock_process = MagicMock()
    with patch("subprocess.Popen", return_value=mock_process) as mock_popen:
        # Test starting server
        model_engine.start_server(TEST_MODEL)
        
        # Verify process started with correct args
        mock_popen.assert_called_once_with([
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", TEST_MODEL,
            "--port", "8000",
            "--download-dir", str(model_engine.model_path)
        ])
        
        # Test stopping server
        model_engine.stop_server()
        
        # Verify SIGTERM was sent
        mock_process.send_signal.assert_called_once_with(signal.SIGTERM)
        mock_process.wait.assert_called()

def test_server_start_error_if_already_running(model_engine):
    """Test error when starting server while one is already running."""
    # Mock subprocess.Popen
    mock_process = MagicMock()
    with patch("subprocess.Popen", return_value=mock_process):
        # Start first server
        model_engine.start_server(TEST_MODEL)
        
        # Try to start second server
        with pytest.raises(RuntimeError, match="Server is already running"):
            model_engine.start_server(TEST_MODEL)

def test_server_stop_handles_timeout(model_engine):
    """Test stop handles timeout gracefully."""
    # Mock subprocess.Popen
    mock_process = MagicMock()
    mock_process.wait.side_effect = [subprocess.TimeoutExpired("cmd", 30), None]
    
    with patch("subprocess.Popen", return_value=mock_process):
        # Start and stop server
        model_engine.start_server(TEST_MODEL)
        model_engine.stop_server()
        
        # Verify SIGTERM was sent first
        mock_process.send_signal.assert_called_once_with(signal.SIGTERM)
        
        # Verify process was killed after timeout
        mock_process.kill.assert_called_once()
        assert mock_process.wait.call_count == 2
