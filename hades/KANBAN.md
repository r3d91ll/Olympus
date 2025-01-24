# HADES Development Kanban

## 🆕 Backlog

### Future Enhancements

- [ ] Add Phoenix monitoring
- [ ] Implement custom evaluation metrics
- [ ] Add advanced RAG chain tracing
- [ ] Optimize performance
- [ ] Add comprehensive documentation

## 📋 Ready for Phase 1

### 1. Vector Store Setup

- [x] Update ArangoDB class with vector methods
  - [x] Add create_vector_collection method
  - [x] Add create_vector_index method
  - [x] Add vector search method
- [x] Create vector collection schema

  ```python
  {
      "text": str,          # Original text content
      "embedding": list,    # Vector embedding
      "metadata": dict,     # Additional info (source, type, etc)
      "timestamp": str,     # ISO format timestamp
      "chunk_id": str,      # Unique identifier for text chunk
      "parent_id": str      # Reference to original document
  }
  ```

- [x] Set up HNSW index configuration

  ```python
  {
      "type": "vector",
      "fields": ["embedding"],
      "algorithm": "hnsw",
      "params": {
          "maxElements": 1000000,
          "efConstruction": 128,
          "ef": 64,
          "M": 16
      }
  }
  ```

### 2. Document Ingestion

- [x] Create document processor
  - [x] Implement text chunking
  - [x] Add metadata extraction
  - [x] Set up chunk ID generation
- [x] Set up embedding pipeline
  - [x] Initialize sentence-transformers model
  - [x] Create batch embedding method
  - [x] Add embedding caching
- [x] Create ingestion workflow
  - [x] Add validation checks
  - [x] Implement batch processing
  - [x] Add error handling

### 3. Retrieval Mechanism

- [x] Implement vector search
  - [x] Add similarity search method
  - [x] Create relevance scoring
  - [x] Add result filtering
- [x] Create context builder
  - [x] Implement context window management
  - [x] Add metadata filtering
  - [x] Create response formatting

### 4. Basic RAG Chain

- [x] Set up LangChain integration
  - [x] Initialize LLM configuration
  - [x] Create custom retriever class
  - [x] Set up response generation
- [x] Create prompt templates
  - [x] Design system prompt
  - [x] Add context template
  - [x] Create response format

## 🏗️ In Progress

### Testing Framework

- [ ] Create unit tests for all components
- [ ] Set up integration tests
- [ ] Add test fixtures and utilities

## ✅ Done

- [x] ArangoDB basic connection
- [x] Initial project structure
- [x] Kanban board setup
- [x] Vector store implementation
  - [x] Collection creation
  - [x] HNSW index setup
  - [x] Vector storage methods
  - [x] Vector search methods
  - [x] Vector deletion methods
- [x] Document processor implementation
  - [x] Text chunking with RecursiveCharacterTextSplitter
  - [x] Metadata extraction and management
  - [x] Embedding generation with HuggingFace
  - [x] Document storage and deletion
  - [x] Error handling and logging
- [x] Retrieval mechanism implementation
  - [x] Similarity search with filtering
  - [x] Relevance scoring
  - [x] Context window management
  - [x] Source tracking
  - [x] Error handling and logging
- [x] RAG Chain implementation
  - [x] LangChain integration with Llama-2
  - [x] Custom prompt templates
  - [x] Response generation
  - [x] Chat history support
  - [x] Source attribution
  - [x] Error handling and logging

## 🚫 Blocked

None currently.

## Detailed Implementation Steps

### Phase 1 Implementation Order

1. **Vector Store Setup** (Day 1)

   ```python
   # Step 1: Update ArangoDB class
   class ArangoDB:
       async def create_vector_collection(self):
           """Create vector collection if not exists."""
           
       async def create_vector_index(self):
           """Create HNSW index on vector collection."""
           
       async def vector_search(self, query_vector: List[float], k: int):
           """Perform vector similarity search."""
   ```

2. **Document Ingestion** (Day 2)

   ```python
   # Step 1: Create document processor
   class DocumentProcessor:
       def chunk_text(self, text: str) -> List[str]:
           """Split text into chunks."""
           
       def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
           """Generate embeddings for chunks."""
           
       async def process_document(self, text: str, metadata: dict):
           """Process document end-to-end."""
   ```

3. **Retrieval Mechanism** (Day 3)

   ```python
   # Step 1: Create retriever
   class Retriever:
       async def similarity_search(self, query: str, k: int):
           """Perform similarity search."""
           
       def build_context(self, results: List[dict]) -> str:
           """Build context from search results."""
   ```

4. **RAG Chain** (Day 4)

   ```python
   # Step 1: Create RAG chain
   class RAGChain:
       def __init__(self):
           self.retriever = Retriever()
           self.llm = self.init_llm()
           
       async def process_query(self, query: str) -> str:
           """Process query through RAG pipeline."""
   ```

## Testing Strategy

### Unit Tests

- Vector store operations
- Document processing
- Retrieval accuracy
- RAG chain functionality

### Integration Tests

- End-to-end document processing
- Complete RAG pipeline
- Error handling scenarios

## Next Actions

1. Set up testing framework
2. Create basic documentation
3. Add example usage
