"""Context analyzer for memory allocation decisions."""

import time
from typing import Dict, Any, List
from loguru import logger
from prometheus_client import Summary

from .models import ContextMetadata, AnalysisResult
from ..config import settings

# Metrics
ANALYSIS_TIME = Summary('context_analysis_seconds', 'Time spent analyzing context')
TOKENIZATION_TIME = Summary('context_tokenization_seconds', 'Time spent tokenizing context')
SEMANTIC_EXTRACTION_TIME = Summary('semantic_extraction_seconds', 'Time spent extracting semantics')

async def tokenize_context(context: str) -> List[str]:
    """
    Tokenize context string into meaningful units.
    
    Args:
        context: Input context string
        
    Returns:
        List of tokens
    """
    try:
        with TOKENIZATION_TIME.time():
            # Simple whitespace tokenization for now
            # TODO: Implement more sophisticated tokenization
            return context.split()
    except Exception as e:
        logger.error(f"Tokenization failed: {str(e)}")
        return []

async def extract_semantics(context: str, tokens: List[str]) -> Dict[str, float]:
    """
    Extract semantic information from context.
    
    Args:
        context: Original context string
        tokens: Tokenized context
        
    Returns:
        Dictionary of semantic features and their values
    """
    try:
        with SEMANTIC_EXTRACTION_TIME.time():
            # Simple semantic extraction for now
            # TODO: Implement proper semantic analysis
            return {
                "relevance": 1.0 if len(tokens) > 10 else 0.5,
                "complexity": len(set(tokens)) / len(tokens) if tokens else 0.0,
                "recency": time.time()
            }
    except Exception as e:
        logger.error(f"Semantic extraction failed: {str(e)}")
        return {}

async def identify_relationships(
    context: str,
    tokens: List[str]
) -> Dict[str, List[str]]:
    """
    Identify relationships between context elements.
    
    Args:
        context: Original context string
        tokens: Tokenized context
        
    Returns:
        Dictionary of relationships between elements
    """
    try:
        # Simple relationship identification for now
        # TODO: Implement proper relationship analysis
        return {
            "dependencies": [],
            "references": []
        }
    except Exception as e:
        logger.error(f"Relationship identification failed: {str(e)}")
        return {}

async def analyze_context(context: str) -> AnalysisResult:
    """
    Analyze context and determine optimal memory allocation.
    
    Args:
        context: Input context string to analyze
        
    Returns:
        AnalysisResult with metadata and allocation decision
    """
    try:
        with ANALYSIS_TIME.time():
            # Early validation
            if not context:
                logger.warning("Empty context provided")
                return AnalysisResult(
                    metadata=ContextMetadata(),
                    suggested_tier="lethe",
                    priority="low",
                    ttl=60
                )
            
            # Extract features
            tokens = await tokenize_context(context)
            semantics = await extract_semantics(context, tokens)
            relationships = await identify_relationships(context, tokens)
            
            # Create metadata
            metadata = ContextMetadata(
                tokens=tokens,
                semantics=semantics,
                relationships=relationships,
                last_access=time.time(),
                access_count=1,
                relevance_score=semantics.get("relevance", 0.0)
            )
            
            # Determine allocation
            return determine_allocation(metadata)
            
    except Exception as e:
        logger.error(f"Context analysis failed: {str(e)}")
        # Return safe default
        return AnalysisResult(
            metadata=ContextMetadata(),
            suggested_tier="lethe",
            priority="low",
            ttl=60
        )

def determine_allocation(metadata: ContextMetadata) -> AnalysisResult:
    """
    Determine optimal memory allocation based on context metadata.
    
    Args:
        metadata: Context metadata to analyze
        
    Returns:
        AnalysisResult with allocation decision
    """
    try:
        relevance = metadata.relevance_score
        complexity = metadata.semantics.get("complexity", 0.0)
        
        # Determine tier and priority
        if relevance > settings.TARTARUS_RELEVANCE_THRESHOLD:
            if complexity > 0.7 or metadata.access_count > 5:
                return AnalysisResult(
                    metadata=metadata,
                    suggested_tier="elysium",
                    priority="high",
                    ttl=7200  # 2 hours
                )
            return AnalysisResult(
                metadata=metadata,
                suggested_tier="asphodel",
                priority="medium",
                ttl=3600  # 1 hour
            )
        
        if relevance > settings.LETHE_PROMOTION_THRESHOLD:
            return AnalysisResult(
                metadata=metadata,
                suggested_tier="tartarus",
                priority="low",
                ttl=1800  # 30 minutes
            )
            
        return AnalysisResult(
            metadata=metadata,
            suggested_tier="lethe",
            priority="low",
            ttl=300  # 5 minutes
        )
            
    except Exception as e:
        logger.error(f"Allocation determination failed: {str(e)}")
        return AnalysisResult(
            metadata=metadata,
            suggested_tier="lethe",
            priority="low",
            ttl=60
        )
