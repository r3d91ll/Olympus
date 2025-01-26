import pytest
from fastapi.testclient import TestClient
from typing import Generator

from src.main import app
from src.db.arango import ArangoDB
from src.memory_management.manager import MemoryManager

@pytest.fixture
def client() -> Generator:
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def db():
    db = ArangoDB()
    await db.connect()
    yield db
    # Cleanup after tests
    if db.db and db.db.has_collection("data"):
        db.db.delete_collection("data")

@pytest.fixture
async def memory_manager(db):
    return MemoryManager(db)
