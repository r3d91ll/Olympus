import pytest
from src.memory_management.memory_tier import ElysiumTier, AsphodelTier

@pytest.mark.asyncio
async def test_elysium_store_retrieve():
    tier = ElysiumTier(max_size=1024)
    key = "test_key"
    value = {"data": "test_value"}
    
    # Test storage
    success = await tier.store(key, value)
    assert success is True
    
    # Test retrieval
    result = await tier.retrieve(key)
    assert result == value

@pytest.mark.asyncio
async def test_asphodel_store_retrieve():
    tier = AsphodelTier(max_size=1024)
    key = "test_key"
    value = {"data": "test_value"}
    
    # Test storage
    success = await tier.store(key, value)
    assert success is True
    
    # Test retrieval
    result = await tier.retrieve(key)
    assert result == value

@pytest.mark.asyncio
async def test_memory_manager(memory_manager):
    key = "test_key"
    value = {"data": "test_value"}
    
    # Test storing in Elysium
    success = await memory_manager.store(key, value, "elysium")
    assert success is True
    
    # Test retrieval from Elysium
    result = await memory_manager.retrieve(key)
    assert result == value
    
    # Test eviction
    success = await memory_manager.evict(key)
    assert success is True
    
    # Verify data is evicted
    result = await memory_manager.retrieve(key)
    assert result is None
