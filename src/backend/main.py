from fastapi import FastAPI
from src.backend.api.chat import router as chat_router
from src.backend.api.model import router as model_router
from src.backend.dependencies import get_chat_service

app = FastAPI()

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(model_router, prefix="/api", tags=["model"])

@app.get("/")
def read_root():
    return {"message": "LLM Context Manager Backend is running"}
