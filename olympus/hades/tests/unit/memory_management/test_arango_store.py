import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Generator, Any, Dict, List
from olympus.hades.src.memory_management.arangodb_store import (
    ArangoMemoryStore,
    VectorNode,
    MemoryEdge
)

@pytest.fixture
def mock_arango_client() -> Generator[Mock, None, None]:
    """Create mock ArangoDB client."""
    with patch("olympus.hades.src.memory_management.arangodb_store.ArangoClient") as mock_client:
        # Mock database
        mock_db = Mock()
        mock_db.has_collection.return_value = False
        mock_db.create_collection.return_value = Mock()
        
        # Mock collection
        mock_collection = Mock()
        mock_collection.add_persistent_index.return_value = None
        mock_collection.add_hash_index.return_value = None
        mock_db.collection.return_value = mock_collection
        
        # Set up client
        mock_client.return_value.db.return_value = mock_db
        yield mock_client

@pytest.fixture
def test_store(mock_arango_client, mock_monitor) -> ArangoMemoryStore:
    """Create test ArangoMemoryStore instance."""
    store = ArangoMemoryStore(
        host="http://localhost:8529",
        db_name="test_db",
        username="test",
        password="test",
        phoenix_monitor=mock_monitor
    )
    return store

@pytest.fixture
def sample_vector_node() -> Dict[str, Any]:
    """Create sample vector node data."""
    return {
        "content": "Test content",
        "vector": [0.1, 0.2, 0.3],
        "timestamp": datetime.now(),
        "importance_score": 0.8,
        "metadata": {
            "source": "test",
            "type": "document"
        }
    }

@pytest.fixture
def sample_memory_edge() -> Dict[str, Any]:
    """Create sample memory edge data."""
    return {
        "from_node": "node1",
        "to_node": "node2",
        "relation_type": "similar_to",
        "weight": 0.9,
        "context_window": 5
    }

@pytest.mark.asyncio
async def test_store_initialization(test_store, mock_arango_client):
    """Test store initialization and collection creation."""
    # Check if collections were created
    mock_db = mock_arango_client.return_value.db.return_value
    assert mock_db.create_collection.call_count == 2  # nodes and edges
    
    # Check if indexes were created
    mock_collection = mock_db.collection.return_value
    assert mock_collection.add_persistent_index.call_count >= 1
    assert mock_collection.add_hash_index.call_count >= 1

@pytest.mark.asyncio
async def test_store_vector_node(test_store, sample_vector_node):
    """Test storing vector nodes."""
    # Mock collection insert
    mock_collection = test_store.db.collection.return_value
    mock_collection.insert.return_value = {"_id": "nodes/123"}
    
    # Store node
    node_id = await test_store.store_memory(
        content=sample_vector_node["content"],
        vector=sample_vector_node["vector"],
        metadata=sample_vector_node["metadata"]
    )
    
    assert node_id == "nodes/123"
    assert mock_collection.insert.call_count == 1

@pytest.mark.asyncio
async def test_create_memory_edge(test_store, sample_memory_edge):
    """Test creating memory edges."""
    # Mock collection insert
    mock_collection = test_store.db.collection.return_value
    mock_collection.insert.return_value = {"_id": "edges/123"}
    
    # Create edge
    edge_id = await test_store.create_edge(
        from_node=sample_memory_edge["from_node"],
        to_node=sample_memory_edge["to_node"],
        relation_type=sample_memory_edge["relation_type"],
        weight=sample_memory_edge["weight"]
    )
    
    assert edge_id == "edges/123"
    assert mock_collection.insert.call_count == 1

@pytest.mark.asyncio
async def test_find_similar_memories(test_store):
    """Test finding similar memories."""
    # Mock AQL query execution
    mock_cursor = Mock()
    mock_cursor.batch.return_value = [{
        "_id": "nodes/123",
        "content": "Similar content",
        "vector": [0.1, 0.2, 0.3],
        "similarity": 0.95,
        "metadata": {"source": "test"}
    }]
    test_store.db.aql.execute.return_value = mock_cursor
    
    # Search for similar memories
    query_vector = [0.1, 0.2, 0.3]
    results = await test_store.find_similar_memories(
        query_vector=query_vector,
        limit=5,
        min_similarity=0.7
    )
    
    assert len(results) == 1
    assert results[0]["similarity"] == 0.95
    assert test_store.db.aql.execute.call_count == 1

@pytest.mark.asyncio
async def test_get_memory_by_id(test_store):
    """Test retrieving memory by ID."""
    # Mock document retrieval
    mock_collection = test_store.db.collection.return_value
    mock_collection.get.return_value = {
        "_id": "nodes/123",
        "content": "Test content",
        "vector": [0.1, 0.2, 0.3],
        "metadata": {"source": "test"}
    }
    
    # Get memory
    memory = await test_store.get_memory("nodes/123")
    
    assert memory["_id"] == "nodes/123"
    assert mock_collection.get.call_count == 1

@pytest.mark.asyncio
async def test_update_memory(test_store):
    """Test updating memory nodes."""
    # Mock document update
    mock_collection = test_store.db.collection.return_value
    mock_collection.update.return_value = {"_id": "nodes/123"}
    
    # Update memory
    success = await test_store.update_memory(
        memory_id="nodes/123",
        importance_score=0.9,
        metadata={"updated": True}
    )
    
    assert success
    assert mock_collection.update.call_count == 1

@pytest.mark.asyncio
async def test_delete_memory(test_store):
    """Test deleting memory nodes."""
    # Mock document removal
    mock_collection = test_store.db.collection.return_value
    mock_collection.delete.return_value = True
    
    # Delete memory
    success = await test_store.delete_memory("nodes/123")
    
    assert success
    assert mock_collection.delete.call_count == 1

@pytest.mark.asyncio
async def test_error_handling(test_store):
    """Test error handling in store operations."""
    # Test store_memory error
    mock_collection = test_store.db.collection.return_value
    mock_collection.insert.side_effect = Exception("Database error")
    
    with pytest.raises(Exception):
        await test_store.store_memory(
            content="Test content",
            vector=[0.1, 0.2, 0.3],
            metadata={}
        )
    
    # Test find_similar_memories error
    test_store.db.aql.execute.side_effect = Exception("Query error")
    
    with pytest.raises(Exception):
        await test_store.find_similar_memories(
            query_vector=[0.1, 0.2, 0.3],
            limit=5
        )
