# Research Notes for Olympus Development

## Fine-tuning Approaches (2024-01-21)

### Transformer² (Self-adaptive LLMs)

Repository: <https://github.com/SakanaAI/self-adaptive-llms>

Key concept: Instead of multiple specialized models, use expert vectors as "masks" for different capabilities:

- One base model (e.g., 14B parameters)
- Lightweight masks for specialization
- Quick adaptation without full fine-tuning

#### Potential Application for HADES

- Base Model: 14B with strong reasoning, coding, data science capabilities
- Database-specific masks:
  - ArangoDB operations
  - PostgreSQL optimization
  - SQL query handling
  - Future database support

Benefits:

- Resource efficient (one model, many masks)
- Quick adaptation to different databases
- Easier deployment and management
- Faster training for new capabilities

### Comparison Point: Titans

Paper: <https://arxiv.org/html/2501.00663v1>

Different approach focusing on active learning and memory formation at test time.
Could be complementary to Transformer² for:

- Learning new patterns
- Building long-term knowledge
- Adapting to novel scenarios

### Future Investigation Needed

1. Base model selection criteria
   - Size vs capability tradeoffs
   - Required foundational knowledge
   - Resource constraints

2. Mask training methodology
   - Expert vector creation
   - Task-specific optimization
   - Performance metrics

3. Evaluation framework
   - Compare with traditional fine-tuning
   - Measure adaptation speed
   - Resource usage metrics

4. Integration strategy
   - How to combine with other approaches
   - When to use which method
   - System architecture implications

### Decision Points for Future

- [ ] Select base model size and capabilities
- [ ] Choose between/combine fine-tuning approaches
- [ ] Design mask training pipeline
- [ ] Create evaluation framework
- [ ] Plan integration with HADES architecture

*Note: Revisit when reaching fine-tuning phase. Monitor for new developments in both approaches.*

## HADES Version Comparison (2024-01-21)

### Architecture Matrix

| Component | Old HADES | Current H.A.D.E.S. | Migration Value |
|-----------|-----------|-------------------|----------------|
| **Vector Store** | Milvus-based | FAISS Integration | 🟡 Consider Milvus features |
| **Database** | ArangoDB (basic) | ArangoDB (advanced) | 🟢 Docker configs |
| **Model Integration** | Basic embeddings | Hephaestus Engine | 🔴 Use new architecture |
| **Memory System** | None | Sophisticated RAG | 🔴 Use new system |
| **Project Structure** | Clean separation | Module-based | 🟢 Worth referencing |
| **Testing** | Basic pytest | Advanced testing | 🟢 Framework adaptable |
| **Docker** | Basic setup | Advanced integration | 🟡 Update and merge |
| **Security** | Basic HTTPS | Advanced patterns | 🟡 Merge approaches |

### Feature Comparison

| Feature | Old HADES | Current H.A.D.E.S. | Notes |
|---------|-----------|-------------------|--------|
| **RAG Capabilities** | Three-tier memory system (Elysium/Asphodel/Lethe) | To be implemented | Old system has interesting memory architecture |
| **Memory Management** | In-memory only | Long-term persistence | Current is superior |
| **Model Handling** | Single model | Multiple model support | Current is superior |
| **Query Processing** | Direct processing | Pipeline architecture | Current is superior |
| **Scalability** | Basic | Advanced | Current is superior |
| **Error Handling** | Basic try/catch | Sophisticated error types | Current is superior |

### Integration Points

| System | Old HADES | Current H.A.D.E.S. | Integration Strategy |
|--------|-----------|-------------------|---------------------|
| **Olympus Core** | Loose coupling | Tight integration | Use current approach |
| **Frontend** | Streamlit | Advanced UI | Keep current UI |
| **APIs** | Basic FastAPI | Advanced FastAPI | Merge best practices |
| **Monitoring** | Basic logging | Advanced telemetry | Combine approaches |

### Migration Recommendations

