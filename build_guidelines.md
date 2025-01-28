# **Project Olympus: Prototype Build & Implementation Guide**

**Version:** 0.1.0 (Prototype)  
**Last Updated:** 2025-01-27  
**Status:** In Development (Early Prototype)

---

## **1. Introduction**

This guide outlines the early-stage (prototype) build for **Project Olympus**, focusing on:

1. **HADES** (Heuristic Adaptive Data Extraction System):  
   A Retrieval-Augmented Generation (RAG) solution leveraging ArangoDB as a combined vector-graph-document store.

2. **Olympus Model Engine**:  
   A dual-model system using ModernBERT for code understanding and embeddings, with a separate LLM for inference and generation tasks.

**Note**: Additional components of Olympus—such as **Agents** (autonomous task handling), **Delphi** (the primary UI), and **Ladon** (system monitoring)—remain part of the larger vision but will not be deeply addressed in this prototype phase.

---

## **2. High-Level Architecture**

Our current prototype architecture revolves around integrating **HADES** and the **Model Engine**:

```mermaid
graph TD
    H[HADES] --> ADB[ArangoDB]
    H --> ME[Model Engine (ModernBERT + LLM)]
    UI[Minimal Web UI] --> H
```

1. **HADES**:
   - Coordinates data ingestion and retrieval from ArangoDB.
   - Communicates with the Model Engine to perform LLM-powered query completion or question answering.
   - Exposes REST or GraphQL endpoints for a minimal frontend.

2. **ArangoDB**:
   - Stores documents, vectors, and knowledge-graph relationships.
   - Allows for hybrid queries (graph + vector + document).
   - Hosts basic text or embedding-based indexing.

3. **Model Engine (ModernBERT + LLM)**:
   - Manages both ModernBERT and LLM components
   - Generates embeddings and analyzes code structure
   - Provides inference capabilities for code understanding and generation
   - Maintains system's self-documentation through continuous analysis

4. **Minimal Web UI**:
   - A basic interface (React, Vue, or any other minimal web stack) for testing HADES queries.
   - Might eventually evolve into Delphi in later phases.

---

## **3. Prototype Scope**

### **3.1 HADES: RAG with ArangoDB**

- **Core Prototype Goals**:
  - Ingest documents or text into ArangoDB (both for graph + vector indexing).
  - Execute simple vector similarity searches combined with graph traversal or filtering.
  - Return relevant context to the Model Engine for generating a final answer or completion.

- **Key HADES Prototype Features**:
  1. **Vector Store Setup**:
     - ArangoDB “Smart Graph” or standard graph collections.
     - Embedding-based indexing for quick similarity search.
  2. **Basic Ingestion/Indexing API**:
     - Endpoint to push data (title, text, metadata).
     - Automatic embedding generation via a local or remote model.
  3. **Query Endpoint**:
     - Endpoint to accept user queries.
     - Retrieves top-N relevant documents (via vector similarity).
     - Optionally merges graph-based relationships (e.g., connected nodes).
  4. **Memory Management** (Simplified):
     - For now, we store all data in ArangoDB.
     - Future tiers (Elysium, Asphodel, Lethe) remain conceptual only.
  5. **Light Testing**:
     - Unit tests covering ingestion and retrieval logic.
     - Integration tests with ArangoDB + the Model Engine.

### **3.2 Model Engine**

- **Core Prototype Goals**:
  - Implement ModernBERT for code understanding and embedding generation
  - Build and maintain a rich knowledge graph of the system's own codebase
  - Provide efficient inference for code analysis and generation
  - Enable self-documenting capabilities through continuous code analysis

