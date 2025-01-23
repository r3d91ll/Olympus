from typing import Any, Dict, List, Optional
from arango import ArangoClient
from loguru import logger

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
            
            # Initialize collections if they don't exist
            if not self.db.has_collection("data"):
                self.db.create_collection("data")
                
            logger.info("Successfully connected to ArangoDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ArangoDB: {str(e)}")
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
