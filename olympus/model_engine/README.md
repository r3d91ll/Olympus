# Model Engine

A lightweight wrapper around vLLM that provides an OpenAI-compatible API server for running LLMs.

## Features

- Simple process management for vLLM server
- OpenAI-compatible API endpoint
- Automatic model downloading and caching
- Graceful server shutdown
- Configurable model path and port

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from olympus.model_engine.core.engine import ModelEngine

# Create engine instance
engine = ModelEngine()

# Start server with a model (downloads if needed)
engine.start_server("Salesforce/codegen-350M-mono", port=8000)

# Server is now running at http://localhost:8000
# Use any OpenAI-compatible client to make requests:
# - POST /v1/completions
# - POST /v1/chat/completions

# When done, stop the server
engine.stop_server()
```

### OpenAI API Example

```python
import openai

# Point to local vLLM server
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "not-needed"

# Make completion request
response = openai.Completion.create(
    model="codegen-350M-mono",  # Model name doesn't matter
    prompt="def fibonacci(n):",
    max_tokens=100,
    temperature=0.7
)
print(response.choices[0].text)
```

## Configuration

The ModelEngine can be configured with:

- `model_path`: Directory for storing downloaded models (default: ~/.cache/olympus/models)
- `port`: Port for the API server (default: 8000)

Additional vLLM options like GPU selection and tensor parallelism will be added in future releases.

## Testing

Run the test suite:

```bash
python -m pytest tests/model_engine --cov=olympus.model_engine -v
```

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.
