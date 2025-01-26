from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
from loguru import logger
from arango import ArangoClient
from pydantic import BaseModel
from phoenix_monitor import PhoenixMonitor  # Import PhoenixMonitor

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
        self.client = ArangoClient(hosts=host)
        self.db = self.client.db(db_name, username=username, password=password)
        self.vector_dim = vector_dimension
        self.monitor = phoenix_monitor
        
        # Initialize collections and indexes
        self._init_collections()
        
    def _init_collections(self):
        """Initialize collections and indexes."""
        if not self.db.has_collection("memory_nodes"):
            self.db.create_collection("memory_nodes")
            # Create vector index for similarity search
            self.db.collection("memory_nodes").add_persistent_index(
                fields=["vector[*]"],
                name="vector_index",
                in_background=True
            )
            
        if not self.db.has_collection("memory_edges"):
            self.db.create_collection("memory_edges", edge=True)
            
        # Create graph if it doesn't exist
        if not self.db.has_graph("memory_graph"):
            graph = self.db.create_graph("memory_graph")
            graph.create_edge_definition(
                edge_collection="memory_edges",
                from_vertex_collections=["memory_nodes"],
                to_vertex_collections=["memory_nodes"]
            )
            
        if self.monitor:
            # Record initial metrics
            self._update_graph_metrics()
    
    async def store_memory(
        self,
        content: str,
        vector: List[float],
        metadata: Dict[str, Any],
        importance: float = 1.0
    ) -> str:
        """Store a memory node with its vector embedding."""
        if self.monitor:
            async with self.monitor.time_operation("arangodb", "store", "memory"):
                result = await self._store_memory_internal(content, vector, metadata, importance)
                self.monitor.record_operation("arangodb", "store", "memory")
                return result
        else:
            return await self._store_memory_internal(content, vector, metadata, importance)
            
    async def _store_memory_internal(
        self,
        content: str,
        vector: List[float],
        metadata: Dict[str, Any],
        importance: float
    ) -> str:
        node = VectorNode(
            content=content,
            vector=vector,
            timestamp=datetime.utcnow(),
            importance_score=importance,
            metadata=metadata
        )
        
        result = self.db.collection("memory_nodes").insert(node.dict())
        
        if self.monitor:
            # Record memory usage after insert
            collection_size = self.db.collection("memory_nodes").statistics()["figures"]["documentsSize"]
            self.monitor.record_memory_usage("arangodb", "memory_nodes", collection_size)
            self._update_graph_metrics()
            
        return result["_key"]
    
    async def create_relationship(
        self,
        from_key: str,
        to_key: str,
        relation_type: str,
        weight: float = 1.0,
        context_window: int = 0
    ) -> str:
        """Create a relationship between two memory nodes."""
        edge = MemoryEdge(
            from_node=from_key,
            to_node=to_key,
            relation_type=relation_type,
            weight=weight,
            context_window=context_window
        )
        
        result = self.db.collection("memory_edges").insert(edge.dict())
        return result["_key"]
    
    async def find_similar_memories(
        self,
        query_vector: List[float],
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar memories using vector similarity search."""
        if self.monitor:
            async with self.monitor.time_operation("arangodb", "similarity_search", "memory"):
                results = await self._find_similar_internal(query_vector, limit, min_similarity)
                
                # Record similarity scores
                for result in results:
                    self.monitor.record_similarity_score("arangodb", "memory", result["similarity"])
                    
                return results
        else:
            return await self._find_similar_internal(query_vector, limit, min_similarity)
            
    async def _find_similar_internal(
        self,
        query_vector: List[float],
        limit: int,
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        aql = """
        FOR doc IN memory_nodes
            LET similarity = COSINE_SIMILARITY(doc.vector, @query_vector)
            FILTER similarity >= @min_similarity
            SORT similarity DESC
            LIMIT @limit
            RETURN {
                key: doc._key,
                content: doc.content,
                similarity: similarity,
                metadata: doc.metadata,
                timestamp: doc.timestamp
            }
        """
        
        cursor = self.db.aql.execute(
            aql,
            bind_vars={
                "query_vector": query_vector,
                "min_similarity": min_similarity,
                "limit": limit
            }
        )
        return [doc for doc in cursor]
    
    async def find_related_context(
        self,
        memory_key: str,
        max_hops: int = 2,
        min_weight: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Find related memories through graph traversal."""
        aql = """
        FOR v, e, p IN 1..@max_hops
            OUTBOUND @start_vertex memory_edges
            FILTER e.weight >= @min_weight
            RETURN {
                key: v._key,
                content: v.content,
                path_length: LENGTH(p.edges),
                total_weight: SUM(p.edges[*].weight),
                metadata: v.metadata
            }
        """
        
        cursor = self.db.aql.execute(
            aql,
            bind_vars={
                "start_vertex": f"memory_nodes/{memory_key}",
                "max_hops": max_hops,
                "min_weight": min_weight
            }
        )
        return [doc for doc in cursor]
    
    async def get_context_window(
        self,
        center_key: str,
        window_size: int = 5
    ) -> List[Dict[str, Any]]:
        """Get memories within a specific context window."""
        aql = """
        FOR v, e IN 1..1 ANY @center memory_edges
            FILTER e.context_window <= @window_size
            SORT e.context_window
            RETURN {
                key: v._key,
                content: v.content,
                window_position: e.context_window,
                metadata: v.metadata
            }
        """
        
        cursor = self.db.aql.execute(
            aql,
            bind_vars={
                "center": f"memory_nodes/{center_key}",
                "window_size": window_size
            }
        )
        return [doc for doc in cursor]
    
    async def prune_old_memories(
        self,
        older_than_days: int = 30,
        keep_min_importance: float = 0.8
    ) -> int:
        """Remove old, unimportant memories while preserving their relationships."""
        aql = """
        FOR doc IN memory_nodes
            FILTER doc.timestamp <= DATE_SUBTRACT(DATE_NOW(), @days, "day")
            FILTER doc.importance_score < @min_importance
            REMOVE doc IN memory_nodes
            RETURN OLD
        """
        
        cursor = self.db.aql.execute(
            aql,
            bind_vars={
                "days": older_than_days,
                "min_importance": keep_min_importance
            }
        )
        return cursor.statistics()["removed"]

    def _update_graph_metrics(self):
        """Update Phoenix metrics for graph statistics."""
        if not self.monitor:
            return
            
        try:
            # Get node and edge counts
            node_count = self.db.collection("memory_nodes").count()
            edge_count = self.db.collection("memory_edges").count()
            
            # Get memory usage for each collection
            nodes_size = self.db.collection("memory_nodes").statistics()["figures"]["documentsSize"]
            edges_size = self.db.collection("memory_edges").statistics()["figures"]["documentsSize"]
            
            # Record memory usage
            self.monitor.record_memory_usage("arangodb", "memory_nodes", nodes_size)
            self.monitor.record_memory_usage("arangodb", "memory_edges", edges_size)
            
            # Get average node degree
            aql = """
            FOR v IN memory_nodes
                LET degree = LENGTH(
                    FOR e IN memory_edges
                        FILTER e._from == v._id OR e._to == v._id
                        RETURN 1
                )
                COLLECT AGGREGATE avg_degree = AVG(degree)
                RETURN avg_degree
            """
            cursor = self.db.aql.execute(aql)
            avg_degree = next(cursor, [0])[0]
            
            # Update graph metrics
            self.monitor.update_graph_metrics("arangodb", {
                "nodes": node_count,
                "edges": edge_count,
                "avg_degree": avg_degree,
                "density": edge_count / (node_count * (node_count - 1)) if node_count > 1 else 0
            })
            
            # Update cache stats if available
            cache_stats = self.db.statistics()
            if "cache" in cache_stats:
                hits = cache_stats["cache"]["hits"]
                misses = cache_stats["cache"]["misses"]
                self.monitor.update_cache_stats("arangodb", "memory", hits, misses)
                
        except Exception as e:
            logger.error(f"Error updating graph metrics: {str(e)}")
