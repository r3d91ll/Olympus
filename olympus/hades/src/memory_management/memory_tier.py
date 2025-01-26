from typing import Any, Dict, Optional, List, Tuple
from abc import ABC, abstractmethod
import asyncio
from loguru import logger
from pydantic import BaseModel

class ContextMetadata(BaseModel):
    """Enhanced metadata for context-aware memory management with vector support."""
    tokens: List[str]
    semantics: Dict[str, float]
    last_access: float
    access_count: int
    vector_embedding: Optional[List[float]] = None  # For similarity search
    relation_triples: Optional[List[Tuple[str, str, str]]] = None  # For structured knowledge
    position_encoding: Optional[List[float]] = None  # For parallel positioning
    compression_ratio: Optional[int] = None  # For token compression tracking
    
class MemoryTier(ABC):
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.current_size = 0
        self._data: Dict[str, Any] = {}
        self._metadata: Dict[str, ContextMetadata] = {}
        self._lock = asyncio.Lock()
    
    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        """Store data in the memory tier."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from the memory tier."""
        pass
    
    @abstractmethod
    async def evict(self, key: str) -> bool:
        """Evict data from the memory tier."""
        pass
        
    async def get_metadata(self, key: str) -> Optional[ContextMetadata]:
        """Get metadata for stored item."""
        return self._metadata.get(key)

class SimilaritySearch:
    """Handles similarity-based memory retrieval."""
    
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0.0

    @staticmethod
    async def find_similar(query_embedding: List[float], 
                          items: Dict[str, Any],
                          metadata: Dict[str, ContextMetadata],
                          threshold: float = 0.7,
                          max_results: int = 5) -> List[Tuple[str, float]]:
        """Find items with similar embeddings."""
        similarities = []
        for key, meta in metadata.items():
            if meta.vector_embedding:
                sim = SimilaritySearch.cosine_similarity(query_embedding, meta.vector_embedding)
                if sim >= threshold:
                    similarities.append((key, sim))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]

class TokenCompressor:
    """Handles token compression for efficient memory storage."""
    
    def __init__(self, max_ratio: int = 16):
        self.max_ratio = max_ratio
        
    async def compress(self, tokens: List[str], ratio: int) -> Tuple[List[str], List[float]]:
        """Compress tokens using adaptive token selection."""
        if ratio > self.max_ratio:
            ratio = self.max_ratio
            
        if len(tokens) <= ratio:
            return tokens, [1.0] * len(tokens)
            
        # Select most important tokens using frequency and position
        token_scores = []
        for i, token in enumerate(tokens):
            # Score based on position (favor start and end)
            pos_score = 1.0 - min(i, len(tokens) - i - 1) / len(tokens)
            # Basic frequency score
            freq_score = tokens.count(token) / len(tokens)
            token_scores.append(pos_score * 0.6 + freq_score * 0.4)
            
        # Select top tokens
        target_len = len(tokens) // ratio
        threshold = sorted(token_scores, reverse=True)[target_len]
        
        compressed_tokens = []
        importance_scores = []
        for token, score in zip(tokens, token_scores):
            if score >= threshold:
                compressed_tokens.append(token)
                importance_scores.append(score)
                
        return compressed_tokens, importance_scores

class ElysiumTier(MemoryTier):
    """Hot memory tier for active context."""
    
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        async with self._lock:
            if self.current_size >= self.max_size:
                logger.warning("Elysium tier at capacity")
                return False
            self._data[key] = value
            if metadata:
                self._metadata[key] = metadata
            return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        return self._data.get(key)
    
    async def evict(self, key: str) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                self._metadata.pop(key, None)
                return True
            return False

class AsphodelTier(MemoryTier):
    """Warm memory tier with similarity search."""
    
    def __init__(self, max_size: int, window_size: int):
        super().__init__(max_size)
        self.window_size = window_size
        self.similarity_search = SimilaritySearch()
    
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        async with self._lock:
            if len(self._data) >= self.window_size:
                # Evict oldest item if at window capacity
                oldest_key = min(
                    self._metadata.keys(),
                    key=lambda k: self._metadata[k].last_access
                )
                await self.evict(oldest_key)
            
            self._data[key] = value
            if metadata:
                self._metadata[key] = metadata
            return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        return self._data.get(key)
    
    async def evict(self, key: str) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                self._metadata.pop(key, None)
                return True
            return False
    
    async def find_similar(self, query_embedding: List[float], threshold: float = 0.7) -> List[Tuple[str, Any]]:
        """Find similar items using vector similarity."""
        similar_keys = await self.similarity_search.find_similar(
            query_embedding,
            self._data,
            self._metadata,
            threshold
        )
        return [(key, self._data[key]) for key, _ in similar_keys]

