# LadonStack

LadonStack is a comprehensive monitoring solution that integrates Phoenix, Prometheus, Grafana, Node Exporter, and DCGM Exporter to provide robust observability for your systems and applications.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone this repository:

   ``` shell
   git clone <your-repository-url>
   cd LadonStack
   ```

2. Create a `.env` file based on the `example.env` and fill in your desired configuration:

   ``` shell
   cp example.env .env
   ```

3. Start the stack:

   ``` shell
   docker-compose up -d
   ```

4. Access Grafana at `http://localhost:9300` (or the port you specified in `.env`)

## Connecting Grafana to Prometheus

1. Log in to Grafana (default credentials are in your `.env` file)
2. Go to Configuration > Data Sources
3. Click "Add data source"
4. Select "Prometheus"
5. Set the URL to `http://prometheus:9090`
6. Click "Save & Test"

## Setting up Dashboards

### Node Exporter Dashboard

1. In Grafana, click the "+" icon on the left sidebar
2. Select "Import"
3. Enter dashboard ID `1860` (or choose another from [Grafana's dashboard repository](https://grafana.com/grafana/dashboards/))
4. Select your Prometheus data source
5. Click "Import"

### DCGM Exporter Dashboard

1. Follow the same steps as above
2. Use dashboard ID `12239` for DCGM Exporter

You can find more dashboards at [Grafana's dashboard repository](https://grafana.com/grafana/dashboards/).

## System Monitoring Features

### Storage Monitoring

- LVM volume groups and logical volumes monitoring
- RAID array status monitoring (mdstat)
- Disk I/O and utilization metrics
- Mount point usage tracking

### System Metrics

- CPU usage per core
- System memory usage
- Storage performance metrics
- Docker container metrics

### Log Aggregation

- System logs from `/var/log`
- Docker container logs
- Systemd journal logs

## Installation

### Using Systemd (Recommended)

1. Clone this repository
2. Run the installation script:

   ```bash
   sudo ./install.sh
   ```

This will:

- Create necessary directories
- Install systemd services
- Start the monitoring stack
- Enable automatic startup on boot

### Managing the Service

```bash
# Check status
systemctl status ladon.service

# Stop the stack
systemctl stop ladon.service

# Start the stack
systemctl start ladon.service

# View logs
journalctl -u ladon.service
```

## Phoenix Setup

Phoenix is an AI Observability & Evaluation tool. While it's included in this stack, it's still in development.

- Docker container: [arizephoenix/phoenix](https://hub.docker.com/r/arizephoenix/phoenix)
- GitHub repository: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)

To interact with Phoenix, you can access it at:

- HTTP: `http://localhost:6006`
- gRPC: `localhost:4317`
- Prometheus metrics: `http://localhost:9091`

Refer to the [Phoenix documentation](https://github.com/Arize-ai/phoenix/blob/main/README.md) for more details on how to use and configure Phoenix.

## Phoenix Integration

Phoenix provides observability for LLM and RAG applications across the Olympus project. Access the Phoenix UI at `http://localhost:6006`.

### Connecting Applications to Phoenix

Phoenix exposes the following ports:

- 6006: Web UI
- 4317: gRPC (for sending traces)
- 9091: Prometheus metrics

#### LangChain Integration

To monitor LangChain applications (like RAG pipelines), add the Phoenix callback handler:

```python
from phoenix import Client
from phoenix.trace.langchain import PhoenixCallbackHandler

# Initialize Phoenix client
phoenix = Client(
    url="http://localhost:6006"  # Phoenix UI URL
)

# Create Phoenix callback
callbacks = [PhoenixCallbackHandler()]

# Use in your LangChain chain
chain = YourLangChainComponent()
result = chain.run(
    callbacks=callbacks,
    input="your input"
)
```

#### Advanced Features

1. **Project Organization**
   - Group traces by project:

   ```python
   callbacks = [PhoenixCallbackHandler(
       project_name="hades-rag"
   )]
   ```

2. **Custom Tags**
   - Add custom metadata to traces:

   ```python
   callbacks = [PhoenixCallbackHandler(
       tags={
           "environment": "production",
           "model": "gpt-4",
           "query_type": "semantic_search"
       }
   )]
   ```

3. **Trace Analysis**
   - View token usage
   - Track latency and performance
   - Analyze prompt templates
   - Monitor embedding quality
   - Debug RAG retrieval results

For more details on LangChain integration, visit the [Phoenix documentation](https://docs.arize.com/phoenix/tracing/integrations-tracing/langchain).

## Troubleshooting

If you encounter any issues:

1. Check the logs: `docker-compose logs`
2. Ensure all containers are running: `docker-compose ps`
3. Verify your `.env` file configuration
4. Restart the stack: `docker-compose down && docker-compose up -d`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).
