# System Patterns

## How the system is built
- Modular architecture with separate components for HADES, Model Engine, and LadonStack
- Each component has its own directory and configuration files
- Components communicate through well-defined APIs

## Key technical decisions
- Use of Docker Compose for managing multi-container applications
- Integration of ArangoDB for knowledge management in HADES
- Lightweight vLLM wrapper for the Model Engine to provide OpenAI-compatible API
- Monitoring and observability platform (LadonStack) integrated with Phoenix for LLM/RAG monitoring

## Architecture patterns
- Three-tier memory system in HADES: Elysium (Hot Storage), Asphodel (Warm Storage), Lethe (Cold Storage)
- RAG operations and knowledge processing handled by HADES
- Model loading, serving, and process management handled by the Model Engine
- Metrics collection and visualization handled by LadonStack

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]
