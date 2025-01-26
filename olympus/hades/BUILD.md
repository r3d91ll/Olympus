# HADES Build Document

## Current State and Next Steps

HADES (Heuristic Adaptive Data Extraction System) is a sophisticated memory management system designed for large language models. This document outlines our current implementation state and the roadmap forward.

## Core Components

### 1. Three-Tiered Memory Management
- **Elysium (Hot Storage)**
  - GPU-resident memory
  - Active context windows
  - Real-time vector operations
  
- **Asphodel (Warm Storage)**
  - CPU memory
  - Recently accessed contexts
  - Compressed token storage
  
- **Lethe (Cold Storage)**
  - ArangoDB persistent storage
  - Vector embeddings with graph relationships
  - Triple-based knowledge representation

### 2. ArangoDB Integration
- Co-located with model in same container for minimal latency
- RocksDB storage engine optimized for vector operations
- Graph capabilities for relationship tracking
- Compression enabled for efficient vector storage

### 3. Monitoring via Ladon
Currently integrated with Phoenix monitoring system:
- Memory usage metrics per tier
- Operation latency tracking
- Cache hit/miss ratios
- Graph statistics
- Vector similarity distributions

Additional metrics can be added through `PhoenixMonitor` class.

## Immediate TODO List

### 1. Basic Functionality Implementation
```bash
# Proposed CLI workflow
olympus model download <model_name>  # Download model using model_engine
olympus model load <model_name>      # Load into memory management system
olympus embed <file_path>            # Generate and store embeddings
olympus query <query>                # Search stored embeddings
```

### 2. Core Components to Implement:
1. Model Engine Integration
   - Interface with `tests/model_engine`
   - Model download and validation
   - Model loading into memory tiers

2. File Processing Pipeline
   - File reading and chunking
   - Embedding generation
   - ArangoDB storage with relationships

3. Query Interface
   - Vector similarity search
   - Graph traversal for context
   - Result ranking and retrieval

### 3. Testing Requirements
1. Unit Tests
   - Memory tier operations
   - ArangoDB operations
   - Phoenix monitoring
   - Model operations

2. Integration Tests
   - End-to-end file processing
   - Model download and loading
   - Query performance
   - Memory management under load

## Technical Details

### Container Configuration
```dockerfile
# Key components in single container:
- NVIDIA CUDA runtime
- Python environment
- ArangoDB instance
- Model weights
- Vector storage
```

### Memory Management Flow
```python
# Example workflow
async def process_file(file_path: str):
    # 1. Load file
    chunks = chunk_file(file_path)
    
    # 2. Generate embeddings (Elysium tier)
    embeddings = await model.embed_chunks(chunks)
    
    # 3. Store in ArangoDB (Lethe tier)
    await store.store_embeddings(embeddings)
    
    # 4. Create relationships
    await store.create_relationships(embeddings)
```

### Monitoring Integration
```python
# Metrics exported to Phoenix
olympus_hades_memory_usage_bytes{component="model",tier="gpu"}
olympus_hades_operation_duration_seconds{component="arangodb",operation="vector_search"}
olympus_hades_cache_ratio{component="arangodb",tier="memory",status="hit"}
```

## Dependencies
- Python 3.10+
- CUDA 12.1
- ArangoDB 3.11.5
- PyTorch (latest)
- python-arango
- prometheus_client

## Next Steps
1. Implement basic CLI interface
2. Add model_engine integration
3. Create file processing pipeline
4. Write core tests
5. Add basic query functionality
6. Document API interfaces

## Notes
- All components are designed but not yet tested
- Basic functionality needs to be implemented
- Focus on CLI interface first, before any web API
- Testing will be critical for memory management
- Monitor memory usage patterns in co-located setup

## Future Considerations
1. Backup and restore procedures
2. Scaling strategies
3. Memory optimization techniques
4. Advanced graph queries
5. Custom embedding models
