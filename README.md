# Project Olympus

A comprehensive AI system composed of four specialized components working in harmony to provide intelligent data management, autonomous operations, monitoring, and user interaction.

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

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/olympus.git
cd olympus
```

2. Set up environment:
```bash
cp config/development/.env.example .env
```

3. Start the services:
```bash
docker-compose up -d
```

4. Initialize the system:
```bash
./scripts/setup/init.sh
```

## Development

Each component has its own development workflow and documentation:

- [HADES Development Guide](hades/docs/development.md)
- [Olympus Agents Guide](agents/docs/development.md)
- [Delphi Frontend Guide](delphi/docs/development.md)
- [LadonStack Integration](ladon/docs/integration.md)

## Documentation

- [System Architecture](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## License

See [LICENSE](LICENSE) file for details.
