from fastapi import APIRouter, HTTPException, Depends
from typing import Any, Dict
from pydantic import BaseModel

from memory_management.manager import MemoryManager
from db.arango import ArangoDB
from .rag_router import router as rag_router

router = APIRouter()

# Include RAG router
router.include_router(
    rag_router,
    prefix="/rag",
    tags=["rag"]
)

class StoreRequest(BaseModel):
    key: str
    value: Any
    tier: str = "elysium"

class Response(BaseModel):
    success: bool
    data: Dict[str, Any] = {}

async def get_memory_manager():
    db = ArangoDB()
    await db.connect()
    return MemoryManager(db)

@router.post("/store", response_model=Response)
async def store_data(
    request: StoreRequest,
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    success = await memory_manager.store(request.key, request.value, request.tier)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to store data")
    return Response(success=True)

@router.get("/retrieve/{key}", response_model=Response)
async def retrieve_data(
    key: str,
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    value = await memory_manager.retrieve(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return Response(success=True, data={"value": value})

@router.delete("/evict/{key}", response_model=Response)
async def evict_data(
    key: str,
    tier: str = None,
    memory_manager: MemoryManager = Depends(get_memory_manager)
):
    success = await memory_manager.evict(key, tier)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to evict data")
    return Response(success=True)