- **Key Model Engine Components**:

  1. **ModernBERT Integration**:
     - Code-aware embedding generation (8,192 token context)
     - Semantic code analysis and relationship inference
     - Continuous codebase understanding
     - Integration with ArangoDB's vector capabilities

  2. **Knowledge Graph Management**:
     - Automatic code relationship mapping
     - Function and module dependency tracking
     - System component relationship inference
     - Continuous graph updates as code evolves

  3. **LLM Integration**:
     - Efficient inference using available GPU resources
     - Context-aware code generation
     - Documentation generation and maintenance
     - Code review and analysis capabilities

  4. **Resource Management**:
     - Optimized GPU utilization across models
     - Efficient batch processing for embeddings
     - Smart context handling for long sequences
     - Memory-efficient model deployment

### **3.3 Minimal Web UI**

- **Core Prototype Goals**:
  - Provide a simple interface to test queries (searching documents or Q&A).
  - Display results returned by HADES (via the Model Engine).
  - Let developers manually validate the RAG + LLM pipeline.

- **Key UI Prototype Features**:
  1. **Search Bar**  
     - Input a user question or text.
  2. **Display Results**  
     - Show relevant documents fetched from HADES.
     - Show final LLM-generated answer.
  3. **Basic Feedback** (Optional)  
     - Provide a quick “thumbs up/down” on answer accuracy (just for local testing).

---

## **4. Development Environment & Setup**

### **4.1 Repository Structure (Prototype Focus)**

```test
olympus/
├── hades/
│   ├── api/            # REST endpoints
│   ├── core/           # Basic RAG logic
│   ├── models/         # Data schemas & embedding logic
│   └── utils/          # Helpers for ingestion, indexing
├── model_engine/
│   ├── src/            # ModernBERT + LLM service bootstrap
│   └── tests/          # Basic unit tests for model engine
├── minimal_ui/
│   └── src/            # Simple React/Vue or plain JS for testing
├── shared/
│   ├── config/         # ArangoDB connections, environment variables
│   └── utils/          # Shared utilities
└── docs/
```

> **Note**: This prototype avoids a full-scale organizational structure (like Agents, Ladon, or elaborate `delphi/` UI) to keep the focus on HADES + Model Engine integration.

### **4.2 Prerequisites**

- **Python 3.10 or higher**  
- **Docker & Docker Compose**  
- **ArangoDB** (5.x or higher recommended)  
  - Local or containerized installation  
- **Node.js 20+** (if building a simple Web UI frontend)

### **4.3 Installation Steps**

1. **Clone the Repository**  

   ```bash
   git clone https://github.com/your-org/olympus.git
   cd olympus
   ```

2. **Install Python Dependencies**  
   - **Using Poetry** (Recommended)

     ```bash
     poetry install
     ```

   - **Or Using Pip**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -e ".[dev]"
     ```

3. **Set Up Environment**  

   ```bash
   cp shared/config/.env.example .env
   # Edit .env to point to your ArangoDB host, Model Engine settings, etc.
   ```

4. **Start ArangoDB**  
   - **Using Docker**:

     ```bash
     docker run -d --name arangodb -p 8529:8529 \
       -e ARANGO_ROOT_PASSWORD=somepassword arangodb
     ```

   - **Or via Docker Compose** (if included in the repo):

     ```bash
     docker-compose up -d
     ```

5. **Initialize Database (Optional)**  
   - Create necessary collections (graph + documents) in ArangoDB.  
   - You can automate this in a script or do it via ArangoDB’s web UI.

---

## **5. Running the Prototype**

### **5.1 HADES Service**

1. **Configuration**  
   - Update any connection details in `shared/config/hades_config.py` (or `.env`).
2. **Launch**  

   ```bash
   cd hades
   uvicorn api.main:app --reload --port 8000
   ```

3. **Endpoints** (example):
   - `POST /api/docs` to ingest a document  
   - `GET /api/query?q=...` to query the RAG pipeline

### **5.2 Model Engine (ModernBERT + LLM)**

1. **Configuration**  
   - Point to your chosen base model (e.g., a smaller open-source LLM) in `model_engine/src/config.py`.
2. **Launch**  

   ```bash
   cd model_engine
   python src/run_model_engine.py
   ```

   - Exposes an endpoint, e.g., `http://localhost:9000/inference`.