1. **High Priority Salvage**:
   - Docker configurations
   - Testing framework
   - Project structure patterns
   - Security configurations

2. **Consider Incorporating**:
   - Milvus integration concepts
   - Separation of concerns patterns
   - API documentation approach
   - Deployment scripts

3. **Skip/Replace**:
   - Old RAG implementation
   - Basic model management
   - Simple memory handling
   - Basic error handling

### Decision Points

- [ ] Evaluate Milvus vs FAISS for vector store
- [ ] Merge Docker configurations
- [ ] Adapt testing framework
- [ ] Update security patterns

*Note: 🟢 = High value for migration, 🟡 = Consider carefully, 🔴 = Skip/replace*

## Current Implementation Strategy (2024-01-21)

### Phase 1: Docker-Based Deployment

1. **Resource Sharing Model**:
   - Docker containerization for HADES and siblings
   - Shared hardware resources
   - Container-based resource allocation
   - Orchestrated multi-service deployment

2. **Model Selection**:

   ```yaml
   model:
     base: "mergekit-community/Qwen2.5-14B-Coder-Merge"
     advantages:
       - Strong coding capabilities
       - Built-in tool calling
       - MCP compatibility
       - Reasoning foundation
     potential_improvements:
       - Fine-tuning for reasoning
       - Tree of Thought enhancement
       - Database-specific optimization
   ```

3. **Container Architecture**:

   ```mermaid
   graph TD
       subgraph "Current Setup"
           H[HADES Container]
           A[ArangoDB Container]
           M[Model Service Container]
           
           H --> |Queries|A
           H --> |Inference|M
       end
       
       subgraph "Shared Resources"
           GPU[GPU Pool]
           RAM[RAM Pool]
           STORAGE[Storage Pool]
       end
       
       M --> GPU
       H --> RAM
       A --> STORAGE
   ```

### Phase 2: Future Dedicated Server

1. **Migration Path**:
   - Move from containers to bare metal
   - Implement full tiered memory
   - Direct hardware access
   - Optimized for database operations

2. **Hardware Utilization**:
   - Dedicated GPUs
   - Optimized storage tiers
   - Direct PCI-E paths
   - Custom memory management

3. **Service Evolution**:

   ```mermaid
   graph LR
       subgraph "Phase 1: Docker"
           D[Docker HADES]
       end
       
       subgraph "Phase 2: Dedicated"
           H[HADES Server]
           T1[Elysium Tier]
           T2[Asphodel Tier]
           T3[Lethe Tier]
           
           H --> T1
           H --> T2
           H --> T3
       end
       
       D --> |Migration|H
   ```

### Current Implementation Priorities

1. **Docker Setup**:
   - [ ] Container resource allocation
   - [ ] Service orchestration
   - [ ] Inter-container communication
   - [ ] Monitoring setup

2. **Model Integration**:
   - [ ] Deploy Qwen2.5-14B-Coder-Merge
   - [ ] Implement tool calling interface
   - [ ] Set up MCP communication
   - [ ] Basic reasoning capabilities

3. **Database Layer**:
   - [ ] ArangoDB container setup
   - [ ] Basic memory management
   - [ ] Query optimization
   - [ ] Backup strategy

### Future Migration Checklist

- [ ] Hardware procurement
- [ ] Bare metal setup
- [ ] Tiered storage implementation
- [ ] Performance optimization
- [ ] Service migration
- [ ] Testing and validation

*Note: Current focus is on getting HADES operational in a shared environment while designing for future dedicated hardware.*

## Tiered Memory Architecture (2024-01-21)

### Layer 1: Hardware Foundation

1. **Elysium (Fastest Tier)**:
   - 256GB RAM
   - tmpfs for model staging
   - Direct PCI-E access to 2x A6000 GPUs
   - ThreadRipper 7960x orchestration
   - Use: Active models, current context, immediate processing

