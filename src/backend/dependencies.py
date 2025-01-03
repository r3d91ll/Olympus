from src.backend.core.services.chat_service import ChatService
from src.backend.config.settings import get_settings

settings = get_settings()
chat_service_instance = ChatService(
    n_keep=settings.n_keep,
    prompt_dir=settings.prompt_dir,
    lmstudio_model=settings.lmstudio_model
)

def get_chat_service():
    return chat_service_instance
