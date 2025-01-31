# Ollama & LangChain Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [LangChain Integration](#langchain-integration)
4. [Ollama API Reference](#ollama-api-reference)
5. [Best Practices](#best-practices)

## Overview

Ollama allows you to run open-source large language models (like Llama 2) locally on your device. Key benefits include:

- Privacy: Your data stays on your device
- Cost: No inference fees
- Flexibility: Support for various models and configurations

### Key Features

- Bundles model weights, configuration, and data into a single package
- Optimizes setup and configuration details, including GPU usage
- Supports both chat and completion models
- Provides local API server for model interaction

## Installation & Setup

### 1. Install Ollama

```bash
# Download and install Ollama for your platform
# Visit: https://ollama.ai/download

# Model storage locations:
# Mac: ~/.ollama/models
# Linux/WSL: /usr/share/ollama/.ollama/models
```

### 2. Install LangChain

```bash
pip install -U langchain-ollama
```

### 3. Pull a Model

```bash
# Pull a model (e.g., Llama 2)
ollama pull llama2

# List available models
ollama list

# Run model directly (CLI)
ollama run llama2
```

## LangChain Integration

### Chat Models (ChatOllama)

```python
from langchain_ollama import ChatOllama

# Initialize chat model
chat_model = ChatOllama(
    model="llama2",
    temperature=0
)

# Simple chat
response = chat_model.invoke("What is LangChain?")

# With system message
messages = [
    ("system", "You are a helpful assistant that translates English to French."),
    ("human", "I love programming.")
]
response = chat_model.invoke(messages)
```

### LLM Models (OllamaLLM)

```python
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Initialize LLM
llm = OllamaLLM(model="llama2")

# Create prompt template
template = """Question: {question}
Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)

# Create chain
chain = prompt | llm

# Use the chain
response = chain.invoke({"question": "What is LangChain?"})
```

### Multi-modal Support

Ollama supports multi-modal LLMs like bakllava and llava:

```python
# Pull multi-modal model
ollama pull bakllava

# Use with image input
# (See Ollama documentation for image handling)
```

## Ollama API Reference

### API Endpoints

Base URL: <http://localhost:11434/api>

#### Generate Completion

```bash
POST /api/generate
```

Parameters:

- `model`: (required) Model name (e.g., "llama2")
- `prompt`: The prompt text
- `stream`: Boolean to control streaming (default: true)
- `options`: Additional model parameters (temperature, etc.)
- `system`: System message override
- `format`: Response format (json or schema)

#### Chat Completion

```bash
POST /api/chat
```

Similar parameters to generate, but formatted for chat interactions.

### Model Management

```bash
# List models
GET /api/tags

# Pull model
POST /api/pull

# Delete model
DELETE /api/delete
```

## Best Practices

1. **Model Selection**
   - Start with smaller models for testing
   - Use larger models for more complex tasks
   - Consider quantized versions for better performance

2. **Performance Optimization**
   - Keep models loaded with appropriate `keep_alive` settings
   - Use streaming for real-time responses
   - Consider GPU acceleration when available

3. **Error Handling**
   - Implement proper error handling for API calls
   - Monitor model loading states
   - Handle timeouts appropriately

4. **Integration Patterns**
   - Use chat models for conversational tasks
   - Use LLMs for completion tasks
   - Leverage prompt templates for consistent interactions

5. **Security Considerations**
   - Run Ollama in isolated environments when needed
   - Monitor resource usage
   - Keep models and software updated

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangChain Documentation](https://python.langchain.com/docs/integrations/chat/ollama)
- [Model Library](https://ollama.ai/library)
