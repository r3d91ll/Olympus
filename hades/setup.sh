#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    case $color in
        "green") echo -e "\033[0;32m$message\033[0m" ;;
        "red") echo -e "\033[0;31m$message\033[0m" ;;
        "yellow") echo -e "\033[1;33m$message\033[0m" ;;
    esac
}

# Check for required commands
print_status "yellow" "Checking prerequisites..."

required_commands=(
    "docker"
    "docker compose"
    "python3"
    "pip"
    "npm"
    "node"
)

for cmd in "${required_commands[@]}"; do
    if ! command_exists $cmd; then
        print_status "red" "Error: $cmd is not installed. Please install it first."
        exit 1
    fi
done

# Setup environment variables
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        print_status "yellow" "Creating .env file from env.example..."
        cp env.example .env
        print_status "yellow" "Please edit .env file with your desired settings"
    else
        print_status "red" "Error: Neither .env nor env.example file found"
        exit 1
    fi
fi

# Load environment variables
set -a
source .env
set +a

# Setup Python virtual environment
print_status "yellow" "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup RAM disk if it doesn't exist
if [ ! -d "/mnt/ramdisk" ]; then
    print_status "yellow" "Setting up RAM disk..."
    sudo mkdir -p /mnt/ramdisk
    sudo mount -t tmpfs -o size=64G tmpfs /mnt/ramdisk
    echo "tmpfs /mnt/ramdisk tmpfs size=64G 0 0" | sudo tee -a /etc/fstab
fi

# Start Docker services
print_status "yellow" "Starting Docker services..."
docker compose down 2>/dev/null
docker compose up -d

# Wait for services to be ready
print_status "yellow" "Waiting for services to be ready..."
max_attempts=30
attempt=1

# Check ArangoDB
while [ $attempt -le $max_attempts ]; do
    if curl -s -u "${ARANGO_USERNAME}:${ARANGO_PASSWORD}" "${ARANGO_URL}/_api/version" >/dev/null; then
        print_status "green" "ArangoDB is ready!"
        break
    fi
    print_status "yellow" "Attempt $attempt/$max_attempts: ArangoDB is not ready yet. Waiting..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    print_status "red" "Error: ArangoDB failed to start within the expected time."
    exit 1
fi

# Create database if it doesn't exist
print_status "yellow" "Creating/verifying database..."
curl -s -u "${ARANGO_USERNAME}:${ARANGO_PASSWORD}" "${ARANGO_URL}/_api/database" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${ARANGO_DATABASE}\"}" > /dev/null

# Setup frontend
print_status "yellow" "Setting up frontend..."
cd frontend
npm install
cd ..

# Setup logging directory
print_status "yellow" "Setting up logging directory..."
sudo mkdir -p ${LOG_DIR:-/var/log/hades}
sudo chown -R $USER:$USER ${LOG_DIR:-/var/log/hades}

print_status "green" "Setup completed successfully!"
print_status "yellow" "To start development:"
print_status "yellow" "1. Backend: python src/main.py"
print_status "yellow" "2. Frontend: cd frontend && npm run dev"
