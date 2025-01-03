## Memory Management Within Mount Olympus

The memory management system integrates naturally into the Mount Olympus architecture, particularly within the HADES subsystem. Just as the mythological Hades managed different realms of the underworld, our system manages different tiers of memory and context.

### Memory Realms in HADES

Each realm in HADES corresponds to a specific type of memory storage and processing:

1. **Elysium (Critical Context - n_keep)**
   - Stores the most important context that must be preserved
   - Managed through explicit preservation rules
   - Direct mapping to n_keep parameter
   - Implementation:

   ```python
   class ElysiumRealm:
       def __init__(self, n_keep_limit: int):
           self.capacity = n_keep_limit
           self.preserved_context = []
           
       async def preserve(self, context: str) -> bool:
           """Preserve critical context in n_keep region."""
           tokens = self.tokenize(context)
           if len(tokens) <= self.capacity:
               self.preserved_context = tokens
               return True
           return False
   ```

2. **Asphodel (Working Memory)**
   - Handles active conversation state
   - Temporary computational results
   - Current context window content
   - Implementation:

   ```python
   class AsphodelRealm:
       def __init__(self, window_size: int):
           self.window_size = window_size
           self.active_context = []
           self.computation_cache = {}
           
       async def process(self, message: str) -> None:
           """Process new messages in working memory."""
           self.active_context.append(message)
           self.prune_if_needed()
   ```

3. **Tartarus (Archival Storage)**
   - Long-term conversation history
   - Indexed for efficient retrieval
   - Semantic relationship mapping
   - Implementation:

   ```python
   class TartarusRealm:
       def __init__(self):
           self.archive = VectorStore()
           self.relationship_graph = NetworkGraph()
           
       async def archive(self, context: ContextBlock) -> str:
           """Archive context with semantic indexing."""
           vector = self.vectorize(context)
           metadata = self.extract_metadata(context)
           return await self.archive.store(vector, metadata)
   ```

### The Rivers of Context Flow

The five rivers of HADES become our context flow management system:

1. **Styx (Primary Flow Control)**

   ```python
   class StyxController:
       async def manage_flow(self, context: Context) -> None:
           """Manage context flow between memory realms."""
           if self.should_preserve(context):
               await self.elysium.preserve(context)
           elif self.is_active(context):
               await self.asphodel.process(context)
           else:
               await self.tartarus.archive(context)
   ```

2. **Lethe (Forgetting Mechanism)**

   ```python
   class LetheManager:
       async def forget(self, context_id: str) -> None:
           """Implement controlled forgetting of irrelevant context."""
           relevance = await self.assess_relevance(context_id)
           if relevance < self.threshold:
               await self.remove_from_memory(context_id)
   ```

### Memory Processing Pipeline

The system processes context through several stages:

1. **Context Analysis**

   ```python
   class ContextAnalyzer:
       async def analyze(self, context: str) -> ContextMetadata:
           """Extract metadata and relationships from context."""
           tokens = self.tokenize(context)
           semantics = await self.extract_semantics(tokens)
           relationships = self.identify_relationships(semantics)
           return ContextMetadata(tokens, semantics, relationships)
   ```

2. **Memory Allocation**

   ```python
   class MemoryAllocator:
       async def allocate(self, context: AnalyzedContext) -> AllocationDecision:
           """Determine optimal memory placement."""
           if self.is_critical(context):
               return AllocationDecision(realm="elysium", priority="high")
           elif self.is_active(context):
               return AllocationDecision(realm="asphodel", priority="medium")
           return AllocationDecision(realm="tartarus", priority="low")
   ```

### Integration with Mount Olympus

The memory system integrates with other Mount Olympus components:

1. **Zeus Integration**
   - Resource allocation for memory operations
   - System-wide memory policy enforcement
   - Cross-component coordination

2. **Athena Integration**
   - Context analysis for memory decisions
   - Knowledge synthesis across memory realms
   - Intelligent retrieval strategies

