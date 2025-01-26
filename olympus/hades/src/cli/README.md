# HADES CLI

A command-line interface for the HADES memory management system.

## Commands

### Setup
Initialize HADES components:
```bash
python -m hades.cli setup [--db-host] [--db-name] [--node-exporter-path]
```

### Model Management
```bash
# List available models
python -m hades.cli model list

# Download a model
python -m hades.cli model download <model_name>

# Load a model into memory
python -m hades.cli model load <model_name>
```

### File Processing
```bash
# Generate embeddings for a file
python -m hades.cli embed <file_path> [--chunk-size] [--overlap]
```

### Querying
```bash
# Search stored embeddings
python -m hades.cli query <query_text> [--limit] [--min-similarity]
```

## Examples

```bash
# Basic workflow
python -m hades.cli setup
python -m hades.cli model download gpt2-medium
python -m hades.cli model load gpt2-medium
python -m hades.cli embed documents/sample.txt
python -m hades.cli query "What is machine learning?"
```

## TODO
- [ ] Implement model_engine integration
- [ ] Add file chunking functionality
- [ ] Implement embedding generation
- [ ] Add proper result formatting
- [ ] Add progress tracking
- [ ] Add model validation
