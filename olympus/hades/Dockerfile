FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install ArangoDB
RUN curl -OL https://download.arangodb.com/arangodb311/DEBIAN/Release.key && \
    apt-key add - < Release.key && \
    echo 'deb https://download.arangodb.com/arangodb311/DEBIAN/ /' | tee /etc/apt/sources.list.d/arangodb.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y arangodb3=3.11.5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir bitsandbytes python-arango

# Copy source code
COPY src/ ./src/

# Configure ArangoDB for performance
COPY arangodb.conf /etc/arangodb3/arangodb.conf
RUN sed -i \
    -e 's/^endpoint.*/endpoint = tcp://127.0.0.1:8529/' \
    -e 's/^# storage-engine.*/storage-engine = rocksdb/' \
    -e 's/^# compression.*/compression = true/' \
    /etc/arangodb3/arangodb.conf

# Environment variables
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV ARANGO_NO_AUTH=1  # Since they're in the same container
ENV MALLOC_ARENA_MAX=4  # Optimize memory allocation

# Create startup script
COPY <<EOF /start.sh
#!/bin/bash
# Start ArangoDB in background
arangod --daemon --pid-file /var/run/arangodb3/arangod.pid --log.foreground true &
# Wait for ArangoDB to be ready
until curl -s http://127.0.0.1:8529/_api/version > /dev/null; do
    echo "Waiting for ArangoDB..."
    sleep 1
done
# Start FastAPI app
exec uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 1
EOF

RUN chmod +x /start.sh

CMD ["/start.sh"]
