from typing import Any, Dict, List, Optional
from arango import ArangoClient
from loguru import logger
from datetime import datetime

from core.config import settings

class ArangoDB:
    def __init__(self):
        self.client = ArangoClient(
            hosts=f"http://{settings.ARANGO_HOST}:{settings.ARANGO_PORT}"
        )
        self.db = None
        
    async def connect(self) -> bool:
        """Connect to ArangoDB and initialize database."""
        try:
            sys_db = self.client.db(
                "_system",
                username=settings.ARANGO_USER,
                password=settings.ARANGO_PASSWORD
            )
            
            if not sys_db.has_database(settings.ARANGO_DB):
                sys_db.create_database(settings.ARANGO_DB)
                
            self.db = self.client.db(
                settings.ARANGO_DB,
                username=settings.ARANGO_USER,
                password=settings.ARANGO_PASSWORD
            )
            
            # Initialize collections
            await self.init_collections()
                
            logger.info("Successfully connected to ArangoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ArangoDB: {str(e)}")
            return False

    async def init_collections(self) -> bool:
        """Initialize all required collections."""
        try:
            # Basic data collection
            if not self.db.has_collection("data"):
                self.db.create_collection("data")
            
            # Vector collection for embeddings
            if not self.db.has_collection("vectors"):
                vectors = self.db.create_collection("vectors")
                # Create HNSW index for vector similarity search
                vectors.add_index({
                    "type": "vector",
                    "fields": ["embedding"],
                    "algorithm": "hnsw",
                    "params": {
                        "maxElements": 1000000,
                        "efConstruction": 128,
                        "ef": 64,
                        "M": 16
                    }
                })
                logger.info("Created vectors collection with HNSW index")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")
            return False
            
    async def store(self, key: str, value: Any) -> bool:
        """Store data in ArangoDB."""
        try:
            collection = self.db.collection("data")
            doc = {"_key": key, "value": value}
            collection.insert(doc, overwrite=True)
            return True
        except Exception as e:
            logger.error(f"Failed to store data in ArangoDB: {str(e)}")
            return False
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from ArangoDB."""
        try:
            collection = self.db.collection("data")
            doc = collection.get(key)
            return doc["value"] if doc else None
        except Exception as e:
            logger.error(f"Failed to retrieve data from ArangoDB: {str(e)}")
            return None
            
    async def delete(self, key: str) -> bool:
        """Delete data from ArangoDB."""
        try:
            collection = self.db.collection("data")
            collection.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete data from ArangoDB: {str(e)}")
            return False

    async def store_vector(
        self,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
        chunk_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> bool:
        """Store a vector embedding with its text and metadata."""
        try:
            collection = self.db.collection("vectors")
            doc = {
                "_key": chunk_id if chunk_id else str(hash(text)),
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
                "parent_id": parent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            collection.insert(doc, overwrite=True)
            logger.debug(f"Stored vector for chunk_id: {doc['_key']}")
            return True
        except Exception as e:
            logger.error(f"Failed to store vector: {str(e)}")
            return False

    async def search_vectors(
        self,
        query_vector: List[float],
        k: int = 3,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors using HNSW index."""
        try:
            collection = self.db.collection("vectors")
            
            # Build AQL query
            aql = """
            FOR doc IN vectors
            SEARCH ANALYZER(VECTOR_DISTANCE(doc.embedding, @query_vector) < 1.0, "vector")
            """
            
            # Add metadata filter if provided
            if metadata_filter:
                filter_conditions = []
                for key, value in metadata_filter.items():
                    filter_conditions.append(f"doc.metadata.{key} == @{key}")
                if filter_conditions:
                    aql += f"\nFILTER {' AND '.join(filter_conditions)}"
            
            # Add sorting and limit
            aql += """
            SORT VECTOR_DISTANCE(doc.embedding, @query_vector)
            LIMIT @k
            RETURN {
                text: doc.text,
                distance: VECTOR_DISTANCE(doc.embedding, @query_vector),
                metadata: doc.metadata,
                chunk_id: doc._key,
                parent_id: doc.parent_id,
                timestamp: doc.timestamp
            }
            """
            
            # Prepare bind vars
            bind_vars = {"query_vector": query_vector, "k": k}
            if metadata_filter:
                bind_vars.update(metadata_filter)
            
            # Execute query
            cursor = self.db.aql.execute(aql, bind_vars=bind_vars)
            results = [doc for doc in cursor]
            
            logger.debug(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search vectors: {str(e)}")
            return []

    async def delete_vectors(
        self,
        chunk_ids: Optional[List[str]] = None,
        parent_id: Optional[str] = None
    ) -> bool:
        """Delete vectors by chunk IDs or parent ID."""
        try:
            collection = self.db.collection("vectors")
            
            if chunk_ids:
                for chunk_id in chunk_ids:
                    collection.delete(chunk_id)
                logger.debug(f"Deleted vectors with chunk_ids: {chunk_ids}")
            
            if parent_id:
                aql = """
                FOR doc IN vectors
                FILTER doc.parent_id == @parent_id
                REMOVE doc IN vectors
                """
                self.db.aql.execute(aql, bind_vars={"parent_id": parent_id})
                logger.debug(f"Deleted vectors with parent_id: {parent_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            return False