3. **OracleDelphi Integration**
   - Memory visualization tools
   - Context editing interface
   - Usage analytics and insights

This architecture provides:

- Clear separation of memory types
- Efficient context flow management
- Intelligent memory allocation
- Seamless integration with existing components

The system maintains the mythological metaphor while implementing sophisticated memory management capabilities, making it both conceptually clear and technically robust.# Build Requirements Document

## Problem Statement & Objectives

### Problem Statement

In LLM conversations, the `n_keep` parameter preserves a specified number of tokens from the beginning of the conversation when context window limits are reached. However, users currently lack visibility into this preservation mechanism and tools to effectively structure their conversations around it. This often leads to important context being lost when it falls outside the preserved region, forcing disruptive conversation restarts.

### Objective

Develop a system that helps users understand and work effectively with the `n_keep` parameter by providing visibility into preserved context, tools for conversation structuring, and proactive warnings when important content risks falling outside the preserved region. This will enable users to maintain meaningful conversation flow while working within the constraints of their context window.

### Scope

- Context monitoring system with utilization alerts
- UI for tagging/editing retained context
- Integration with existing LLM platforms
- Context editing and review tools

### Key Features

- Token-based context utilization tracking
- Content tagging for retention/removal
- Direct context editing capabilities
- Notifications before token limit breaches
- Context versioning and undo functionality
- Local model loading and initialization support

### Expected Outcomes

- Reduced conversation disruptions
- Improved context relevance
- Enhanced user control over conversation flow
- Higher user satisfaction through predictable context management

### Success Metrics

- Reduction in forced conversation restarts
- Context window utilization efficiency
- User engagement with management tools
- Response coherence maintenance

## Critical Observations and Potential Obstacles

### 1. User Interface Complexity

- **Challenge:** Designing an intuitive and user-friendly interface for monitoring and editing context
- **Consideration:** Conduct user experience research, implement tooltips and tutorials

### 2. Integration with Existing LLM Platforms

- **Challenge:** Ensuring compatibility with various LLM platforms
- **Consideration:** Develop modular integration strategies, start with local models

### 3. User Training and Adoption

- **Challenge:** Users may need training for effective tool utilization
- **Consideration:** Provide comprehensive training materials and support

### 4. Maintaining Response Coherence

- **Challenge:** Direct context editing may lead to inconsistencies
- **Consideration:** Implement validation mechanisms and automated suggestions

### 5. Scalability and Maintenance

- **Challenge:** Managing performance and increasing data volumes
- **Consideration:** Design with scalability in mind, regular maintenance planning

### 6. Local Model Integration

- **Challenge:** Managing local model resources and configurations
- **Consideration:** Utilize LangChain and Hugging Face, optimize for RTX A6000 GPUs

## Development Cycle Tasks

### 1. Initial Setup

- Create conda environment
- Setup initial project structure
- Install base dependencies (FastAPI, Reflex, SQLite, LangChain, PyTorch)
- Initialize git repository

### 2. Core Backend Development

- Context tracking service implementation
  - Token counting
  - Percentage calculation
  - Alert threshold logic
- Storage service development
  - Context versioning
  - Content tagging system
  - SQLite database schema
- API endpoints creation
  - Context CRUD operations
  - Version management
  - Tag management
  - Model management

### 3. Frontend Development with Reflex

The frontend serves as a visual interface to our JSON structures, making complex prompt management intuitive for users. We'll build this in layers:

Base Application Layer:

- Set up Reflex application structure
- Implement state management for JSON blocks
- Create responsive layout system
- Develop real-time token counting display

Prompt Visualization Interface:

- Create a visual representation of the prompt structure showing:
  - System instructions (personality) section
  - n_keep preserved region with token count
  - Recent conversation history with token count
  - Current message area
  - Model parameters display
- Implement color coding to distinguish different sections
- Add token usage bars for each section

JSON Management Interface:

