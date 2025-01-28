# Project Olympus Product Context

## Why this project exists
Project Olympus is an AI infrastructure platform designed to efficiently deploy and serve large language models (LLMs), manage scalable knowledge bases, and provide robust system monitoring and observability. It aims to standardize AI infrastructure across various applications.

## What problems it solves
1. **Efficient LLM Deployment and Serving**: Provides a lightweight model engine based on vLLM for serving LLMs with minimal resource overhead.
2. **Scalable Knowledge Management**: Utilizes ArangoDB as a combined vector-graph-document store to handle complex data retrieval and storage needs.
3. **System Monitoring and Observability**: Integrates LadonStack for comprehensive monitoring and observability of the AI system.

## How it should work
1. **HADES (Heuristic Adaptive Data Extraction System)**:
   - Coordinates data ingestion and retrieval from ArangoDB.
   - Communicates with the Model Engine to perform LLM-powered query completion or question answering.
   - Exposes REST or GraphQL endpoints for a minimal frontend.

2. **Model Engine**:
   - Serves an LLM via vLLM, handling inference requests from HADES.
   - Supports basic prompt engineering and can be extended for more advanced tasks like fine-tuning or distributed scaling.

3. **Minimal Web UI**:
   - Provides a simple interface to test queries and validate the RAG + LLM pipeline.