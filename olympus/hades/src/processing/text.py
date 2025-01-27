from typing import List, Dict, Any
import asyncio
from pathlib import Path
from loguru import logger
import tiktoken
import aiofiles

async def read_file(file_path: Path) -> str:
    """Read file content asynchronously."""
    try:
        async with aiofiles.open(str(file_path), 'r', encoding='utf-8') as f:
            return await f.read()
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {str(e)}")
        raise

async def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Failed to count tokens: {str(e)}")
        raise

async def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
    encoding_name: str = "cl100k_base"
) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks with metadata."""
    try:
        # Validate parameters
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size")
            
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        chunks = []
        
        # Early return for small texts
        if len(tokens) <= chunk_size:
            return [{
                "text": text,
                "start_idx": 0,
                "end_idx": len(text),
                "tokens": len(tokens)
            }]
            
        current_pos = 0
        while current_pos < len(tokens):
            # Get chunk tokens
            chunk_end = min(current_pos + chunk_size, len(tokens))
            chunk_tokens = tokens[current_pos:chunk_end]
            
            # Decode chunk
            chunk_text = encoding.decode(chunk_tokens)
            
            # Store chunk with metadata
            chunks.append({
                "text": chunk_text,
                "start_idx": current_pos,
                "end_idx": chunk_end,
                "tokens": len(chunk_tokens)
            })
            
            # Move position considering overlap
            # Ensure we make progress even with large overlap
            current_pos = chunk_end - min(overlap, chunk_end - current_pos - 1)
            if current_pos >= len(tokens):
                break
            
        return chunks
        
    except Exception as e:
        logger.error(f"Failed to chunk text: {str(e)}")
        raise

async def process_file(
    file_path: Path,
    chunk_size: int = 1000,
    overlap: int = 100
) -> List[Dict[str, Any]]:
    """Process file into chunks with metadata."""
    try:
        # Read file
        content = await read_file(file_path)
        
        # Get file stats
        stats = {
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": file_path.suffix
        }
        
        # Chunk content
        chunks = await chunk_text(
            text=content,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        # Add file metadata to chunks
        for chunk in chunks:
            chunk.update(stats)
            
        return chunks
        
    except Exception as e:
        logger.error(f"Failed to process file {file_path}: {str(e)}")
        raise