2. **Asphodel (Fast Storage)**:
   - 2x 2TB NVMe Gen5 in RAID0
   - Ultra-fast cache layer
   - Quick model loading
   - Use: Recent contexts, frequent models, fast data staging

3. **Lethe (Persistence Layer)**:
   - 2x 4TB NVMe Gen5 in RAID1 (Backup)
   - 5x 1TB Gen4 in RAID5 (Storage)
   - 4x 20TB HDD in RAID5 (Archive)
   - Use: Long-term storage, historical data, model archives

### Software Implementation

```python
class TieredMemoryManager:
    def __init__(self):
        self.elysium = {
            "ram": "256GB",
            "tmpfs": "/dev/shm",
            "gpu_memory": "2x 48GB A6000"
        }
        self.asphodel = {
            "fast_cache": "RAID0 4TB",
            "access_time": "microseconds"
        }
        self.lethe = {
            "backup": "RAID1 8TB",
            "storage": "RAID5 4TB",
            "archive": "RAID5 80TB"
        }
```

### Memory Movement Patterns

1. **Predictive Loading**:

   ```mermaid
   graph TD
       A[Predict Need] --> B[Stage to tmpfs]
       B --> C[Load to GPU]
       D[Cool Data] --> E[Move to Asphodel]
       E --> F[Archive to Lethe]
   ```

2. **Data Lifecycle**:
   - Hot data in Elysium (RAM/GPU)
   - Warm data in Asphodel (NVMe RAID0)
   - Cold data in Lethe (RAID1/RAID5)

3. **Optimization Strategies**:
   - Pre-staging models to tmpfs
   - Smart caching in Asphodel
   - Intelligent archival in Lethe

### Integration with HADES

1. **Memory-Aware Operations**:
   - Model placement optimization
   - Context-aware data movement
   - Resource-conscious scheduling

2. **Performance Considerations**:
   - Direct GPU access paths
   - NVMe optimization
   - RAID configuration tuning

3. **Scaling Strategy**:
   - Vertical scaling with hardware
   - Horizontal scaling across nodes
   - Memory tier balancing

### Implementation Priorities

- [ ] Design memory movement algorithms
- [ ] Implement predictive loading
- [ ] Create monitoring system
- [ ] Optimize data placement
- [ ] Develop backup strategies

*Note: This architecture demonstrates building from Layer 1 hardware through to high-level AI operations, showing how each tier serves specific purposes in the overall system.*

## Privacy and Security Design Principles (2024-01-21)

### Core Principle: Absolute Privacy Boundary

The system must be designed with an absolute privacy boundary where even the system creators/maintainers CANNOT access client data:

1. **AI as Legal Entity**:
   - AI operates as a privileged entity within the household
   - Similar to attorney-client or doctor-patient privilege
   - AI manages its own database and access controls
   - Household owns both AI and data sovereignty

2. **Security Architecture**:
   - Zero vendor access to client databases
   - No support backdoors
   - One-way update channels only
   - Sanitized diagnostics without data exposure

3. **Support Model**:
   - Technical support through sanitized diagnostics only
   - System updates without data access
   - Infrastructure maintenance without content visibility
   - Clear legal and technical boundaries

4. **Implementation Requirements**:
   - Strong encryption at rest and in transit
   - Local data sovereignty
   - AI-controlled access management
   - Technical impossibility of vendor access

5. **Business Implications**:
   - Compliant with ArangoDB BSL 1.1
   - Strong privacy as selling point
   - Clear legal framework
   - Scalable business model

### Technical Implementation Notes

- Design all systems with privacy-first architecture
- Implement one-way update channels
- Create sanitized diagnostic systems
- Develop AI-managed access controls
- Plan for legal entity framework

### Future Considerations

- [ ] Design privacy-preserving diagnostic system
- [ ] Develop secure update mechanism
- [ ] Create AI privilege framework
- [ ] Plan legal entity structure
- [ ] Design security boundary implementation

*Note: This is a fundamental design principle - "If we can access client data, we ARE the security vulnerability."*
