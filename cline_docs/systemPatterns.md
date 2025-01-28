# Project Olympus System Patterns

## How the system is built
Project Olympus is built using a modular architecture with clear separation of concerns:

1. **HADES (Heuristic Adaptive Data Extraction System)**:
   - **API Layer**: Exposes REST or GraphQL endpoints for data ingestion and retrieval.
   - **Core Logic**: Handles RAG operations, including vector similarity searches and graph traversal.
   - **Data Models**: Defines schemas and embedding logic for data storage in ArangoDB.

2. **Model Engine**:
   - **Inference Service**: Serves LLMs via vLLM, handling inference requests from HADES.
   - **Configuration Management**: Manages model settings and configurations.
   - **Monitoring**: Provides basic monitoring capabilities to track service performance.

3. **Minimal Web UI**:
   - **Frontend Application**: A simple interface for testing queries and displaying results from the RAG + LLM pipeline.
   - **Integration with HADES**: Communicates with HADES endpoints to fetch data and display results.

## Key technical decisions
1. **ArangoDB**: Chosen as the vector-graph-document store due to its ability to handle hybrid queries (graph + vector + document) and support for embedding-based indexing.
2. **vLLM**: Selected for the Model Engine due to its lightweight footprint and suitability for prototyping LLM inference services.
3. **REST/GraphQL Endpoints**: Used for communication between HADES, the Model Engine, and the Minimal Web UI to ensure flexibility and ease of integration.

## Architecture patterns
1. **Microservices Architecture**: Each component (HADES, Model Engine, Minimal Web UI) is designed as a separate service with well-defined interfaces.
2. **Event-Driven Design**: Components communicate through events where possible, promoting loose coupling and scalability.
3. **Modular Codebase**: The codebase is organized into modules to facilitate easy maintenance and extension of individual components.