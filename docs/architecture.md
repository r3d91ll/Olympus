# Project Olympus Architecture

## System Overview

```mermaid
graph TD
    subgraph Delphi[Delphi - Human Interface]
        UI[User Interface]
        Dashboard[Dashboards]
        Controls[System Controls]
    end

    subgraph Olympus[Olympus - Agent Pool]
        Agents[Specialized Agents]
        Scheduler[Task Scheduler]
        Optimizer[Resource Optimizer]
    end

    subgraph HADES[HADES - Backend]
        MCP[MCP Server]
        RAG[RAG Engine]
        Vector[Vector Store]
        Graph[Knowledge Graph]
        Memory[Memory Management]
    end

    subgraph LadonStack[LadonStack - Monitoring]
        Metrics[Metrics Collection]
        Logs[Log Aggregation]
        Traces[Distributed Tracing]
        Alerts[Alert Management]
        Health[Health Checks]
    end

    subgraph ModelEngine[Olympus Model Engine]
        ModelAPI[Model API]
        ModelRegistry[Model Registry]
        Inference[Inference Engine]
        Training[Training Pipeline]
        Optimization[Model Optimization]
    end

    %% Delphi to HADES
    UI --> |Queries| MCP
    Controls --> |Commands| MCP
    MCP --> |Responses| UI

    %% Delphi to Olympus
    UI --> |Task Requests| Agents
    Agents --> |Task Status| Dashboard

    %% LadonStack Monitoring
    Metrics --> |System Metrics| Dashboard
    Logs --> |Log Data| Dashboard
    Alerts --> |Alert Status| Dashboard
    Health --> |Health Status| Dashboard

    %% LadonStack to Components
    Metrics -.-> |Monitor| HADES
    Metrics -.-> |Monitor| Olympus
    Metrics -.-> |Monitor| Delphi
    Metrics -.-> |Monitor| ModelEngine
    Logs -.-> |Collect| HADES
    Logs -.-> |Collect| Olympus
    Logs -.-> |Collect| Delphi
    Logs -.-> |Collect| ModelEngine
    Health -.-> |Check| HADES
    Health -.-> |Check| Olympus
    Health -.-> |Check| ModelEngine
    Traces -.-> |Trace| MCP
    Traces -.-> |Trace| ModelAPI

    %% ModelEngine Connections
    ModelAPI --> |Model Requests| HADES
    ModelAPI --> |Inference| Agents
    ModelRegistry --> |Model Info| MCP
    Training --> |New Models| ModelRegistry
    Optimization --> |Optimized Models| ModelRegistry

    %% Olympus to HADES
    Agents --> |Data Requests| MCP
    Scheduler --> |Maintenance Tasks| Memory

    %% HADES Internal
    MCP --> RAG
    RAG --> Vector
    RAG --> Graph
    Memory --> Vector
    Memory --> Graph

    style Delphi fill:#ffd700,stroke:#333
    style Olympus fill:#ff69b4,stroke:#333
    style HADES fill:#4169e1,stroke:#333
    style LadonStack fill:#32cd32,stroke:#333
    style ModelEngine fill:#ff6347,stroke:#333
```

## Component Responsibilities

### HADES (Backend)
- **MCP Server**: Message Control Protocol server for handling all external communications
- **RAG Engine**: Retrieval Augmented Generation for intelligent query processing
- **Vector Store**: Efficient storage and retrieval of embeddings
- **Knowledge Graph**: Relationship and context management
- **Memory Management**: Tiered data lifecycle management (Elysium, Asphodel, Lethe)

### Olympus (Agent Pool)
- **Specialized Agents**: Task-specific AI agents for system operations
- **Task Scheduler**: Orchestration of system tasks
- **Resource Optimizer**: System resource optimization

### Delphi (Human Interface)
- **User Interface**: Primary interaction point for users
- **Dashboards**: Real-time visualization
- **System Controls**: Configuration and control interface

### LadonStack (Monitoring)
- **Metrics Collection**: System and application metrics gathering
- **Log Aggregation**: Centralized logging system
- **Distributed Tracing**: Request tracing across components
- **Alert Management**: Intelligent alerting system
- **Health Checks**: Component and system health monitoring

### Olympus Model Engine
- **Model API**: Unified interface for model operations
- **Model Registry**: Central repository for model management
- **Inference Engine**: Optimized inference execution
- **Training Pipeline**: Model training and fine-tuning
- **Model Optimization**: Quantization and optimization tools

## Integration Notes

### Model Engine Decoupling
The current model management functionality in HADES may need to be decoupled and integrated with the Olympus Model Engine in the future. This decision will be based on:

1. **Operational Requirements**
   - Performance needs
   - Resource utilization
   - Scaling patterns

2. **Architectural Considerations**
   - Service boundaries
   - Data flow patterns
   - System coupling

3. **Migration Strategy**
   - Gradual transition
   - Backward compatibility
   - Service discovery

The decoupling process will be evaluated based on system usage patterns and performance requirements.
