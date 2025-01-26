# Deployment Overview: Single Container

In this setup, **Project Olympus** runs in a single container. Its primary role is to provide:

- A **Streamlit-based chat interface** for conversational AI.
- Integration with **Hugging Face** to download and manage locally run models.
- (Optional) Tools for RAG workflows, such as encoding and querying external data stores.

---

## Olympus Build Requirements

### Overview

The Olympus container serves as the execution environment for the project. It provides a streamlined interface for interacting with Hugging Face models, supports RAG workflows, and hosts a chat interface. Below are the core requirements:

1. **Hugging Face Model Integration**  
   - Enable downloading and running quantized or full-sized models from Hugging Face.  
   - Provide a pure Python-based workflow to manage and execute these models locally.

2. **Chat Interface**  
   - Support a simple Streamlit-based chat interface for model interaction.  
   - Handle conversational context and (optionally) session persistence.

3. **RAG Integration (Optional)**  
   - Provide an optional mechanism for uploading files and folders for indexing.  
   - Offer tools for embedding and querying data to support RAG workflows.

---

### Key Components and Dependencies

1. **Core Features**  
   - **Python Environment**: Ensure compatibility with Python 3.12+.  
   - **Required Libraries** (example):
     - **Streamlit** for the front-end.
     - **Hugging Face Transformers** for model integration.
     - **torch** to support model inference.
     - **SentenceTransformers** (or similar) for optional RAG encoding tasks.

2. **Streamlit Front-End**  
   - Configured to launch on container startup.
   - Provide dedicated tabs or pages for:
     - **Chat interaction** (main feature).
     - **File/folder uploads** for optional RAG indexing.
     - **Model management** (download, update, and execution).

3. **Hugging Face Model Integration**  
   - Use `transformers` and `torch` for locally running models.
   - Download quantized models via the Hugging Face Hub.
   - Manage model versions and dependencies as needed.

4. **(Optional) RAG Database Integration**  
   - If you choose to include a RAG component, ensure your container has the required dependencies (e.g., `sentence-transformers` or any embedding library).  
   - Provide a Python-based interface to store and query embedded data.  
   - This can be as simple as an on-disk vector store or an external database service (configured separately).

5. **Logging and Monitoring**  
   - **Structured Logging**:
     - Integrate Python’s `logging` module to track user interactions and data flow.
   - Include basic metrics for performance monitoring where applicable.

---

### Build Instructions

1. **Base Image**  
   - Use an official Python image as the base, such as `python:3.9-slim`.

2. **Installing Dependencies**  
   - Maintain a `requirements.txt` with the relevant Python libraries, for example:

     ```plaintext
     streamlit
     transformers
     torch
     sentence-transformers
     ```

   - Install them in your Dockerfile with `pip install`.

3. **Setting Up the Application**  
   - Copy the application code into the container with a structure like:

     ```plaintext
     /app
       |-- /services
       |-- /frontend
       |-- main.py
     ```

   - `main.py` (or similarly named file) should contain the Streamlit entry point.

4. **Exposing Ports**  
   - Default port for the Streamlit front-end: **8501**.

5. **Dockerfile Example**  

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY . /app

   RUN pip install --no-cache-dir -r requirements.txt

   CMD ["streamlit", "run", "main.py"]
   ```

---

### Networking and Container Configuration

1. **Docker Network**  
   - If you choose to run additional services (e.g., an external database or vector store) separately, ensure they share a network so Olympus can query them.  

2. **Environment Variables**  
   - Store credentials (e.g., Hugging Face tokens) in a `.env` file or pass them as Docker environment variables.

3. **Health Checks**  
   - Add health checks to ensure the Streamlit front-end is up:

     ```yaml
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:8501"]
       interval: 30s
       timeout: 10s
       retries: 3
     ```

---

### Modular and Layered Architecture

To keep the system **flexible** for future expansions:

- **Encapsulate Future Upgrades**: If you add more components (e.g., orchestrators like “Apollo” or advanced RAG services), they can be built into separate modules or containers.  
- **Support Scalability**: A layered design ensures you can scale specific components without impacting the entire system.  
- **Enhance Maintainability**: Isolate modules such as chat, RAG uploads, and model management to simplify debugging and testing.

---

## Operational Notes

1. **Starting the Container**  
   - Spin up the Olympus container, which launches Streamlit on port **8501** by default.  

2. **Data Initialization**  
   - If using a RAG approach, you may need to initialize any external storage, embedding pipelines, or indexing processes (handled within `main.py` or a separate script).

3. **Security & Credentials**  
   - Use environment variables for sensitive credentials (e.g., Hugging Face tokens).  
   - Consider Docker secrets or environment variable managers (like Vault) in production.

---

## References & Related Links

1. **Hugging Face**  
   - [Transformers Documentation](https://huggingface.co/docs/transformers/index)  
   - Learn about loading different model architectures, quantization, and tokenizers.

2. **Streamlit**  
   - [Streamlit Docs](https://docs.streamlit.io/)  
   - Guidance on building interactive UIs in Python.

3. **Optional: Vector or RAG Storage**  
   - [Sentence Transformers](https://www.sbert.net/)  
   - Guidance on embedding text for vector-based retrieval.  
   - This can be integrated with an external vector store (e.g., Pinecone, Weaviate) or a local on-disk solution.

4. **Docker**  
   - [Docker Compose](https://docs.docker.com/compose/)  
   - If you plan to orchestrate multiple services (e.g., a separate database), provide a `docker-compose.yml` that includes both containers on a shared network.

---

By **focusing on a single Olympus container** that serves a **simple chat interface** and **Hugging Face model downloads**, this document provides a straightforward roadmap for teams looking to spin up a local or cloud-based conversational AI service.
