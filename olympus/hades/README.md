# Project Olympus

## Overview
Project Olympus is a comprehensive AI system composed of three primary components, each serving a specialized role in the ecosystem:

1. **H.A.D.E.S.** (Heuristic Adaptive Data Extraction System)
   - RAG-enabled database backend
   - Knowledge graph and vector storage
   - API/MCP server interface
   - Tiered memory management

2. **Olympus** (Agent Pool)
   - Specialized reasoning agents
   - System monitoring and maintenance
   - Resource optimization
   - Health checks and diagnostics

3. **Delphi** (Human Interface)
   - Unified frontend interface
   - Interactive dashboards
   - Visualization tools
   - Command center functionality

## HADES Component
HADES serves as the intelligent backend, organized into three memory tiers:
- **Elysium**: Active context and hot data storage
- **Asphodel**: Recent data and warm storage
- **Lethe**: Archived data and cold storage

### Core Features
- Advanced RAG capabilities
- Vector search integration
- Graph-based knowledge storage
- Real-time data processing
- MCP (Message Control Protocol) interface

## Setup and Installation
1. Clone the repository
2. Copy `.env.example` to `.env` and configure environment variables
3. Run `setup.sh` to initialize the development environment
4. Use `docker-compose up` to start the required services

## Development Requirements
- Python 3.9+
- Node.js 16+
- Docker and Docker Compose
- ArangoDB 3.9+

## Testing
- Unit tests: `pytest tests/`
- Integration tests: `pytest tests/integration/`
- Coverage reports: `pytest --cov=src tests/`

## Documentation
- API documentation in `/docs`
- Architecture details in `/docs/architecture`
- Component specifications in `/docs/specs`

## License
See LICENSE file for details.
