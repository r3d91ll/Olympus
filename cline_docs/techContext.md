# Project Olympus Tech Context

## Technologies used
1. **ArangoDB**: Version 5.x or higher (vector-graph-document store)
2. **vLLM**: Lightweight AI model engine for serving LLMs
3. **Python 3.10+**: Primary programming language for backend services
4. **Docker & Docker Compose**: For containerization and orchestration of services
5. **Node.js 20+**: For the Minimal Web UI frontend (React/Vue or plain JS)
6. **FastAPI**: Used in HADES for building RESTful APIs
7. **Pydantic v2**: For data validation and parsing in Python services
8. **pytest**: For unit and integration testing

## Development setup
1. **Repository Structure**:
   - `hades/`: Contains the HADES service with API, core logic, models, and utilities.
   - `model_engine/`: Contains the Model Engine service with vLLM inference code and tests.
   - `minimal_ui/`: Contains the Minimal Web UI frontend code.
   - `shared/`: Shared configuration files and utility functions used across services.

2. **Environment Setup**:
   - Clone the repository using Git.
   - Install Python dependencies using Poetry or a virtual environment with Pip.
   - Set up environment variables by copying `.env.example` to `.env`.
   - Start ArangoDB using Docker or Docker Compose.
   - Launch each service (HADES, Model Engine) and run the Minimal Web UI frontend.

3. **Tools and Libraries**:
   - **ArangoDB**: For data storage and retrieval.
   - **vLLM**: For serving LLMs.
   - **FastAPI**: For building RESTful APIs in HADES.
   - **Pydantic v2**: For data validation in Python services.
   - **pytest**: For testing both unit and integration aspects of the system.

## Technical constraints
1. **Resource Limitations**:
   - The prototype is designed to run on a CPU or single-GPU environment, with no advanced scheduling or distributed GPU support yet.
   - Minimal Web UI requires Node.js 20+ for frontend development.

2. **Scalability**:
   - While the current setup is suitable for prototyping, future enhancements will require more robust infrastructure for handling larger datasets and higher loads.

3. **Integration Complexity**:
   - The system relies on tight integration between HADES, the Model Engine, and the Minimal Web UI, which may introduce complexity in maintaining and scaling individual components.