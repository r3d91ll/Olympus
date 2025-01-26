# Project Olympus

A comprehensive AI system composed of four specialized components working in harmony to provide intelligent data management, autonomous operations, monitoring, and user interaction.

## Project Structure

```text
olympus/
├── hades/              #Heuristic Adaptive Data Extraction System
│   ├── api/           # REST API endpoints
│   ├── core/          # Core RAG and knowledge graph functionality
│   ├── models/        # Data models and schemas
│   └── utils/         # HADES-specific utilities
├── agents/            # Olympus Agents
│   ├── api/           # Agent communication endpoints
│   ├── core/          # Agent core logic and reasoning
│   ├── models/        # Agent models and types
│   └── utils/         # Agent-specific utilities
├── delphi/            # User Interface and Visualization
│   ├── api/           # UI backend endpoints
│   ├── core/          # Core UI logic
│   ├── models/        # UI state and data models
│   └── utils/         # UI utilities
├── ladon/             # System Monitoring and Management
│   ├── api/           # Monitoring endpoints
│   ├── core/          # Core monitoring logic
│   ├── models/        # Monitoring models
│   └── utils/         # Monitoring utilities
└── shared/            # Shared Components
    ├── config/        # Configuration management
    ├── types/         # Shared type definitions
    └── utils/         # Common utilities
```

## Core Components

### HADES (Hierarchical Adaptive Data Extraction System)

- RAG-enabled database backend
- Knowledge graph and vector storage
- API/MCP server interface
- Tiered memory management

### Olympus Agents

- Specialized reasoning agents
- Task scheduling and execution
- Resource optimization
- System automation

### Delphi

- Unified human interface
- Interactive dashboards
- Visualization tools
- Command center functionality

### LadonStack

- System and application monitoring
- Log aggregation and analysis
- Distributed tracing
- Alert management
- Health monitoring
- Storage performance tracking (LVM, RAID)
- System metrics collection
- Automated startup via systemd
- Persistent data storage
- Docker container monitoring
- LLM/RAG observability with Phoenix:
  - Token usage tracking
  - Latency monitoring
  - Prompt template analysis
  - Embedding quality metrics
  - RAG retrieval debugging
  - Cross-component trace correlation

## Monitoring Infrastructure

### System Monitoring

- Prometheus for metrics collection
- Grafana for visualization
- Node Exporter for system metrics
- DCGM Exporter for GPU metrics
- Loki for log aggregation

### LLM/RAG Monitoring

- Phoenix observability platform
- LangChain integration
- Project-based trace organization
- Custom tagging support
- Performance analytics
- Debugging tools

## Development

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Poetry (recommended) or pip

### Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/your-org/olympus.git
    cd olympus
    ```

2. Install dependencies:

    ```bash
    # Using poetry (recommended)
    poetry install

    # Using pip
    pip install -e ".[dev]"
    ```

3. Set up environment:

    ```bash
    cp config/development/.env.example .env
    ```

4. Start services:

    ```bash
    docker-compose up -d
    ```

### Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=olympus
```

### Code Quality

```bash
# Format code
black olympus tests
isort olympus tests

# Type checking
mypy olympus

# Linting
flake8 olympus tests
```

## Documentation

- API documentation is available in `docs/api/`
- Architecture details in `docs/architecture/`
- Deployment guides in `docs/deployment/`

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.
