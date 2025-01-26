"""Vector search service using ArangoDB's FAISS integration."""

from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from prometheus_client import Summary, Counter

from .arango import ArangoDB
from core.config import settings

# Metrics
VECTOR_INSERT_TIME = Summary('vector_insert_seconds', 'Time spent inserting vectors')
VECTOR_SEARCH_TIME = Summary('vector_search_seconds', 'Time spent searching vectors')
VECTOR_OPS = Counter('vector_operations_total', 'Total vector operations', ['operation'])

class VectorStore:
    """Vector storage and search using ArangoDB's vector capabilities."""
    
    def __init__(self, db: ArangoDB):
        """Initialize vector store with ArangoDB connection."""
        self.db = db
        self._collection_name = "vectors"
        self._index_name = "vector_index"
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize vector store and create necessary collections/indexes."""
        try:
            if self._initialized:
                return True
                
            # Ensure collection exists
            if not self.db.db.has_collection(self._collection_name):
                collection = self.db.db.create_collection(self._collection_name)
                
                # Create FAISS index
                collection.add_persistent_index({
                    "type": "inverted",
                    "fields": ["vector"],
                    "analyzer": "identity"
                })
                
                # Create vector index using FAISS
                collection.add_persistent_index({
                    "type": "vector",
                    "fields": ["vector"],
                    "algorithm": "faiss",
                    "dimension": settings.VECTOR_DIMENSION,
                    "similarity": "euclidean"  # or "cosine" based on needs
                })
                
            self._initialized = True
            logger.info("Vector store initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            return False
            
    async def store(
        self,
        key: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a vector with optional metadata.
        
        Args:
            key: Unique identifier
            vector: Vector data as list of floats
            metadata: Optional metadata to store with vector
            
        Returns:
            bool: Success status
        """
        try:
            with VECTOR_INSERT_TIME.time():
                collection = self.db.db.collection(self._collection_name)
                
                doc = {
                    "_key": key,
                    "vector": vector,
                    "metadata": metadata or {}
                }
                
                collection.insert(doc, overwrite=True)
                VECTOR_OPS.labels(operation="insert").inc()
                return True
                
        except Exception as e:
            logger.error(f"Failed to store vector: {str(e)}")
            return False
            
    async def search(
        self,
        query_vector: List[float],
        k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            metadata_filter: Optional filter for metadata fields
            
        Returns:
            List of tuples (key, distance, metadata)
        """
        try:
            with VECTOR_SEARCH_TIME.time():
                collection = self.db.db.collection(self._collection_name)
                
                # Build AQL query
                aql = """
                FOR doc IN VECTOR_NEAREST(
                    @collection,
                    @vector,
                    @k,
                    "vector"
                )
                """
                
                # Add metadata filter if provided
                if metadata_filter:
                    filter_conditions = []
                    for key, value in metadata_filter.items():
                        filter_conditions.append(f'doc.metadata.{key} == @{key}')
                    if filter_conditions:
                        aql += f" FILTER {' AND '.join(filter_conditions)}"
                
                aql += " RETURN { key: doc._key, distance: doc.distance, metadata: doc.metadata }"
                
                # Execute query
                bind_vars = {
                    "collection": self._collection_name,
                    "vector": query_vector,
                    "k": k,
                    **(metadata_filter or {})
                }
                
                cursor = self.db.db.aql.execute(aql, bind_vars=bind_vars)
                results = [(doc["key"], doc["distance"], doc["metadata"]) for doc in cursor]
                
                VECTOR_OPS.labels(operation="search").inc()
                return results
                
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
            
    async def delete(self, key: str) -> bool:
        """Delete a vector by key."""
        try:
            collection = self.db.db.collection(self._collection_name)
            collection.delete(key)
            VECTOR_OPS.labels(operation="delete").inc()
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector: {str(e)}")
            return False
            
    async def update_metadata(
        self,
        key: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update metadata for a vector."""
        try:
            collection = self.db.db.collection(self._collection_name)
            collection.update({"_key": key}, {"metadata": metadata})
            VECTOR_OPS.labels(operation="update_metadata").inc()
            return True
        except Exception as e:
            logger.error(f"Failed to update vector metadata: {str(e)}")
            return False
