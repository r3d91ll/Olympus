import pytest
from olympus.model_engine.core.engine import ModelEngine
import subprocess

def test_model_engine_init():
    engine = ModelEngine()
    assert engine.model_path.exists()

def test_start_server(mocker):
    engine = ModelEngine()
    mock_popen = mocker.patch('subprocess.Popen')
    engine.start_server("Salesforce/codegen-350M-mono", port=8000)
    mock_popen.assert_called_once_with([
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", "Salesforce/codegen-350M-mono",
        "--port", "8000",
        "--download-dir", str(engine.model_path)
    ])

def test_stop_server(mocker):
    engine = ModelEngine()
    mock_popen = mocker.patch('subprocess.Popen')
    mock_process = mock_popen.return_value
    mock_process.wait.side_effect = subprocess.TimeoutExpired(None, None)
    engine.start_server("Salesforce/codegen-350M-mono", port=8000)
    engine.stop_server()
    mock_process.send_signal.assert_called_once_with(subprocess.signal.SIGTERM)
    mock_process.wait.assert_called_once_with(timeout=30)
    mock_process.kill.assert_called_once()