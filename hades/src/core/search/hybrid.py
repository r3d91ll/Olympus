"""Hybrid search combining vector similarity and context-aware filtering."""

# TODO: Future Improvements
# 1. Enhanced Context Scoring:
#    - Implement semantic role labeling for better relationship understanding
#    - Add temporal context awareness (time-based relevance decay)
#    - Incorporate user interaction patterns and feedback
#    - Add domain-specific context boosting
#    - Implement contextual embeddings for different aspects of the query
#    - Add multi-hop relationship scoring
#    - Consider query intent classification for context weighting
#    - Implement adaptive context boost based on query characteristics

from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from prometheus_client import Summary, Counter, Histogram

from core.config import settings
from core.context import analyze_context, AnalysisResult
from core.embeddings import EmbeddingModel
from db import VectorStore
from memory_management.manager import MemoryManager

# Metrics
HYBRID_SEARCH_TIME = Summary('hybrid_search_seconds', 'Time spent on hybrid search')
SEARCH_RESULTS = Histogram(
    'hybrid_search_results',
    'Number of results returned from hybrid search',
    buckets=[0, 1, 5, 10, 20, 50, 100]
)
SEARCH_OPS = Counter('hybrid_search_operations_total', 'Total hybrid search operations')

# Initialize embedding model
_embedding_model = EmbeddingModel()

async def hybrid_search(
    query: str,
    vector_store: VectorStore,
    memory_manager: MemoryManager,
    top_k: int = 10,
    min_relevance: float = 0.5,
    context_boost: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Perform hybrid search combining vector similarity with context awareness.
    
    Args:
        query: Search query string
        vector_store: Vector store instance
        memory_manager: Memory manager instance
        top_k: Number of results to return
        min_relevance: Minimum relevance score (0-1)
        context_boost: Weight for context-based boost (0-1)
        
    Returns:
        List of search results with scores and metadata
    """
    try:
        with HYBRID_SEARCH_TIME.time():
            # Analyze query context
            context_analysis = await analyze_context(query)
            
            # Get query vector
            query_vector = await get_query_vector(query)
            
            if query_vector is None:
                return []
            
            # Get relevant items from memory tiers
            memory_items = await get_memory_context(
                memory_manager,
                context_analysis
            )
            
            # Prepare metadata filter based on context
            metadata_filter = build_metadata_filter(
                context_analysis,
                memory_items
            )
            
            # Perform vector search with context-aware filtering
            vector_results = await vector_store.search(
                query_vector=query_vector,
                k=top_k * 2,  # Get more results for reranking
                metadata_filter=metadata_filter
            )
            
            # Rerank results using context
            results = rerank_results(
                vector_results,
                context_analysis,
                memory_items,
                context_boost
            )
            
            # Filter and sort final results
            final_results = [
                {
                    "id": result[0],
                    "score": result[1],
                    "metadata": result[2],
                    "context_score": result[3]
                }
                for result in results
                if result[1] >= min_relevance
            ][:top_k]
            
            # Update metrics
            SEARCH_OPS.inc()
            SEARCH_RESULTS.observe(len(final_results))
            
            return final_results
            
    except Exception as e:
        logger.error(f"Hybrid search failed: {str(e)}")
        return []

async def get_query_vector(query: str) -> Optional[List[float]]:
    """
    Get vector embedding for query.
    
    Args:
        query: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Check cache first
        if cached := _embedding_model.get_cached_embedding(query):
            return cached
            
        # Generate new embedding
        return await _embedding_model.generate(
            query,
            pooling=settings.EMBEDDING_POOLING
        )
        
    except Exception as e:
        logger.error(f"Failed to get query vector: {str(e)}")
        return None

async def get_memory_context(
    memory_manager: MemoryManager,
    context: AnalysisResult
) -> Dict[str, Any]:
    """Get relevant items from memory tiers."""
    try:
        # Check Elysium first
        items = {}
        for key in context.metadata.relationships.get("references", []):
            if value := await memory_manager.retrieve(key):
                items[key] = value
                
        # If not enough context, check Asphodel
        if len(items) < 5:
            # TODO: Implement broader context retrieval
            pass
            
        return items
        
    except Exception as e:
        logger.error(f"Failed to get memory context: {str(e)}")
        return {}

def build_metadata_filter(
    context: AnalysisResult,
    memory_items: Dict[str, Any]
) -> Dict[str, Any]:
    """Build ArangoDB filter based on context."""
    try:
        filter_conditions = {}
        
        # Add relevance threshold
        filter_conditions["relevance_score"] = {
            ">=": settings.TARTARUS_RELEVANCE_THRESHOLD
        }
        
        # Add context-based conditions
        if context.metadata.semantics:
            filter_conditions["semantic_type"] = {
                "IN": list(context.metadata.semantics.keys())
            }
            
        # Add relationship-based conditions
        if context.metadata.relationships:
            filter_conditions["related_to"] = {
                "IN": list(memory_items.keys())
            }
            
        return filter_conditions
        
    except Exception as e:
        logger.error(f"Failed to build metadata filter: {str(e)}")
        return {}

def rerank_results(
    vector_results: List[Tuple[str, float, Dict[str, Any]]],
    context: AnalysisResult,
    memory_items: Dict[str, Any],
    context_boost: float
) -> List[Tuple[str, float, Dict[str, Any], float]]:
    """
    Rerank search results using context information.
    
    Returns:
        List of tuples (id, combined_score, metadata, context_score)
    """
    try:
        reranked = []
        
        for result_id, vector_score, metadata in vector_results:
            # Calculate context score
            context_score = calculate_context_score(
                metadata,
                context,
                memory_items
            )
            
            # Combine scores
            combined_score = (
                (1 - context_boost) * vector_score +
                context_boost * context_score
            )
            
            reranked.append((
                result_id,
                combined_score,
                metadata,
                context_score
            ))
            
        # Sort by combined score
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked
        
    except Exception as e:
        logger.error(f"Failed to rerank results: {str(e)}")
        return [(r[0], r[1], r[2], 0.0) for r in vector_results]

def calculate_context_score(
    metadata: Dict[str, Any],
    context: AnalysisResult,
    memory_items: Dict[str, Any]
) -> float:
    """Calculate context-based relevance score."""
    try:
        score = 0.0
        
        # Semantic similarity
        if semantic_overlap := len(
            set(metadata.get("semantics", {})) &
            set(context.metadata.semantics)
        ):
            score += 0.4 * (semantic_overlap / len(context.metadata.semantics))
            
        # Relationship strength
        if relationship_overlap := len(
            set(metadata.get("related_to", [])) &
            set(memory_items.keys())
        ):
            score += 0.4 * (relationship_overlap / len(memory_items))
            
        # Recency and access patterns
        if access_time := metadata.get("last_access", 0):
            time_factor = 1.0 / (1.0 + (time.time() - access_time) / 3600)
            score += 0.2 * time_factor
            
        return score
        
    except Exception as e:
        logger.error(f"Failed to calculate context score: {str(e)}")
        return 0.0
