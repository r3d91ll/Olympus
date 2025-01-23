from typing import Any, Optional, Dict, Tuple
from loguru import logger
import time

from .memory_tier import (
    ElysiumTier, AsphodelTier, TartarusTier, LetheTier,
    ContextMetadata
)
from core.config import settings
from core.logging import log_memory_stats
from core.context import analyze_context, AnalysisResult

class MemoryManager:
    def __init__(self, db_connection: Any):
        """Initialize memory manager with all tiers."""
        self.elysium = ElysiumTier(settings.ELYSIUM_MAX_SIZE)
        self.asphodel = AsphodelTier(
            max_size=settings.ASPHODEL_MAX_SIZE,
            window_size=settings.ASPHODEL_WINDOW_SIZE
        )
        self.tartarus = TartarusTier(float('inf'))  # No size limit for archival
        self.lethe = LetheTier(float('inf'), db_connection)
        
    async def _update_stats(self):
        """Update memory statistics for monitoring."""
        log_memory_stats(
            elysium_size=self.elysium.current_size,
            asphodel_size=self.asphodel.current_size,
            lethe_size=self.lethe.current_size,
            metrics={
                "elysium_items": len(self.elysium._data),
                "asphodel_items": len(self.asphodel._data),
                "tartarus_items": len(self.tartarus._data),
                "memory_utilization": (
                    (self.elysium.current_size + self.asphodel.current_size) /
                    (settings.ELYSIUM_MAX_SIZE + settings.ASPHODEL_MAX_SIZE)
                ) * 100
            }
        )
        
    async def store_with_context(
        self,
        key: str,
        value: Any,
        context: str
    ) -> Tuple[bool, AnalysisResult]:
        """
        Store data with context analysis for optimal tier placement.
        
        Args:
            key: Storage key
            value: Value to store
            context: Context string for analysis
            
        Returns:
            Tuple of (success, analysis_result)
        """
        try:
            # Analyze context
            analysis = await analyze_context(context)
            
            # Store in appropriate tier
            success = await self.store(
                key,
                value,
                metadata=analysis.metadata,
                tier=analysis.suggested_tier
            )
            
            return success, analysis
            
        except Exception as e:
            logger.error(f"Error storing with context: {str(e)}")
            return False, None
        
    async def store(
        self,
        key: str,
        value: Any,
        metadata: Optional[ContextMetadata] = None,
        tier: Optional[str] = None
    ) -> bool:
        """Store data in the appropriate memory tier."""
        try:
            success = False
            if tier == "elysium":
                success = await self.elysium.store(key, value, metadata)
            elif tier == "asphodel":
                success = await self.asphodel.store(key, value, metadata)
            elif tier == "tartarus":
                success = await self.tartarus.store(key, value, metadata)
            elif tier == "lethe":
                success = await self.lethe.store(key, value, metadata)
            else:
                logger.error(f"Invalid tier specified: {tier}")
                return False
                
            await self._update_stats()
            return success
            
        except Exception as e:
            logger.error(f"Error storing data: {str(e)}")
            return False
    
    async def retrieve(self, key: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Retrieve data from memory tiers.
        Returns tuple of (value, tier_found_in)
        """
        # Check tiers in order of access speed
        if value := await self.elysium.retrieve(key):
            return value, "elysium"
            
        if value := await self.asphodel.retrieve(key):
            # Consider promoting to Elysium
            metadata = await self.asphodel.get_metadata(key)
            if metadata and metadata.access_count > 5:
                await self.store(key, value, metadata, "elysium")
                await self.asphodel.evict(key)
            return value, "asphodel"
            
        if value := await self.tartarus.retrieve(key):
            # Consider promoting to Asphodel
            metadata = await self.tartarus.get_metadata(key)
            if metadata:
                metadata.access_count += 1
                await self.store(key, value, metadata, "asphodel")
                await self.tartarus.evict(key)
            return value, "tartarus"
            
        if value := await self.lethe.retrieve(key):
            # Always promote from Lethe to Tartarus on access
            await self.store(key, value, None, "tartarus")
            return value, "lethe"
            
        return None, None
        
    async def evict(self, key: str) -> bool:
        """Evict data from all tiers."""
        success = False
        success |= await self.elysium.evict(key)
        success |= await self.asphodel.evict(key)
        success |= await self.tartarus.evict(key)
        success |= await self.lethe.evict(key)
        
        if success:
            await self._update_stats()
            
        return success
