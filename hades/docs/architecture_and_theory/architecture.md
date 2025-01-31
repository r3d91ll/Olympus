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
    Logs -.-> |Collect| HADES
    Logs -.-> |Collect| Olympus
    Logs -.-> |Collect| Delphi
    Health -.-> |Check| HADES
    Health -.-> |Check| Olympus
    Traces -.-> |Trace| MCP

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

## Data Flow

1. **User Interaction Flow**
   - User submits query through Delphi UI
   - Request routed to HADES via MCP
   - RAG engine processes query using Vector Store and Knowledge Graph
   - Response returned through MCP to UI

2. **System Management Flow**
   - Olympus agents handle system operations
   - LadonStack monitors all components
   - Metrics and logs collected centrally
   - Alerts trigger automated responses

3. **Memory Management Flow**
   - New data enters through Elysium
   - Aging data moves to Asphodel
   - Archived data stored in Lethe
   - Performance metrics tracked by LadonStack

## Communication Protocols

1. **External Communication**
   - REST APIs for synchronous requests
   - WebSocket for real-time updates
   - GraphQL for complex data queries

2. **Internal Communication**
   - MCP for inter-component messaging
   - gRPC for high-performance internal calls
   - OpenTelemetry for monitoring data

3. **Monitoring Protocols**
   - Prometheus metrics format
   - OpenTelemetry tracing
   - Structured logging (JSON)
   - SNMP for network monitoring

## Security Model

1. **Authentication**
   - JWT-based user authentication
   - API key management for services
   - Role-based access control

2. **Data Protection**
   - End-to-end encryption
   - Secure WebSocket connections
   - Encrypted data at rest

3. **Monitoring Security**
   - Secure metrics collection
   - Encrypted log transport
   - Authenticated monitoring endpoints
   - Audit logging