- Develop an intelligent JSON editor that:
  - Shows formatted prompt components
  - Highlights token counts for each section
  - Provides real-time validation
  - Offers syntax highlighting
- Create intuitive controls for:
  - Expanding/collapsing JSON sections
  - Editing specific blocks
  - Removing conversation tangents
  - Adjusting n_keep boundaries

Resource Monitoring Dashboard:

- Display GPU utilization metrics
- Show memory usage across GPUs
- Visualize NVLink bandwidth usage
- Present model loading status

### 4. Integration Phase

The integration phase focuses on connecting our JSON-centric management system with the GPU-optimized backend:

JSON Synchronization:

- Implement real-time synchronization between frontend and backend JSON structures
- Create WebSocket connections for live updates
- Develop conflict resolution for concurrent edits
- Build validation pipeline for JSON modifications

GPU Resource Integration:

- Connect GPU monitoring to dashboard
- Implement model loading/unloading controls
- Create memory management interface
- Develop performance optimization tools

End-to-End Workflows:

- Build conversation management pipeline
- Implement context editing workflow
- Create model switching system
- Develop error handling and recovery

Performance Optimization:

- Optimize JSON parsing and validation
- Implement caching for frequent operations
- Create efficient update mechanisms
- Develop background processing for heavy operations

This simplified JSON-centric approach makes the system more maintainable because:

- Clear separation of concerns between JSON structure and presentation
- Direct mapping between frontend display and backend data
- Simplified state management through JSON structures
- Reduced complexity in data transformation
- Easier testing and validation of system components

### 5. Testing

- Unit tests (pytest)
- Integration tests
- Performance benchmarks
- Manual testing checklist

### 6. Step 1 Implementation: Basic Chat and tmpfs Integration

- Implement tmpfs storage for prompts
  - Set up temporary folder (/dev/shm/llm_context)
  - Backend logic for tmpfs operations
- Develop simple chat interface
  - Message handling
  - Prompt storage in tmpfs

### 7. Step 2 Expansion: Manual Edit Features

- Extend chat interface
  - Context loading from tmpfs
  - Edit functionality
  - Save functionality

### 8. Local Model Management

- Enable Hugging Face model downloads
- LangChain integration
- RTX A6000 GPU optimization
- Model switching support

### 9. Documentation

- Function/class docstrings
- API documentation
- Schema documentation

### 10. Docker Deployment

- Create Dockerfile
- Docker-compose setup
- Test deployment
- Create README.md

## Technical Stack Requirements

### Backend Stack

- FastAPI framework
- Pydantic 2+ for:
  - Type enforcement
  - Configuration management
  - Data validation
  - API models/schemas
  - Domain models
  - Service interfaces
  - JSON structure validation for prompt components

### Hardware Optimization

- NVLink Configuration:
  - NCCL library integration
  - Distributed processing setup
  - Memory management across GPUs
- GPU Resource Management:
  - Mixed precision training/inference
  - Dynamic model loading
  - Efficient memory utilization
  - Performance monitoring

### Prompt Structure Management

- JSON block editing for:
  - n_keep preserved region ("task memory")
  - Recent conversation history
- Visual representation of:
  - System instructions (personality)
  - n_keep content
  - Unprotected context
  - Current message
  - Model parameters
- Token usage visualization for each component
- Real-time editing capabilities for context adjustment

### Frontend Stack

- Reflex framework
- Component-based architecture
- State management

### Project Architecture

```
src/
├── backend/
│   ├── api/          # FastAPI routes
│   ├── core/         # Core business logic
│   │   ├── models/   # Pydantic models
│   │   └── services/
│   ├── config/       # Pydantic config
│   └── db/           # Database layer
├── frontend/         # Reflex components
└── shared/          # Shared Pydantic models
```

## Additional Notes

- Frontend Framework: Reflex chosen for Python-native capabilities
- Backend Framework: FastAPI for RAG operations and API handling
- Local Models: Initial focus on Hugging Face models
- Hardware Optimization: RTX A6000 GPU utilization focus


