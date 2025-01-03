from fastapi import APIRouter, HTTPException, Depends
from src.shared.models import ChatRequest
from src.backend.core.services.chat_service import ChatService
from src.backend.dependencies import get_chat_service

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    try:
        response = await chat_service.handle_chat_request(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
