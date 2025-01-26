"""Retrieval mechanism for RAG pipeline."""
from typing import Dict, List, Optional, Union
import numpy as np
from loguru import logger

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

from db.arango import ArangoDB

class Retriever:
    """Handle document retrieval and context building."""
    
    def __init__(
        self,
        db: ArangoDB,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_context_length: int = 2000
    ):
        """Initialize retriever.
        
        Args:
            db: ArangoDB instance
            embedding_model: HuggingFace model name for embeddings
            max_context_length: Maximum length of combined context
        """
        self.db = db
        self.max_context_length = max_context_length
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            cache_folder=".cache/huggingface"
        )
        
    def _calculate_relevance_score(self, distance: float) -> float:
        """Calculate relevance score from distance.
        
        Convert distance to similarity score (0-1 range).
        Lower distance means higher similarity.
        """
        # Assuming cosine distance, convert to similarity
        return 1 - min(1.0, max(0.0, distance))
        
    def _filter_by_relevance(
        self,
        results: List[Dict],
        threshold: float = 0.7
    ) -> List[Dict]:
        """Filter results by relevance score."""
        filtered = [
            r for r in results
            if self._calculate_relevance_score(r["distance"]) >= threshold
        ]
        logger.debug(
            f"Filtered {len(results)} results to {len(filtered)} "
            f"using threshold {threshold}"
        )
        return filtered
        
    def _build_context_window(
        self,
        results: List[Dict],
        max_length: Optional[int] = None
    ) -> str:
        """Build context window from results."""
        max_len = max_length or self.max_context_length
        context_parts = []
        current_length = 0
        
        # Sort by relevance score
        sorted_results = sorted(
            results,
            key=lambda x: self._calculate_relevance_score(x["distance"]),
            reverse=True
        )
        
        for result in sorted_results:
            text = result["text"]
            text_len = len(text)
            
            # Check if adding this text would exceed max length
            if current_length + text_len > max_len:
                # If this is the first text, include a truncated version
                if not context_parts:
                    truncated = text[:max_len]
                    context_parts.append(truncated)
                break
                
            context_parts.append(text)
            current_length += text_len
            
        return "\n\n".join(context_parts)
        
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query text."""
        try:
            return self.embedding_model.embed_query(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {str(e)}")
            raise
            
    async def similarity_search(
        self,
        query: Union[str, List[float]],
        k: int = 3,
        threshold: float = 0.7,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Perform similarity search with filtering."""
        try:
            # Generate embedding if query is text
            query_vector = (
                await self.generate_query_embedding(query)
                if isinstance(query, str)
                else query
            )
            
            # Search vector store
            results = await self.db.search_vectors(
                query_vector=query_vector,
                k=k,
                metadata_filter=metadata_filter
            )
            
            # Filter by relevance
            if threshold:
                results = self._filter_by_relevance(results, threshold)
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {str(e)}")
            return []
            
    async def get_relevant_context(
        self,
        query: str,
        k: int = 3,
        threshold: float = 0.7,
        metadata_filter: Optional[Dict] = None,
        max_length: Optional[int] = None
    ) -> Dict:
        """Get relevant context for query."""
        try:
            # Perform similarity search
            results = await self.similarity_search(
                query=query,
                k=k,
                threshold=threshold,
                metadata_filter=metadata_filter
            )
            
            if not results:
                logger.warning("No relevant context found")
                return {
                    "context": "",
                    "sources": [],
                    "relevance_scores": []
                }
                
            # Build context window
            context = self._build_context_window(
                results,
                max_length=max_length
            )
            
            # Extract sources and scores
            sources = []
            scores = []
            for r in results:
                source = r["metadata"].get("source", "unknown")
                if source not in sources:
                    sources.append(source)
                scores.append(
                    self._calculate_relevance_score(r["distance"])
                )
                
            return {
                "context": context,
                "sources": sources,
                "relevance_scores": scores
            }
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {str(e)}")
            return {
                "context": "",
                "sources": [],
                "relevance_scores": []
            }
            
    async def get_context_by_id(
        self,
        parent_id: str,
        max_length: Optional[int] = None
    ) -> Dict:
        """Get context for a specific document."""
        try:
            # Search by parent ID
            results = await self.db.search_vectors(
                metadata_filter={"parent_id": parent_id}
            )
            
            if not results:
                logger.warning(f"No context found for parent_id: {parent_id}")
                return {
                    "context": "",
                    "sources": [],
                    "chunk_count": 0
                }
                
            # Build context window
            context = self._build_context_window(
                results,
                max_length=max_length
            )
            
            # Extract sources
            sources = []
            for r in results:
                source = r["metadata"].get("source", "unknown")
                if source not in sources:
                    sources.append(source)
                    
            return {
                "context": context,
                "sources": sources,
                "chunk_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to get context by ID: {str(e)}")
            return {
                "context": "",
                "sources": [],
                "chunk_count": 0
            }
