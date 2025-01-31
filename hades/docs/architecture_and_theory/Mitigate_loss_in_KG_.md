# Mitigating Information Loss in Knowledge Graphs for GraphRAG

## Overview

This paper introduces the Triple Context Restoration and Question-driven Feedback (TCR-QF) framework, designed to address two critical challenges in Knowledge Graph (KG) - Large Language Model (LLM) integration:

1. Information sparsity from incomplete extraction
2. Context loss during text-to-triple conversion

## Key Challenges in KG-LLM Integration

### Information Sparsity

- Occurs when information extraction misses important triples
- Caused by:
  - Data noise
  - Long-tail entities
  - Complex relationships
  - Limitations in extraction algorithms

### Context Loss

- Happens during conversion of unstructured text to discrete triples
- Results in loss of:
  - Semantic nuances
  - Relational dependencies
  - Broader contextual information

## The TCR-QF Framework

### 1. Knowledge Graph Construction

- Uses LLMs for initial triple extraction
- Process:
  1. **Document Splitting**:
     - Chunks of 2048 tokens with 256 token overlap
     - Overlap ensures capture of cross-chunk entities
  2. **Triple Extraction**:
     - Extracts (eh,r,et) triples from each chunk
     - Includes entity types and descriptions
  3. **Subgraph Merging**:
     - Merges entities referring to same concepts
     - Uses similarity functions for entity consolidation

### 2. Triple Context Restoration

- **Context Retrieval**:
  - Traces back to source documents for each triple
  - Retrieves original contextual information

- **Triple Context Tracing**:
  - Identifies most relevant sentences from source documents
  - Uses embedding models for similarity matching
  - Selects highest-scoring contextual sentences

- **Triple Augmentation**:
  - Enhances triples with associated contextual sentences
  - Restores semantic integrity

### 3. Query-Driven Feedback

- Implements iterative process to:
  - Identify missing information relevant to queries
  - Dynamically enrich the KG
  - Improve completeness of knowledge representation

## Experimental Results

### Performance Improvements

- Average improvements across five benchmark datasets:
  - 29.1% improvement in Exact Match (EM)
  - 15.5% improvement in F1 score

### Specific Dataset Results

1. **HotpotQA**:
   - TCR-QF EM score: 0.558
   - 59% improvement over GPT-4o baseline

2. **2WikiMultiHopQA**:
   - TCR-QF EM score: 0.598
   - 76.4% improvement over Naive RAG
   - 49.5% improvement over TOG

3. **MuSiQue-Full**:
   - TCR-QF EM score: 0.303
   - 60.3% improvement over GraphRAG

## Key Advantages

1. **Enhanced Accuracy**: Consistently higher performance across all datasets
2. **Robust Reasoning**: Better handling of complex multi-hop questions
3. **Dynamic Enrichment**: Continuous improvement of knowledge representation
4. **Context Preservation**: Maintains semantic richness of original text
5. **General Applicability**: Effective across various question-answering tasks

## Implementation Considerations

- Requires careful document splitting and overlap management
- Needs efficient embedding models for similarity matching
- Benefits from high-quality source document retention
- Demands balanced threshold setting for entity merging

## Future Implications

- Potential for improved information retrieval systems
- Applications in complex reasoning tasks
- Framework for better KG-LLM integration
- Foundation for more accurate question-answering systems
