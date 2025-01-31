# Layer 6: Query and Presentation Layer

## Overview

Layer 6 serves as the interface layer of HADES, handling:

1. Query Processing and Routing
2. Response Generation and Formatting
3. API Endpoints and Integration
4. Visualization and Presentation

### Architecture Components

1. **Query Router**

```python
async def process_query(query_data: dict) -> dict:
    """Process and route incoming queries based on type and context."""
    
    if not is_valid_query(query_data):
        return create_error_response("Invalid query format")
        
    query_type = determine_query_type(query_data)
    
    match query_type:
        case "knowledge_graph":
            return await route_to_graph_handler(query_data)
        case "vector_search":
            return await route_to_vector_handler(query_data)
        case "hybrid":
            return await route_to_hybrid_handler(query_data)
        case _:
            return create_error_response("Unsupported query type")
```

2. **Response Generator**

```python
async def generate_response(query_result: dict, format_type: str) -> dict:
    """Generate formatted responses based on query results."""
    
    # Validate and sanitize results
    cleaned_result = sanitize_result(query_result)
    
    # Apply trust score filtering
    if cleaned_result.trust_score < MIN_TRUST_THRESHOLD:
        return create_low_trust_response(cleaned_result)
    
    # Format based on requested type
    match format_type:
        case "json":
            return format_json_response(cleaned_result)
        case "graph":
            return format_graph_response(cleaned_result)
        case "text":
            return format_text_response(cleaned_result)
        case "visualization":
            return format_visualization_response(cleaned_result)
```

3. **API Interface**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="HADES Query Interface")

class QueryRequest(BaseModel):
    query_text: str
    query_type: str = "hybrid"
    response_format: str = "json"
    trust_threshold: float = 0.7
    context_depth: int = 2

@app.post("/query")
async def handle_query(request: QueryRequest):
    """Main query endpoint."""
    try:
        # Process query
        query_result = await process_query({
            "text": request.query_text,
            "type": request.query_type,
            "trust_threshold": request.trust_threshold,
            "context_depth": request.context_depth
        })
        
        # Generate response
        return await generate_response(
            query_result, 
            request.response_format
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": await check_component_health()
    }
```

4. **Visualization Engine**

```python
async def create_visualization(data: dict, viz_type: str) -> dict:
    """Create visualizations based on query results."""
    
    match viz_type:
        case "knowledge_graph":
            return await create_graph_visualization(data)
        case "timeline":
            return await create_timeline_visualization(data)
        case "heatmap":
            return await create_heatmap_visualization(data)
        case "relationship":
            return await create_relationship_visualization(data)
```

### Integration Points

1. **With Layer 5 (Orchestration)**

```python
async def coordinate_with_orchestrator(query: dict) -> dict:
    """Coordinate query processing with Layer 5."""
    
    # Get orchestration context
    context = await layer5.get_query_context(query)
    
    # Apply context-aware routing
    if context.requires_validation:
        return await route_to_validation_flow(query, context)
    
    # Handle standard flow
    return await route_to_standard_flow(query, context)
```

2. **With Layer 4 (Inference)**

```python
async def enrich_with_inference(response: dict) -> dict:
    """Enrich responses with inference layer insights."""
    
    # Get relevant inferences
    inferences = await layer4.get_inferences(response)
    
    # Merge and format
    enriched_response = merge_inferences(response, inferences)
    
    return format_enriched_response(enriched_response)
```

### Performance Optimizations

1. **Query Caching**

```python
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=1000)
async def cache_query_result(
    query_hash: str,
    result: dict,
    ttl: int = 3600
) -> None:
    """Cache query results with TTL."""
    await redis.set(f"query:{query_hash}", result, ex=ttl)

async def get_cached_result(
    query_hash: str
) -> Optional[dict]:
    """Retrieve cached query result."""
    return await redis.get(f"query:{query_hash}")
```

2. **Response Streaming**

```python
async def stream_large_response(
    query_result: dict,
    chunk_size: int = 1000
) -> AsyncGenerator[dict, None]:
    """Stream large query results in chunks."""
    
    for chunk in chunk_result(query_result, chunk_size):
        yield await format_chunk(chunk)
```

### Security Considerations

1. **Query Validation**

```python
def validate_query(query: dict) -> bool:
    """Validate incoming queries for security."""
    
    # Check for injection attempts
    if contains_injection(query):
        log_security_event("Injection attempt detected")
        return False
    
    # Validate trust requirements
    if not meets_trust_requirements(query):
        log_security_event("Trust requirement not met")
        return False
    
    return True
```

2. **Response Sanitization**

```python
def sanitize_response(response: dict) -> dict:
    """Sanitize response data before sending."""
    
    # Remove sensitive information
    cleaned = remove_sensitive_data(response)
    
    # Validate data types
    validated = validate_data_types(cleaned)
    
    return validated
```

## Configuration

```yaml
query_layer:
  api:
    host: "0.0.0.0"
    port: 8000
    workers: 4
    timeout: 30
    
  cache:
    enabled: true
    ttl: 3600
    max_size: 1000
    
  security:
    min_trust_score: 0.7
    require_authentication: true
    rate_limit: 100
    
  visualization:
    max_nodes: 1000
    max_relationships: 5000
    default_format: "graph"
```

## Usage Examples

1. **Basic Knowledge Query**

```python
response = await query({
    "text": "What are the key components of HADES?",
    "type": "knowledge_graph",
    "format": "text",
    "trust_threshold": 0.8
})
```

2. **Relationship Analysis**

```python
response = await query({
    "text": "Show relationships between Layer 3 and Layer 4",
    "type": "relationship",
    "format": "visualization",
    "context_depth": 3
})
```

3. **Hybrid Search**

```python
response = await query({
    "text": "Find similar architectural patterns to HADES",
    "type": "hybrid",
    "format": "graph",
    "trust_threshold": 0.9
})
```
