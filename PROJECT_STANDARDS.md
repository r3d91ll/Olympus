# Olympus Project Standards and Architecture

## Important Project Documents

- `README.md` - Primary project documentation and getting started guide
- `BUILD-alt.md` - Alternative build instructions and configurations
- `CONTRIBUTING.md` - Contribution guidelines and processes
- `KANBAN.md` - Project management and task tracking
- `research_notes.md` - Research findings and technical decisions
- `docs/` - Detailed documentation directory

## Project Overview

Olympus is a custom-built machine learning infrastructure system consisting of three main components:

1. **HADES** (Heuristic Adaptive Data Extraction System)
   - Three-tier memory system:
     - Elysium (Hot Storage)
     - Asphodel (Warm Storage)
     - Lethe (Cold Storage)
   - Core component for data management and storage

2. **Model Engine**
   - ML model management and execution
   - Model versioning and deployment
   - Training pipeline orchestration

3. **Delphi**
   - Frontend interface
   - Visualization and monitoring
   - User interaction layer

## Development Standards

### Python Version and Environment

- **Python Version**: 3.8.x (standardized across all modules)
- **Virtual Environment**: Use `.venv` in project root
- **Package Management**: Single unified `requirements.txt` at project root

### Code Organization

```text
Olympus/                         # Root project directory
├── olympus/                     # Main code directory
│   ├── agents/                  # Agent implementations
│   ├── config/                  # Configuration management
│   ├── continual_learning/      # Continuous learning systems
│   ├── delphi/                  # Frontend interface
│   │   ├── src/
│   │   └── tests/
│   ├── hades/                   # Data management system
│   │   ├── src/
│   │   │   ├── model/
│   │   │   ├── processing/
│   │   │   └── cli/
│   │   └── tests/
│   ├── ladon/                   # Additional component
│   ├── model_configs/           # Model configuration files
│   ├── model_engine/           # ML model management
│   │   ├── src/
│   │   └── tests/
│   └── shared/                 # Shared utilities
├── docs/                       # Project documentation
├── scripts/                    # Utility scripts
├── shared/                     # Global shared resources
└── tests/                     # Top-level integration tests
```

### Coding Standards

1. **Style Guide**
   - Follow Google Python Style Guide
   - Use Black for formatting (line length: 88)
   - Use isort for import sorting
   - Use flake8 for linting
   - Use mypy for type checking

2. **Function Design**
   - Use functional programming paradigms
   - Implement RORO (Receive Object, Return Object) pattern
   - Use type hints consistently
   - Descriptive variable names with auxiliary verbs

3. **Error Handling**
   - Early returns for error conditions
   - Custom error types per module
   - Comprehensive error logging
   - User-friendly error messages

### Testing Strategy

1. **Unit Tests**
   - Framework: pytest
   - Coverage requirement: minimum 80%
   - Run tests in isolation
   - Mock external dependencies

2. **Integration Tests**
   - Test inter-module communication
   - End-to-end workflows
   - Performance benchmarks

3. **Test Tools**
   - pytest-asyncio for async tests
   - pytest-cov for coverage
   - pytest-mock for mocking
   - pytest-xdist for parallel execution

### Documentation

1. **Code Documentation**
   - Google-style docstrings
   - Type hints for all functions
   - Module-level docstrings
   - README.md in each module

2. **API Documentation**
   - OpenAPI/Swagger for REST endpoints
   - Function signatures and examples
   - Error scenarios and handling

### Performance Guidelines

1. **Asynchronous Operations**
   - Use async/await for I/O operations
   - Implement connection pooling
   - Batch operations where possible

2. **Caching Strategy**
   - Redis for hot cache
   - Implement cache invalidation
   - Cache warming strategies

### Installation and Deployment

1. **Dependencies**
   - Single requirements.txt at project root
   - Version pinning for all packages
   - Regular dependency updates
   - Hardware-specific optimizations

2. **Environment Setup**

   ```bash
   python3.8 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Development Workflow

1. **Version Control**
   - Feature branches from main
   - Pull request reviews
   - Conventional commits
   - Semantic versioning

2. **CI/CD**
   - Automated testing
   - Style checking
   - Type checking
   - Coverage reporting

## Hardware Requirements

- Specific hardware configurations
- GPU requirements
- Memory requirements
- Storage requirements

## Monitoring and Logging

1. **Logging Standards**
   - Use loguru for consistent logging
   - Log levels and their usage
   - Log rotation and retention

2. **Monitoring**
   - Performance metrics
   - Error tracking
   - Resource utilization

## Security

1. **Code Security**
   - Dependency scanning
   - Code scanning
   - Secret management
   - Access control

2. **Data Security**
   - Encryption standards
   - Access patterns
   - Backup strategies
