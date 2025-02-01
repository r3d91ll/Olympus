Below is an **updated** version of the build document with **Docker** usage emphasized to ensure a consistent CUDA version (12.1) required by the stable release of vLLM. This helps avoid mismatches with the workstation’s native CUDA 12.4 environment. The relevant changes and instructions for Docker-based development are highlighted in the **System Requirements**, **Quick Start Guide**, and a new **Docker Setup** section. Feel free to adapt any specifics (e.g., base image, mount paths) to your organization’s standards.

---

# Olympus Engine Build Document

**Version:** 1.0.1  
**Last Updated:** 2025-01-12  
**Status:** Phase 1 - CLI Development (Docker Integration)

## Table of Contents

1. [Overview](#overview)  
2. [System Requirements](#system-requirements)  
3. [Quick Start Guide](#quick-start-guide)  
4. [Docker Setup](#docker-setup)  
5. [Architecture](#architecture)  
6. [CLI Implementation](#cli-implementation)  
7. [Database Schema](#database-schema)  
8. [Configuration Management](#configuration-management)  
9. [Development Guide](#development-guide)  
10. [Testing Strategy](#testing-strategy)  
11. [Verification and Validation](#verification-and-validation)  
12. [Troubleshooting](#troubleshooting)  
13. [Security Considerations](#security-considerations)  
14. [Future Considerations](#future-considerations)  
15. [Conclusion](#conclusion)

---

## Overview

The Olympus Engine is a critical component providing model management and inference capabilities using **vLLM** for tensor parallelization. Due to a discrepancy between the workstation CUDA (12.4) and the stable vLLM release (designed for CUDA 12.1), **Docker** must be used to ensure a consistent environment.

Development is split into two phases:

1. **CLI Interface** (Current Phase)  
2. **REST API Interface** (Future Phase)

### Core Features

- Download models from HuggingFace  
- Register models and configurations in SQLite  
- Load/unload models with vLLM  
- Configure tensor parallelization  
- Manage multiple models  

---

## System Requirements

### Hardware Requirements

- **CUDA-capable GPU** with 8GB+ VRAM (16GB+ recommended)  
- **16GB+ System RAM**  
- **100GB+ Storage** (SSD recommended)

### Software Dependencies (Host System)

- **Docker** (19.03+), or any version that supports **NVIDIA Container Toolkit**  
- **NVIDIA Container Toolkit** for GPU pass-through in Docker  
- **Docker Compose** (optional, if you prefer compose files)

> **Important**: You do **not** need to match the workstation’s native CUDA version to vLLM. **All development and runtime operations** will happen inside the Docker container with the compatible CUDA 12.1 environment.

---

## Quick Start Guide

### 1. Install Docker & NVIDIA Container Toolkit (Host)

Follow official instructions for:

- [Docker Installation](https://docs.docker.com/engine/install/)  
- [NVIDIA Container Toolkit Installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### 2. Build and Launch Docker Container

See [Docker Setup](#docker-setup) for the detailed steps. In short:

```bash
docker build -t olympus-engine:latest .
docker run --gpus all -it --name olympus_dev \
    -v $(pwd):/workspace/olympus-engine \
    olympus-engine:latest bash
```

### 4. Inside the Docker Container

Activate your Python environment and proceed with the usual steps:

```bash
cd /workspace/olympus-engine
source venv/bin/activate
olympus --help
```

---

## Docker Setup

This section ensures you have a **CUDA 12.1** environment inside Docker, matching the stable vLLM requirements.

### Dockerfile Example

Below is a minimal Dockerfile you can place in the `olympus-engine/` root folder:

```dockerfile
# Use NVIDIA base image with CUDA 12.1 support
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    python3.10 \
    python3.10-venv \
    python3-pip \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /workspace/olympus-engine

# Create a virtual environment (venv) for Python
RUN python3.10 -m venv /opt/venv

# Upgrade pip and install Python dependencies
RUN /opt/venv/bin/pip install --upgrade pip

# Copy requirements for vLLM, click, pydantic, etc.
# If you have a requirements.txt or pyproject.toml, copy them here.
COPY requirements.txt /workspace/olympus-engine/requirements.txt

# Install dependencies in the venv
RUN /opt/venv/bin/pip install -r requirements.txt

# Expose any ports if needed (not strictly necessary for CLI)
# EXPOSE 8000

# By default, start a bash shell
CMD ["/bin/bash"]
```

### Building the Docker Image

```bash
docker build -t olympus-engine:latest .
```

### Running the Container

```bash
# Ensure --gpus all is passed for GPU access
docker run --gpus all -it --name olympus_dev \
    -v $(pwd):/workspace/olympus-engine \
    olympus-engine:latest \
    bash
```

Once inside the container:

```bash
# Activate the Python venv
source /opt/venv/bin/activate

# Move to project directory
cd /workspace/olympus-engine

# (Optional) Reinstall if needed
pip install -r requirements.txt

# Now run Olympus Engine commands
olympus --help
```

---

## Architecture

### Core Components

- **vLLM Engine**: Handles model loading and inference  
- **SQLite Registry**: Stores model configurations and metadata  
- **File System Manager**: Manages model files and cache  
- **CLI Interface**: Primary user interaction layer  

### Directory Structure

```
olympus_engine/
├── cli/
│   ├── commands/
│   └── main.py
├── core/
│   ├── config/
│   ├── db/
│   └── model_manager/
├── utils/
└── vllm_integration/
```

---

## CLI Implementation

### Command Structure

```
olympus
├── model
│   ├── download    # Download from HuggingFace
│   ├── load        # Load with optional config
│   ├── unload      # Unload active model
│   ├── delete      # Remove model and registry
│   └── list        # Show available models
└── config
    ├── set-default # Set default configuration
    └── show        # Display current configuration
```

#### Command Examples

**Model Management**

```bash
# Download a model
olympus model download --name meta-llama/Llama-2-7b-chat-hf

# List available models
olympus model list

# Load with default config
olympus model load --name llama-2-7b-chat

# Load with custom config
olympus model load --name llama-2-7b-chat --config custom_config.json

# Unload model
olympus model unload --name llama-2-7b-chat

# Delete model
olympus model delete --name llama-2-7b-chat
```

**Configuration Management**

```bash
# Show current config
olympus config show

# Set new default config
olympus config set-default --file new_defaults.json

# Show current GPU allocation (example)
olympus config show --gpu-status
```

---

## Database Schema

### Models Table

```sql
CREATE TABLE models (
    model_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_url TEXT,
    local_path TEXT NOT NULL,
    config_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);
```

### Active Models Table

```sql
CREATE TABLE active_models (
    model_id TEXT PRIMARY KEY,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config_override_json TEXT,
    FOREIGN KEY(model_id) REFERENCES models(model_id)
);
```

### Database Management

```bash
# Initialize database
olympus db init

# Backup database
olympus db backup

# View model registry
olympus db list-models

# Check model status
olympus db status --model-name llama-2-7b-chat
```

---

## Configuration Management

### Default Configuration

```json
{
    "model": {
        "tensor_parallel_size": 1,
        "gpu_memory_utilization": 0.90,
        "max_model_len": 8192,
        "quantization": null
    },
    "system": {
        "cache_dir": "/path/to/cache",
        "models_dir": "/path/to/models",
        "max_parallel_models": 1,
        "log_level": "INFO"
    }
}
```

### Model-Specific Configuration Override

```json
{
    "model": {
        "tensor_parallel_size": 2,
        "quantization": "int8",
        "max_model_len": 4096
    }
}
```

### Environment Variables

```bash
# Set these in your ~/.bashrc or inside the container before running Olympus
export OLYMPUS_CACHE_DIR="/path/to/cache"
export OLYMPUS_MODELS_DIR="/path/to/models"
export OLYMPUS_LOG_LEVEL="DEBUG"
export HF_AUTH_TOKEN="your_huggingface_token"
```

---

## Development Guide

### Code Style and Standards

```bash
# Install development dependencies
pip install black flake8 isort mypy pytest

# Format code
black olympus_engine/
isort olympus_engine/

# Run linting
flake8 olympus_engine/

# Type checking
mypy olympus_engine/
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Run tests before pushing
pytest tests/

# Push and create PR
git push origin feature/new-feature
```

### Logging Best Practices

```python
from olympus_engine.utils.logger import logger

# Structured logging examples
logger.info("Loading model", extra={"model_name": name})
logger.debug("Configuration details", extra={"config": config_dict})
logger.error("Failed to load model", extra={"error": str(e)})
```

### Error Handling

```python
from olympus_engine.utils.exceptions import (
    ModelNotFoundError,
    ConfigurationError,
    ResourceError
)

try:
    model_manager.load_model(name)
except ModelNotFoundError as e:
    logger.error("Model not found", extra={"name": name})
    raise
except ResourceError as e:
    logger.error("Insufficient resources", extra={"error": str(e)})
    raise
```

---

## Testing Strategy

### Setting Up Test Environment

```bash
# Inside the container, install test dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Run all tests
pytest

# Run with coverage report
pytest --cov=olympus_engine tests/

# Run specific test category
pytest tests/test_model_manager.py
```

### Test Categories

**Unit Tests**

```python
# Example: tests/test_model_manager.py
def test_model_load_configuration():
    config = ModelConfig(
        tensor_parallel_size=1,
        gpu_memory_utilization=0.9
    )
    assert config.is_valid()

@pytest.mark.asyncio
async def test_model_download():
    model_name = "facebook/opt-125m"
    result = await model_manager.download(model_name)
    assert result.success
```

**Integration Tests**

```python
# Example: tests/test_cli_integration.py
def test_model_download_and_load():
    result = runner.invoke(cli, ["model", "download",
                                 "--name", "facebook/opt-125m"])
    assert result.exit_code == 0
    
    result = runner.invoke(cli, ["model", "load",
                                 "--name", "opt-125m"])
    assert result.exit_code == 0
```

**Performance Tests**

```python
# Example: tests/test_performance.py
@pytest.mark.performance
def test_model_load_time():
    start_time = time.time()
    model_manager.load_model("opt-125m")
    load_time = time.time() - start_time
    
    assert load_time < 30  # seconds
```

---

## Verification and Validation

### Environment Setup Verification

Run these commands **inside the Docker container** to verify your environment is correctly configured:

```bash
# Python Environment
which python        # Should point to /opt/venv/bin/python
python --version    # Should show 3.10 or higher

# CUDA Setup (container version)
nvidia-smi          # Should show GPU(s) and CUDA 12.1
nvcc --version      # Should match CUDA 12.1.x

# Dependencies
pip freeze | grep vllm   # Should show vllm==0.2.0
pip freeze | grep torch  # Should show compatible PyTorch version
```

**Expected Output Example:**

<details>
  <summary>Click to Expand</summary>

```bash
$ nvidia-smi
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.60.13    Driver Version: 525.60.13    CUDA Version: 12.1     |
|-------------------------------+----------------------+----------------------+
...

$ python --version
Python 3.10.12
```

</details>

### Installation Success Checklist

- [ ] Docker image built successfully  
- [ ] Container runs with `--gpus all` flag  
- [ ] Python virtual environment exists in `/opt/venv`  
- [ ] CUDA toolkit inside container verified (`nvidia-smi`, `nvcc --version`)  
- [ ] Database initialized and accessible  
- [ ] Model directory permissions set correctly  
- [ ] Logging configured and writable  

### Command Validation Examples

#### Model Download

```bash
olympus model download --name facebook/opt-125m
```

**Expected Output:**

```bash
Downloading:   100%|████████| 250M/250M [00:30<00:00, 8.33MB/s]
Model downloaded successfully to /path/to/models/opt-125m
```

#### Model Load

```bash
olympus model load --name opt-125m
```

**Expected Output:**

```bash
Loading model opt-125m...
Initializing vLLM engine...
Model loaded successfully. Status: READY
```

### Self-Diagnosis Guide

For each operation, verify success using these commands:

- **After Download**:

  ```bash
  ls -l $OLYMPUS_MODELS_DIR/opt-125m  # Should show model files
  olympus db list-models             # Should show the model in registry
  ```

- **After Load**:

  ```bash
  olympus model status  # Should show "LOADED"
  nvidia-smi            # Should show GPU memory usage
  ```

- **After Configuration Change**:

  ```bash
  olympus config show            # Should reflect your changes
  cat ~/.olympus/config.json     # Should be valid JSON
  ```

### Common Error Patterns and Solutions

| Symptom            | Verification Command          | Solution                                               |
|--------------------|-------------------------------|--------------------------------------------------------|
| **Model not found**      | `olympus db list-models`            | Check download logs in `/var/log/olympus/olympus.log`  |
| **CUDA error**           | `nvidia-smi`                         | Verify GPU drivers and container CUDA version          |
| **Permission denied**    | `ls -l $OLYMPUS_MODELS_DIR`          | Run permission fix commands from Security section       |
| **Database error**       | `sqlite3 olympus.db .tables`         | Initialize or repair database inside container          |

Remember to check `/var/log/olympus/olympus.log` for detailed error messages if any step fails.

---

## Troubleshooting

### Common Issues and Solutions

1. **CUDA/GPU Issues**  

   ```bash
   # Inside container: 
   nvidia-smi
   # If fails, ensure host has NVIDIA Container Toolkit
   # and container is run with --gpus all
   ```

2. **Memory Management**  

   ```bash
   # Check GPU memory usage inside container
   watch -n 1 nvidia-smi

   # If OOM errors:
   # 1. Reduce batch size in config
   # 2. Enable quantization
   # 3. Increase tensor parallelism
   ```

3. **Model Loading Issues**  

   ```bash
   # Check model files
   ls -la $OLYMPUS_MODELS_DIR

   # Verify database state
   sqlite3 olympus.db
   > SELECT * FROM models WHERE name = 'problem-model';
   > SELECT * FROM active_models;

   # Clear model cache
   rm -rf $OLYMPUS_CACHE_DIR/*
   ```

4. **Database Issues**  

   ```bash
   # Backup current database
   cp olympus.db olympus.db.backup

   # Reset database
   rm olympus.db
   olympus db init

   # Check database integrity
   sqlite3 olympus.db "PRAGMA integrity_check;"
   ```

### Logging and Debugging

```bash
# Enable Debug Logging Temporarily
export OLYMPUS_LOG_LEVEL=DEBUG

# Permanent (add to ~/.bashrc inside container or your Dockerfile)
echo 'export OLYMPUS_LOG_LEVEL=DEBUG' >> ~/.bashrc
```

```bash
# View Detailed Logs
# Show last 100 lines of logs
tail -n 100 /var/log/olympus/olympus.log

# Follow logs in real-time
tail -f /var/log/olympus/olympus.log
```

---

## Security Considerations

### File System Security

#### Model Storage

```bash
# Inside container: set correct permissions for model directory
chmod 750 $OLYMPUS_MODELS_DIR
chown -R olympus:olympus $OLYMPUS_MODELS_DIR

# Secure config files
chmod 600 ~/.olympus/config.json
```

#### Database Security

```bash
# Inside container: set correct permissions for database
chmod 600 olympus.db
chown olympus:olympus olympus.db

# Backup permissions
chmod 600 olympus.db.backup
```

### API Security

#### Authentication

- Store HuggingFace tokens securely  
- Use environment variables for sensitive data  
- Implement token rotation if needed  

```bash
# Secure way to set tokens inside container
export HF_AUTH_TOKEN=$(cat /path/to/secure/token)
```

#### Access Control

```python
# Example access control implementation
class ModelAccess:
    def check_permissions(self, user, model_name):
        return self.acl.has_permission(user, model_name)
```

---

## Future Considerations

### Phase 2: REST API Implementation

#### Planned Endpoints

```python
# Model Management
POST   /api/v1/models/download
POST   /api/v1/models/load
POST   /api/v1/models/unload
DELETE /api/v1/models/{name}
GET    /api/v1/models/list

# Configuration
GET    /api/v1/config
PUT    /api/v1/config
```

### Scaling Considerations

**Multi-GPU Support**

```json
{
    "model": {
        "tensor_parallel_size": 4,
        "pipeline_parallel_size": 2,
        "gpu_allocation": ["0,1", "2,3"]
    }
}
```

**Load Balancing**

```json
{
    "load_balancing": {
        "strategy": "round_robin",
        "max_requests_per_model": 1000,
        "health_check_interval": 30
    }
}
```

### Monitoring and Metrics

**Prometheus Integration**

```python
# Future metrics collection example
from prometheus_client import Counter, Gauge

MODEL_LOAD_TIME = Gauge('model_load_seconds', 'Time taken to load model')
INFERENCE_REQUESTS = Counter('inference_requests_total', 'Total inference requests')
```

**Dashboard Integration**

```yaml
# Future Grafana dashboard configuration
dashboards:
  - name: "Olympus Models"
    panels:
      - title: "Model Load Times"
        type: "graph"
        metrics: ["model_load_seconds"]
      - title: "GPU Memory Usage"
        type: "gauge"
        metrics: ["gpu_memory_used"]
```

### Plugin System

**Example Plugin Interface**

```python
class ModelBackend(Protocol):
    async def load_model(self, name: str, config: Dict) -> bool:
        ...
    
    async def unload_model(self, name: str) -> bool:
        ...

class TensorRTBackend(ModelBackend):
    # Future TensorRT implementation
    pass
```

---

## Conclusion

By using **Docker** with a **CUDA 12.1** base image, we ensure compatibility with the stable vLLM release—avoiding issues tied to the host’s CUDA 12.4 environment. The Olympus Engine provides a robust foundation for model management and inference, and this document will be updated as new features are implemented and as we move towards Phase 2 of development.

For the latest updates and contributions, please refer to:

- **GitHub Repository**  
- **Documentation Wiki**  
- **Issue Tracker**  
- **Team Chat Channel**

Remember to check for updates to this document as the project evolves.

---

## Checklist

### Section 1: Environment Prerequisites

- [x] **Confirm Docker Installation**  
  - [x] Docker is installed (run `docker --version` to verify).  
  - [skip] (Optional) Docker Compose is installed (run `docker compose version` to verify).  
- [x] **Confirm GPU Support**  
  - [x] NVIDIA drivers are installed on the host machine.  
  - [x] NVIDIA Container Toolkit is installed (`nvidia-smi` works inside Docker, or follow official [NVIDIA docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)).  

### Section 2: Create/Edit the Dockerfile

- [x] **Dockerfile base image**  
  - [x] Confirm you’re using the desired CUDA version (e.g., `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`).  
- [ ] **Install system dependencies**  
  - [x] Confirm all packages you need (e.g., `python3.10`, `python3.10-venv`, `python3-pip`, etc.) are included.  
- [x] **Set up Python environment**  
  - [x] Python virtual environment created.  
  - [x] Requirements file (`requirements.txt` or similar) is copied over.  
  - [x] Packages in `requirements.txt` are installed correctly (`RUN /opt/venv/bin/pip install -r requirements.txt`).  
- [x] **Dockerfile cleanup**  
  - [x] Unused dependencies removed.  
  - [x] Proper `CMD` or entrypoint is set (e.g., `CMD ["/bin/bash"]`).  
  - **NOTE:** the docker container can be started with the start.sh script.

### Section 3: Build the Docker Image

- [x] **Build script or manual build**  
  - [x] Confirm `docker build -t olympus-engine:latest .` runs without errors.  
  - [x] Confirm the image (e.g., `olympus-engine:latest`) appears in `docker images`.  
- [x] **Troubleshoot build errors**  
  - [x] Handle any missing dependencies or version conflicts.  

### Section 4: Run the Container (Using Bash Script)

- [ ] **Create/Update `start.shj`**  
  - [ ] Ensure the script includes `docker run` with GPU support (`--gpus all`).  
  - [ ] Mount volumes correctly (`-v $(pwd):/workspace/olympus-engine`).  
  - [ ] Set the working directory (`-w /workspace/olympus-engine`).  
  - [ ] Include any environment variables (`-e NVIDIA_VISIBLE_DEVICES=all`).  
- [ ] **Make script executable**  
  - [ ] `chmod +x start.shj`.  
- [ ] **Execute script**  
  - [ ] `./start.shj` runs without errors and drops you into a bash shell in the container.  

### Section 5: Verify GPU Access in the Container

- [ ] **Check NVIDIA SMI**  
  - [ ] Run `nvidia-smi` inside the container and confirm GPU info is displayed.  
- [ ] **Verify GPU Libraries**  
  - [ ] Confirm any frameworks (e.g., PyTorch, TensorFlow) can see the GPU if required.  

### Section 6: Application Tests (Optional)

- [ ] **Run sample Python script**  
  - [ ] Verify your Python environment is activated (if needed, `source /opt/venv/bin/activate` or similar).  
  - [ ] Test any scripts that depend on GPU.  
- [ ] **Database or other dependencies**  
  - [ ] If you have a database (SQLite or otherwise), confirm it’s accessible.  

### Section 7: Cleanup and Next Steps

- [ ] **Shut down and remove container**  
  - [ ] Confirm you can exit the container (type `exit`) and that it removes itself if using `--rm`.  
- [ ] **Push image to registry (if desired)**  
  - [ ] Configure Docker Hub or a private registry.  
  - [ ] `docker tag` and `docker push` as needed.  

---

Use (or remove) whichever parts apply to your project. As each task is completed, you can replace the `[ ]` with `[x]` to track progress.

**End of Document**
