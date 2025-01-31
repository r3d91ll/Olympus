# Phase 1: Base System Build

## 1. Fedora 41 Installation

### 1.1 Base System
```bash
# Download Fedora 41 XFCE
# Create bootable USB using:
sudo dd if=Fedora-XFCE-Live.iso of=/dev/sdX bs=4M status=progress

# During installation:
# 1. Configure RAID arrays as per L1_hardware.md:
#   - md127: RAID0 (3× 1.8TB NVMe) for cache
#   - md126: RAID1 (2× 3.6TB NVMe) for system
#   - md125: RAID5 (5× 1TB NVMe) for home
```

### 1.2 Mount Points Setup
```bash
# Create logical volumes
sudo pvcreate /dev/md127 /dev/md126 /dev/md125
sudo vgcreate vg_fast /dev/md127
sudo vgcreate vg_system /dev/md126
sudo vgcreate vg_home /dev/md125

# Create and mount volumes as per L1_hardware.md
# vg_fast (RAID0)
sudo lvcreate -L 1.46T -n lv_mlcache vg_fast    # /opt/ml/cache
sudo lvcreate -L 1T -n lv_workspace vg_fast      # /opt/ml/workspace
sudo lvcreate -L 200G -n lv_syscache vg_fast     # /var/cache
sudo lvcreate -L 850G -n lv_ollama vg_fast       # /usr/share/ollama/.ollama
sudo lvcreate -L 48G -n lv_swap vg_fast          # [SWAP]

# vg_system (RAID1)
sudo lvcreate -L 500G -n lv_varlib vg_system     # /var/lib
sudo lvcreate -L 200G -n lv_varlog vg_system     # /var/log
sudo lvcreate -L 50G -n lv_etc vg_system         # /etc
sudo lvcreate -L 1.5T -n lv_mlmodels vg_system   # /opt/ml/models
sudo lvcreate -L 1T -n lv_olympus vg_system      # /opt/olympus
```

### 1.3 NVIDIA Setup
```bash
# Add RPM Fusion
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install NVIDIA drivers
sudo dnf install akmod-nvidia
sudo dnf install xorg-x11-drv-nvidia-cuda
```

## 2. ArangoDB Installation

### 2.1 Base Installation
```bash
# Create arangodb user
sudo useradd -r -d /var/lib/arangodb3 -s /sbin/nologin arangodb

# Install ArangoDB
curl -OL https://download.arangodb.com/arangodb311/RPM/arangodb3-3.11.5-1.0.x86_64.rpm
sudo dnf install ./arangodb3-3.11.5-1.0.x86_64.rpm

# Configure storage locations
sudo mkdir -p /opt/ml/workspace/arangodb
sudo chown -R arangodb:arangodb /opt/ml/workspace/arangodb

# Update ArangoDB configuration
sudo tee /etc/arangodb3/arangod.conf << EOF
[database]
directory=/opt/ml/workspace/arangodb

[server]
storage-engine=rocksdb
EOF
```

### 2.2 Initial Setup
```bash
# Initialize database
sudo systemctl start arangodb3
sudo arango-secure-installation

# Create initial databases
arangosh --server.username root --server.password <password> << EOF
db._createDatabase('hades');
db._useDatabase('hades');
db._createCollection('documents');
db._createCollection('embeddings');
EOF
```

## 3. Training Environment Setup

### 3.1 Python Environment
```bash
# Install Python tools
sudo dnf install python3.11-devel python3.11-pip

# Create virtual environment
python3.11 -m venv /opt/ml/workspace/venv
source /opt/ml/workspace/venv/bin/activate

# Install basic packages
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers sentence-transformers python-arango
```

### 3.2 Directory Structure
```bash
# Create necessary directories
sudo mkdir -p /opt/ml/{cache,workspace,models,projects}
sudo mkdir -p /opt/olympus

# Set permissions
sudo chown -R $USER:$USER /opt/ml
sudo chown -R $USER:$USER /opt/olympus
```

## 4. Development Environment Setup

### 4.1 CUDA and Development Tools
```bash
# Install CUDA Toolkit
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/fedora37/x86_64/cuda-fedora37.repo
sudo dnf clean all
sudo dnf module disable nvidia-driver
sudo dnf -y install cuda-toolkit-12-1

# Install development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install cmake ninja-build gcc-c++ git

# Install VSCode
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
sudo dnf install code

# VSCode Extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension ms-toolsai.jupyter
code --install-extension github.copilot
code --install-extension github.copilot-chat
```

### 4.2 Docker Setup
```bash
# Install Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo | \
  sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
sudo dnf install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 4.3 Ollama Installation
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configure Ollama storage location
sudo mkdir -p /usr/share/ollama/.ollama
sudo chown -R $USER:$USER /usr/share/ollama/.ollama

# Create Ollama service file
sudo tee /etc/systemd/system/ollama.service << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_MODELS=/usr/share/ollama/.ollama"
ExecStart=/usr/local/bin/ollama serve
User=$USER
Group=$USER
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Ollama
sudo systemctl daemon-reload
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull initial models
ollama pull llama2
ollama pull codellama
```

### 4.4 Additional Development Tools
```bash
# Install additional useful tools
sudo dnf install -y \
    htop \
    neofetch \
    tmux \
    ripgrep \
    fd-find \
    jq \
    yq \
    bat \
    exa \
    fzf \
    zoxide

# Install Node.js (for certain VSCode extensions)
sudo dnf module install nodejs:20/development

# Install Python development tools
pip install \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    pytest-asyncio \
    ipython \
    jupyter \
    jupyterlab
```

## 5. Verification Steps

### 5.1 System Checks
```bash
# Verify NVIDIA setup
nvidia-smi

# Verify ArangoDB
curl http://localhost:8529/_api/version

# Verify Python environment
python -c "import torch; print(torch.cuda.is_available())"
```

### 5.2 Initial Test
```python
# Test script: test_setup.py
from arango import ArangoClient
import torch
from sentence_transformers import SentenceTransformer

# Test ArangoDB connection
client = ArangoClient()
db = client.db('hades', username='root', password='<password>')
print("ArangoDB connection successful")

# Test CUDA
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")

# Test embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')
text = "Hello, world!"
embedding = model.encode(text)
print(f"Generated embedding shape: {embedding.shape}")
```

## Next Steps
1. Basic document ingestion pipeline
2. Simple embedding generation
3. Basic query functionality
4. Initial RAG implementation

## Notes
- All paths align with L1_hardware.md specifications
- System optimized for ML workloads
- Ready for Phase 2 expansion

## Environment Variables

Add to `~/.bashrc`:
```bash
# CUDA and development paths
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH

# Python environment
export PYTHONPATH=/opt/olympus:$PYTHONPATH

# Development tools
export EDITOR=code
export VISUAL=code

# Ollama settings
export OLLAMA_MODELS=/usr/share/ollama/.ollama