class TartarusTier(MemoryTier):
    """Archival tier with compression and similarity search."""
    
    def __init__(self, max_size: int):
        super().__init__(max_size)
        self.compressor = TokenCompressor()
        self.similarity_search = SimilaritySearch()
    
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        async with self._lock:
            if isinstance(value, str):
                # Apply compression for string values
                tokens = value.split()
                compressed_tokens, scores = await self.compressor.compress(tokens, ratio=4)
                value = " ".join(compressed_tokens)
                if metadata:
                    metadata.compression_ratio = 4
                    metadata.tokens = compressed_tokens
            
            self._data[key] = value
            if metadata:
                self._metadata[key] = metadata
            return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        return self._data.get(key)
    
    async def evict(self, key: str) -> bool:
        async with self._lock:
            if key in self._data:
                del self._data[key]
                self._metadata.pop(key, None)
                return True
            return False
    
    async def find_similar(self, query_embedding: List[float], threshold: float = 0.6) -> List[Tuple[str, Any]]:
        """Find similar items with a lower threshold for archival data."""
        similar_keys = await self.similarity_search.find_similar(
            query_embedding,
            self._data,
            self._metadata,
            threshold
        )
        return [(key, self._data[key]) for key, _ in similar_keys]

class TripleStore:
    """Manages relation triple storage and retrieval."""
    
    def __init__(self, db_connection: Any):
        self.db = db_connection
        
    async def store_triple(self, subject: str, relation: str, object: str, 
                          embedding: Optional[List[float]] = None) -> str:
        """Store a relation triple and return its unique ID."""
        triple_id = f"{subject}:{relation}:{object}"
        await self.db.store_triple({
            'id': triple_id,
            'subject': subject,
            'relation': relation,
            'object': object,
            'embedding': embedding
        })
        return triple_id
        
    async def query_triples(self, 
                          subject: Optional[str] = None,
                          relation: Optional[str] = None,
                          object: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query triples matching the given pattern."""
        query = {}
        if subject:
            query['subject'] = subject
        if relation:
            query['relation'] = relation
        if object:
            query['object'] = object
        return await self.db.query_triples(query)

class LetheTier(MemoryTier):
    """Cold storage tier with integrated vector and graph capabilities."""
    
    def __init__(self, max_size: int, db_connection: ArangoMemoryStore):
        super().__init__(max_size)
        self.db = db_connection
        self.similarity_search = SimilaritySearch()
        
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        """Store data with vector embeddings and graph relationships."""
        try:
            async with self._lock:
                # Store in memory
                self._data[key] = value
                
                if metadata:
                    # Store in ArangoDB with vector embedding
                    memory_key = await self.db.store_memory(
                        content=value if isinstance(value, str) else str(value),
                        vector=metadata.vector_embedding or [],
                        metadata={
                            "tokens": metadata.tokens,
                            "semantics": metadata.semantics,
                            "last_access": metadata.last_access,
                            "access_count": metadata.access_count,
                            "compression_ratio": metadata.compression_ratio
                        },
                        importance=metadata.semantics.get("importance", 1.0)
                    )
                    
                    # Store relationships if present
                    if metadata.relation_triples:
                        for subject, relation, obj in metadata.relation_triples:
                            # Create nodes for subject and object if they don't exist
                            subject_key = await self._ensure_node_exists(subject)
                            object_key = await self._ensure_node_exists(obj)
                            
                            # Create relationship
                            await self.db.create_relationship(
                                from_key=subject_key,
                                to_key=object_key,
                                relation_type=relation,
                                weight=metadata.semantics.get(f"rel_weight_{relation}", 1.0)
                            )
                    
                    metadata.db_key = memory_key
                    self._metadata[key] = metadata
                    
                return True
                
        except Exception as e:
            logger.error(f"Error storing in Lethe: {str(e)}")
            return False
            
    async def _ensure_node_exists(self, content: str) -> str:
        """Ensure a node exists in the graph, create if not."""
        # Simple hash as key
        node_key = str(hash(content))
        
        try:
            # Try to find existing node
            existing = await self.db.find_similar_memories(
                query_vector=[0] * self.db.vector_dim,  # Placeholder vector
                limit=1
            )
            if existing:
                return existing[0]["key"]
                
            # Create new node if not found
            return await self.db.store_memory(
                content=content,
                vector=[0] * self.db.vector_dim,  # Placeholder vector
                metadata={},
                importance=1.0
            )
            
        except Exception as e:
            logger.error(f"Error ensuring node exists: {str(e)}")
            return node_key
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data with related context."""
        try:
            value = self._data.get(key)
            if value is not None and key in self._metadata:
                metadata = self._metadata[key]
                if hasattr(metadata, "db_key"):
                    # Get related context
                    related = await self.db.find_related_context(
                        memory_key=metadata.db_key,
                        max_hops=2
                    )
                    
                    # Update metadata with related information
                    metadata.related_context = related
                    
            return value
            
        except Exception as e:
            logger.error(f"Error retrieving from Lethe: {str(e)}")
            return None
            
    async def find_similar(self, query_vector: List[float], threshold: float = 0.7) -> List[Tuple[str, Any]]:
        """Find similar items using vector similarity in ArangoDB."""
        try:
            similar = await self.db.find_similar_memories(
                query_vector=query_vector,
                min_similarity=threshold
            )
            
            # Convert to expected format
            return [(doc["key"], self._data.get(doc["key"])) for doc in similar]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
