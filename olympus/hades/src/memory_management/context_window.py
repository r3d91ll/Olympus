from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import torch
from loguru import logger

@dataclass
class ContextBlock:
    """Represents a block of context with its attention cache."""
    tokens: List[int]  # Token IDs
    position_ids: List[int]  # Position IDs for tokens
    kv_cache: Optional[Dict[str, torch.Tensor]]  # KV cache for this block
    importance_score: float  # Score for determining which blocks to keep in GPU
    last_access_time: float  # Timestamp of last access
    
class HybridContextWindow:
    """Manages context between GPU and CPU memory."""
    
    def __init__(
        self,
        max_gpu_context: int = 32768,  # 32K tokens for GPU
        gpu_cache_size: int = 16384,   # 16K tokens reserved for cache
        cpu_context_size: int = 65536  # 64K tokens in CPU
    ):
        self.max_gpu_context = max_gpu_context
        self.gpu_cache_size = gpu_cache_size
        self.gpu_sliding_size = max_gpu_context - gpu_cache_size
        self.cpu_context_size = cpu_context_size
        
        # GPU context blocks (cache + sliding window)
        self.gpu_cache_blocks: List[ContextBlock] = []
        self.gpu_sliding_blocks: List[ContextBlock] = []
        
        # CPU context blocks
        self.cpu_blocks: List[ContextBlock] = []
        
        # Current token counts
        self.gpu_cache_tokens = 0
        self.gpu_sliding_tokens = 0
        self.cpu_tokens = 0
        
    def _calculate_importance(self, block: ContextBlock, current_time: float) -> float:
        """Calculate importance score for a block based on recency and content."""
        time_factor = 1.0 / (1.0 + (current_time - block.last_access_time))
        return block.importance_score * time_factor
    
    async def add_context(
        self,
        tokens: List[int],
        kv_cache: Optional[Dict[str, torch.Tensor]] = None,
        position_ids: Optional[List[int]] = None
    ) -> None:
        """Add new context, managing GPU and CPU storage."""
        if position_ids is None:
            position_ids = list(range(len(tokens)))
            
        # Create new block
        new_block = ContextBlock(
            tokens=tokens,
            position_ids=position_ids,
            kv_cache=kv_cache,
            importance_score=1.0,  # New blocks start with high importance
            last_access_time=torch.cuda.Event().record()
        )
        
        # If GPU sliding window is full, move least important block to CPU
        if self.gpu_sliding_tokens + len(tokens) > self.gpu_sliding_size:
            await self._move_to_cpu()
            
        # Add new block to GPU sliding window
        self.gpu_sliding_blocks.append(new_block)
        self.gpu_sliding_tokens += len(tokens)
        
        # If CPU is full, remove oldest blocks
        while self.cpu_tokens > self.cpu_context_size:
            removed_block = self.cpu_blocks.pop(0)
            self.cpu_tokens -= len(removed_block.tokens)
            
    async def _move_to_cpu(self) -> None:
        """Move least important block from GPU sliding window to CPU."""
        if not self.gpu_sliding_blocks:
            return
            
        current_time = torch.cuda.Event().record()
        
        # Find least important block
        block_scores = [
            (i, self._calculate_importance(block, current_time))
            for i, block in enumerate(self.gpu_sliding_blocks)
        ]
        least_important_idx = min(block_scores, key=lambda x: x[1])[0]
        
        # Move block to CPU
        block = self.gpu_sliding_blocks.pop(least_important_idx)
        
        # Convert KV cache to CPU tensor if it exists
        if block.kv_cache:
            cpu_kv_cache = {
                key: tensor.cpu() 
                for key, tensor in block.kv_cache.items()
            }
            block.kv_cache = cpu_kv_cache
            
        self.cpu_blocks.append(block)
        self.gpu_sliding_tokens -= len(block.tokens)
        self.cpu_tokens += len(block.tokens)
        
    async def _move_to_gpu(self, block_idx: int) -> None:
        """Move a block from CPU to GPU."""
        if block_idx >= len(self.cpu_blocks):
            return
            
        block = self.cpu_blocks.pop(block_idx)
        
        # Convert KV cache back to GPU if it exists
        if block.kv_cache:
            gpu_kv_cache = {
                key: tensor.cuda() 
                for key, tensor in block.kv_cache.items()
            }
            block.kv_cache = gpu_kv_cache
            
        # Make space in GPU sliding window if needed
        while (self.gpu_sliding_tokens + len(block.tokens) > self.gpu_sliding_size):
            await self._move_to_cpu()
            
        self.gpu_sliding_blocks.append(block)
        self.gpu_sliding_tokens += len(block.tokens)
        self.cpu_tokens -= len(block.tokens)
        
    async def get_context_for_position(self, position: int) -> Tuple[List[int], Optional[Dict[str, torch.Tensor]]]:
        """Get context and KV cache for a specific position."""
        # Check GPU cache first
        total_pos = 0
        for block in self.gpu_cache_blocks:
            if total_pos <= position < total_pos + len(block.tokens):
                block.last_access_time = torch.cuda.Event().record()
                return block.tokens, block.kv_cache
            total_pos += len(block.tokens)
            
        # Check GPU sliding window
        for block in self.gpu_sliding_blocks:
            if total_pos <= position < total_pos + len(block.tokens):
                block.last_access_time = torch.cuda.Event().record()
                return block.tokens, block.kv_cache
            total_pos += len(block.tokens)
            
        # Check CPU blocks and move to GPU if found
        for i, block in enumerate(self.cpu_blocks):
            if total_pos <= position < total_pos + len(block.tokens):
                await self._move_to_gpu(i)
                block.last_access_time = torch.cuda.Event().record()
                return block.tokens, block.kv_cache
            total_pos += len(block.tokens)
            
        return [], None
        
    async def promote_to_cache(self, block_idx: int) -> bool:
        """Promote a block from sliding window to cache if important enough."""
        if block_idx >= len(self.gpu_sliding_blocks):
            return False
            
        if self.gpu_cache_tokens + len(self.gpu_sliding_blocks[block_idx].tokens) <= self.gpu_cache_size:
            # Move block to cache
            block = self.gpu_sliding_blocks.pop(block_idx)
            self.gpu_cache_blocks.append(block)
            self.gpu_cache_tokens += len(block.tokens)
            self.gpu_sliding_tokens -= len(block.tokens)
            return True
            
        return False
        
    def get_memory_stats(self) -> Dict[str, int]:
        """Get current memory usage statistics."""
        return {
            "gpu_cache_tokens": self.gpu_cache_tokens,
            "gpu_sliding_tokens": self.gpu_sliding_tokens,
            "cpu_tokens": self.cpu_tokens,
            "total_tokens": self.gpu_cache_tokens + self.gpu_sliding_tokens + self.cpu_tokens
        }
