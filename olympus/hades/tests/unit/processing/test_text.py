import pytest
from pathlib import Path
import tempfile
import asyncio
from olympus.hades.src.processing.text import (
    read_file,
    count_tokens,
    chunk_text,
    process_file
)

@pytest.fixture
def sample_text():
    """Create sample text for testing."""
    return "This is a test text. " * 20  # Create text long enough to chunk but not too long

@pytest.fixture
def temp_file(sample_text):
    """Create temporary file with sample text."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(sample_text)
        return Path(f.name)

@pytest.mark.asyncio
async def test_read_file(temp_file):
    """Test file reading."""
    content = await read_file(temp_file)
    assert isinstance(content, str)
    assert len(content) > 0
    
    with pytest.raises(FileNotFoundError):
        await read_file(Path("nonexistent.txt"))

@pytest.mark.asyncio
async def test_count_tokens():
    """Test token counting."""
    text = "This is a test."
    count = await count_tokens(text)
    assert isinstance(count, int)
    assert count > 0
    
    with pytest.raises(Exception):
        await count_tokens(text, encoding_name="nonexistent")

@pytest.mark.asyncio
async def test_chunk_text(sample_text):
    """Test text chunking."""
    # Test normal chunking
    chunks = await chunk_text(
        text=sample_text,
        chunk_size=50,
        overlap=10
    )
    
    assert isinstance(chunks, list)
    assert len(chunks) > 1
    
    # Test chunk properties
    for chunk in chunks:
        assert "text" in chunk
        assert "start_idx" in chunk
        assert "end_idx" in chunk
        assert "tokens" in chunk
        assert chunk["tokens"] <= 50  # Should not exceed chunk_size
        
    # Test overlap
    for i in range(len(chunks) - 1):
        current_end = chunks[i]["end_idx"]
        next_start = chunks[i + 1]["start_idx"]
        overlap_size = current_end - next_start
        assert overlap_size > 0  # Should have some overlap
        assert overlap_size <= 10  # Should not exceed specified overlap
        
    # Test invalid overlap
    with pytest.raises(ValueError):
        await chunk_text(
            text=sample_text,
            chunk_size=50,
            overlap=50  # Equal to chunk_size
        )
        
    # Test small text
    small_chunks = await chunk_text(
        text="Small text.",
        chunk_size=50,
        overlap=10
    )
    assert len(small_chunks) == 1

@pytest.mark.asyncio
async def test_process_file(temp_file):
    """Test full file processing."""
    chunks = await process_file(
        file_path=temp_file,
        chunk_size=50,
        overlap=10
    )
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    
    # Test chunk metadata
    for chunk in chunks:
        assert "file_name" in chunk
        assert "file_size" in chunk
        assert "file_type" in chunk
        assert "text" in chunk
        assert "tokens" in chunk
        
    # Test with nonexistent file
    with pytest.raises(FileNotFoundError):
        await process_file(Path("nonexistent.txt"))

@pytest.fixture(autouse=True)
def cleanup(temp_file):
    """Clean up temporary file after each test."""
    yield
    try:
        temp_file.unlink()
    except:
        pass  # Ignore errors during cleanup
