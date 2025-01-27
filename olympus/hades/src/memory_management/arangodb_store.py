from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
from loguru import logger
from arango import ArangoClient
from pydantic import BaseModel
from ..monitoring.phoenix_monitor import PhoenixMonitor

class VectorNode(BaseModel):
    """Represents a vector node in the memory graph."""
    content: str
    vector: List[float]
    timestamp: datetime
    importance_score: float
    metadata: Dict[str, Any]

class MemoryEdge(BaseModel):
    """Represents a semantic relationship between memory nodes."""
    from_node: str
    to_node: str
    relation_type: str
    weight: float
    context_window: int

class ArangoMemoryStore:
    """Integrated vector and graph memory store using ArangoDB."""
    
    def __init__(
        self,
        host: str = "http://localhost:8529",
        db_name: str = "hades_memory",
        username: str = "root",
        password: str = "",
        vector_dimension: int = 1536,  # Default for many embedding models
        phoenix_monitor: Optional[PhoenixMonitor] = None
    ):
        """Initialize ArangoDB store with vector and graph capabilities."""
        try:
            self.client = ArangoClient(hosts=host)
            self.db = self.client.db(db_name, username=username, password=password)
            self.vector_dim = vector_dimension
            self.monitor = phoenix_monitor
            
            # Initialize collections and indexes
            self._init_collections()
            
            if self.monitor:
                self.monitor.record_metric("store_init_success", 1)
                
        except Exception as e:
            logger.error(f"Failed to initialize ArangoDB store: {str(e)}")
            if self.monitor:
                self.monitor.record_metric("store_init_failure", 1)
            raise
        
    def _init_collections(self):
        """Initialize collections and indexes."""
        try:
            # Create memory nodes collection if it doesn't exist
            if not self.db.has_collection("memory_nodes"):
                self.db.create_collection("memory_nodes")
                nodes = self.db.collection("memory_nodes")
                
                # Create vector index for similarity search
                nodes.add_persistent_index(
                    fields=["vector[*]"],
                    sparse=False,
                    unique=False,
                    name="vector_index"
                )
                
                # Create metadata indexes
                nodes.add_hash_index(
                    fields=["metadata.source"],
                    sparse=True,
                    unique=False,
                    name="source_index"
                )
                
            # Create memory edges collection if it doesn't exist
            if not self.db.has_collection("memory_edges"):
                self.db.create_collection("memory_edges", edge=True)
                edges = self.db.collection("memory_edges")
                
                # Create edge indexes
                edges.add_hash_index(
                    fields=["relation_type"],
                    sparse=False,
                    unique=False,
                    name="relation_index"
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")
            raise
            
    async def store_memory(
        self,
        content: str,
        vector: List[float],
        metadata: Dict[str, Any],
        importance_score: float = 0.5
    ) -> str:
        """Store memory node with vector embedding."""
        try:
            node = VectorNode(
                content=content,
                vector=vector,
                timestamp=datetime.now(),
                importance_score=importance_score,
                metadata=metadata
            )
            
            result = self.db.collection("memory_nodes").insert(node.model_dump())
            node_id = result["_id"]
            
            if self.monitor:
                self.monitor.record_metric("memory_store_success", 1)
                
            return node_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            if self.monitor:
                self.monitor.record_metric("memory_store_failure", 1)
            raise
            
    async def create_edge(
        self,
        from_node: str,
        to_node: str,
        relation_type: str,
        weight: float = 1.0,
        context_window: int = 5
    ) -> str:
        """Create edge between memory nodes."""
        try:
            edge = MemoryEdge(
                from_node=from_node,
                to_node=to_node,
                relation_type=relation_type,
                weight=weight,
                context_window=context_window
            )
            
            result = self.db.collection("memory_edges").insert(edge.model_dump())
            edge_id = result["_id"]
            
            if self.monitor:
                self.monitor.record_metric("edge_create_success", 1)
                
            return edge_id
            
        except Exception as e:
            logger.error(f"Failed to create edge: {str(e)}")
            if self.monitor:
                self.monitor.record_metric("edge_create_failure", 1)
            raise
            
    async def find_similar_memories(
        self,
        query_vector: List[float],
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar memories using vector similarity."""
        try:
            # AQL query for vector similarity search
            query = """
            FOR doc IN memory_nodes
                LET similarity = LENGTH(doc.vector) == LENGTH(@query_vector)
                    ? 1 - SQRT(SUM(
                        FOR i IN RANGE(0, LENGTH(@query_vector) - 1)
                            RETURN POW(doc.vector[i] - @query_vector[i], 2)
                    ))
                    : 0
                FILTER similarity >= @min_similarity
                SORT similarity DESC
                LIMIT @limit
                RETURN MERGE(
                    KEEP(doc, ["_id", "content", "vector", "metadata"]),
                    { similarity: similarity }
                )
            """
            
            cursor = self.db.aql.execute(
                query,
                bind_vars={
                    "query_vector": query_vector,
                    "min_similarity": min_similarity,
                    "limit": limit
                }
            )
            
            results = [doc for doc in cursor.batch()]
            
            if self.monitor:
                self.monitor.record_metric("similarity_search_success", 1)
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to find similar memories: {str(e)}")
            if self.monitor:
                self.monitor.record_metric("similarity_search_failure", 1)
            raise
            
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory by ID."""
        try:
            memory = self.db.collection("memory_nodes").get(memory_id)
            return memory
            
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {str(e)}")
            raise
            
    async def update_memory(
        self,
        memory_id: str,
        importance_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update memory node properties."""
        try:
            update_data = {}
            if importance_score is not None:
                update_data["importance_score"] = importance_score
            if metadata is not None:
                update_data["metadata"] = metadata
                
            if update_data:
                self.db.collection("memory_nodes").update(memory_id, update_data)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {str(e)}")
            raise
            
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory node and its edges."""
        try:
            self.db.collection("memory_nodes").delete(memory_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {str(e)}")
            raise
