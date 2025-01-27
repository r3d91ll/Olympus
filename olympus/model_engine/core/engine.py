"""Core model engine implementation using vLLM's OpenAI-compatible API."""
import signal
from typing import Optional
import subprocess
from pathlib import Path

class ModelEngine:
    """Manages vLLM model server process."""
    
    def __init__(self, model_path: Optional[Path] = None) -> None:
        """Initialize model engine.
        
        Args:
            model_path: Optional path to model directory for storing downloaded models
        """
        self.model_path = model_path or Path.home() / ".cache" / "olympus" / "models"
        self.model_path.mkdir(parents=True, exist_ok=True)
        self._current_process: Optional[subprocess.Popen] = None
        
    def start_server(self, model_name: str, port: int = 8000) -> None:
        """Start vLLM OpenAI-compatible API server.
        
        This downloads the model if needed and serves it via FastAPI
        with an OpenAI-compatible /v1/completions endpoint.
        
        Args:
            model_name: Name of HuggingFace model to load
            port: Port to serve model on (default: 8000)
            
        Raises:
            RuntimeError: If server is already running
        """
        if self._current_process:
            raise RuntimeError("Server is already running. Stop it first.")
            
        # Start vLLM OpenAI-compatible server
        self._current_process = subprocess.Popen([
            "python", "-m", "vllm.entrypoints.openai.api_server",
            "--model", model_name,
            "--port", str(port),
            "--download-dir", str(self.model_path)
        ])
        
    def stop_server(self) -> None:
        """Gracefully stop the vLLM server."""
        if not self._current_process:
            return
            
        # Send SIGTERM to allow graceful shutdown
        self._current_process.send_signal(signal.SIGTERM)
        
        # Wait up to 30 seconds for process to end
        try:
            self._current_process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown fails
            self._current_process.kill()
            self._current_process.wait()
            
        self._current_process = None
