from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
import asyncio
from loguru import logger
from pydantic import BaseModel

class ContextMetadata(BaseModel):
    """Metadata for context-aware memory management."""
    tokens: List[str]
    semantics: Dict[str, float]
    last_access: float
    access_count: int
    
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
    """Warm memory tier for recent data."""
    
    def __init__(self, max_size: int, window_size: int):
        super().__init__(max_size)
        self.window_size = window_size
    
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

class TartarusTier(MemoryTier):
    """Archival tier for potentially relevant but inactive data."""
    
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        async with self._lock:
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

class LetheTier(MemoryTier):
    """Cold storage tier with database backend."""
    
    def __init__(self, max_size: int, db_connection: Any):
        super().__init__(max_size)
        self.db = db_connection
    
    async def store(self, key: str, value: Any, metadata: Optional[ContextMetadata] = None) -> bool:
        try:
            await self.db.store(key, value, metadata.dict() if metadata else None)
            return True
        except Exception as e:
            logger.error(f"Error storing in Lethe: {str(e)}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        try:
            return await self.db.retrieve(key)
        except Exception as e:
            logger.error(f"Error retrieving from Lethe: {str(e)}")
            return None
    
    async def evict(self, key: str) -> bool:
        try:
            return await self.db.delete(key)
        except Exception as e:
            logger.error(f"Error evicting from Lethe: {str(e)}")
            return False
