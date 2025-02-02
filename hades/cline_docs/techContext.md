# HADES Technical Context

## Core Technologies

### 1. Learning Infrastructure
- **Qwen2.5-coder-instruct Model**
  - Base model for self-guided learning
  - Strong tool-use and coding abilities
  - Excellent reasoning capabilities
  - LoRA adapter support
  - Fine-tuning compatibility
  - Function calling support

### 2. Reference Library (ArangoDB)
- **ArangoDB 3.12+**
  - Documentation storage
  - Example query repository
  - Best practices library
  - Performance patterns
  - Vector search for similar examples
  - Graph storage for relationships

### 3. Learning Environment
- **Development Setup**
  - Fedora 41 XFCE base
  - NVIDIA drivers and CUDA
  - Development tools
  - ArangoDB tools
  - Training frameworks

### 4. Hardware Requirements
- **Training Resources**
  - AMD Threadripper 7960x
  - 2× NVIDIA RTX A6000 (48GB VRAM each)
  - 256GB ECC RDIMM RAM
  - High-speed storage for training data

- **Storage Configuration**
  - RAID0 (5.5TB) for high-speed cache
  - RAID1 (3.6TB) for system & ML storage
  - RAID5 (4TB) for home directory
  - RAID6 (planned, 60TB raw) for cold storage

## Development Stack

### 1. Core Dependencies
```toml
[dependencies]
python = "^3.11"
python-arango = "^7.9.0"  # ArangoDB driver
torch = "2.1.0+cu121"     # PyTorch with CUDA
transformers = "^4.36"    # Hugging Face
peft = "^0.7.0"          # LoRA support
datasets = "^2.16.0"     # Training data
accelerate = "^0.26.0"   # Training optimization
wandb = "^0.16.2"        # Experiment tracking
```

### 2. Training Tools
- VSCode with extensions:
  - Python
  - Jupyter
  - GitHub Copilot
  - Docker
  - Remote Development
  - Training visualization

### 3. Learning Monitoring
- Training progress tracking:
  - Weights & Biases
  - TensorBoard
  - Custom metrics
  - Learning curves
  - Skill assessment

## System Architecture

### 1. Learning Environment Layout
```text
/opt/
├── ml/
│   ├── training/     → RAID0 (Training data)
│   ├── workspace/    → RAID0 (Active learning)
│   ├── models/       → RAID1 (Qwen2.5 & LoRAs)
│   └── experiments/  → RAID5 (Training runs)
├── reference/        → RAID0 (ArangoDB library)
└── olympus/          → RAID1 (HADES system)
```

### 2. Training Configuration
```yaml
training:
  qwen2.5:
    model_id: "Qwen/Qwen2.5-14B-coder-instruct"
    training_args:
      per_device_train_batch_size: 4
      gradient_accumulation_steps: 4
      warmup_steps: 100
      max_steps: 1000
      learning_rate: 2e-5
      fp16: true
      
  lora:
    r: 16
    lora_alpha: 32
    lora_dropout: 0.1
    target_modules:
      - "q_proj"
      - "v_proj"
    
  datasets:
    arangodb_docs:
      path: "/opt/ml/training/arangodb"
      max_length: 2048
      num_proc: 8
```

## Training Environment Setup

### 1. Base System
```bash
# Core development tools
dnf groupinstall "Development Tools"
dnf install cmake ninja-build gcc-c++

# Training tools
pip install -U pip setuptools wheel
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Initialize training
wandb login
accelerate config
```

### 2. Training Stack
```bash
# NVIDIA setup
dnf install akmod-nvidia
dnf install cuda cuda-devel
dnf install nvidia-docker2

# Training optimization
dnf install nvme-cli
dnf install tuned
tuned-adm profile throughput-performance

# Monitoring tools
pip install wandb tensorboard
```

### 3. Reference Library Setup
```bash
# Install ArangoDB
curl -OL https://download.arangodb.com/arangodb312/RPM/arangodb3-3.12.0-1.0.x86_64.rpm
dnf install ./arangodb3-3.12.0-1.0.x86_64.rpm

# Configure for documentation storage
mkdir -p /opt/reference
chown -R arangodb:arangodb /opt/reference

# Initialize documentation store
cat > /etc/arangodb3/arangod.conf << EOF
[database]
directory=/opt/reference

[server]
storage-engine=rocksdb

[rocksdb]
total-write-buffer-size=512M
block-cache-size=512M

[arangosearch]
threads=8
EOF
```

## Deployment Configuration

### 1. Docker Setup
```yaml
version: '3.8'
services:
  arangodb:
    image: arangodb:3.12
    environment:
      - ARANGO_ROOT_PASSWORD=${ARANGO_PASSWORD}
    volumes:
      - arangodb_data:/opt/arangodb
    ports:
      - "8529:8529"
    command: >
      arangod
      --server.storage-engine=rocksdb
      --rocksdb.total-write-buffer-size=512M
      --rocksdb.block-cache-size=512M
      --arangosearch.threads=8

  decoder:
    image: ${DECODER_IMAGE}
    environment:
      - CUDA_VISIBLE_DEVICES=0,1
    volumes:
      - model_data:/opt/ml/models
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2
              capabilities: [gpu]
```

### 2. Environment Variables
```bash
# CUDA and development paths
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH

# Python environment
export PYTHONPATH=/opt/olympus:$PYTHONPATH

# Ollama settings
export OLLAMA_MODELS=/usr/share/ollama/.ollama
```

## Monitoring and Observability

### 1. Metrics Collection
- System metrics via Node Exporter
- GPU metrics via DCGM Exporter
- Custom metrics for:
  - Model performance
  - Memory tier transitions
  - Trust score evolution

### 2. Logging Strategy
- Structured logging with JSON format
- Log levels:
  - DEBUG: Development details
  - INFO: Normal operations
  - WARNING: Potential issues
  - ERROR: Operation failures
  - CRITICAL: System failures

### 3. Alerting Rules
```yaml
alerting:
  memory_pressure:
    warning: 75%    # Memory usage threshold
    critical: 90%   # Critical memory threshold
    
  model_performance:
    latency_ms: 100 # Max acceptable latency
    error_rate: 1%  # Max error rate
    
  trust_scores:
    min_threshold: 0.7  # Minimum acceptable trust
    alert_on_drop: true # Alert on score drops
```

## Security Considerations

### 1. Authentication
- ArangoDB authentication
- API key authentication
- JWT for session management

### 2. Authorization
- Role-based access control
- Resource-level permissions
- Audit logging

### 3. Data Protection
- Encryption at rest
- Secure communication
- Regular backups