### **5.3 Minimal Web UI**

1. **Install Dependencies**  

   ```bash
   cd minimal_ui
   npm install
   ```

2. **Run Dev Server**  

   ```bash
   npm run dev
   ```

3. **Usage**  
   - Access `http://localhost:3000` (or specified port).
   - Enter a query to test if HADES + Model Engine integration is working.

---

## **6. Testing**

1. **Unit Tests**  

   ```bash
   pytest --cov=hades hades/tests
   pytest --cov=model_engine model_engine/tests
   ```

2. **Integration Tests**  
   - Make sure ArangoDB is running.
   - Possibly use `pytest` with Docker or local services.  
   - Test ingestion + query flow all the way to the Model Engine.

3. **Performance Smoke Tests**  
   - Run a small script with multiple parallel queries to confirm everything holds up under moderate load.

---

## **7. Future Directions**

Though we are deferring many advanced features for now, it is important to keep them in mind:

1. **Expanding HADES**  
   - Enhanced RAG features (multi-hop graph queries, more refined retrieval strategies).  
   - Integration of advanced memory tiers (Elysium/Asphodel/Lethe) in a later production phase.

2. **Robust Model Engine**  
   - Fine-tuning pipeline (e.g., training/adapting with vLLM).  
   - Larger GPU-based deployments or multi-GPU distributed scaling.  
   - Additional prompt engineering and advanced inference endpoints.

3. **Delphi (Full Web UI)**  
   - Rich data visualization, agent orchestration, and advanced dashboards.  
   - Full integration with Agents and Ladon for monitoring.

4. **Agents + LadonStack**  
   - Autonomous scheduling, multi-agent collaboration, system metrics, and observability dashboards.  
   - Currently outside the scope of this prototype, but will eventually unify with HADES and the Model Engine.

### **7.1 RAG for Codebases: A Future Coding Agent**

A key evolution for HADES is to **index and analyze code** as richly as any other domain text. By leveraging ArangoDB’s combined vector/graph capabilities, you can build an **AI coding agent** that helps search, refactor, or maintain large codebases:

- **Hierarchical Graph Structure**  
  - Break the codebase into **application → module (folder) → class → function** nodes.  
  - Create edges to represent parent-child relationships (e.g., `APP_CONTAINS_MODULE`, `MODULE_CONTAINS_CLASS`, etc.) and imports (`IMPORTS` edges).

- **Semantic Search**  
  - Store vector embeddings for each function or class (with a code-focused model like CodeBERT or StarCoder).  
  - Query the codebase in natural language (“Where is GPU memory allocated?”) and retrieve relevant functions via vector similarity, plus relational context (who imports or calls those functions).

- **LLM Integration**  
  - Once top code snippets are retrieved, the Model Engine can generate refactoring suggestions, documentation, or new feature implementations using the assembled context.

- **Practical Benefits**  
  - Quickly locate relevant code in large projects.  
  - Provide deeper, relational “understanding” of how modules, classes, and functions interconnect.  
  - Streamline major refactors or expansions with minimal manual cross-referencing.

Although this code-centric approach is beyond the current prototype scope, **designing HADES with flexible graph + vector storage** sets you up for implementing such advanced features in the near future.

---

## **8. Conclusion**

This document describes the **prototype** build of Project Olympus, focusing on:

- **HADES**: A minimal but functional RAG system using ArangoDB.  
- **Model Engine**: A dual-model system using ModernBERT for code understanding and embeddings, with a separate LLM for inference and generation tasks.
- **Minimal Web UI**: A basic interface to test end-to-end query → retrieval → answer flows.

By limiting scope to these core functionalities, the team can validate the essential RAG pipeline and model integration early on, ensuring a stable foundation for future expansion into more advanced or production-ready features.

**Long-term**, consider expanding HADES to power an **AI coding agent** that deeply understands your codebase structure (application → module → class → function) and leverages LLMs for next-level development and refactoring assistance.

---

**End of Prototype Build & Implementation Guide**
