from pydantic import BaseModel, Field
import os
from src.shared.models import LMStudioModel

class Settings(BaseModel):
    n_keep: int = Field(default=5, description="Number of messages to keep in the conversation history")
    prompt_dir: str = Field(default="ramdisk/prompts", description="Directory for storing conversation prompts")
    lmstudio_model: LMStudioModel = Field(
        default_factory=lambda: LMStudioModel(
            model_id="qwen2.5-coder-32b-instruct",
            api_url="http://localhost:1234/api/v0/chat/completions",
            temperature=0.7,
            max_tokens=-1,
            stream=False
        ),
        description="Configuration for the LMStudio model"
    )

def get_settings():
    return Settings(
        n_keep=int(os.getenv("N_KEEP", 5)),
        prompt_dir=os.getenv("PROMPT_DIR", "ramdisk/prompts"),
        lmstudio_model=LMStudioModel(
            model_id=os.getenv("LMS_STUDIO_MODEL_ID", "qwen2.5-coder-32b-instruct"),
            api_url=os.getenv("LMS_STUDIO_API_URL", "http://localhost:1234/api/v0/chat/completions"),
            temperature=float(os.getenv("LMS_STUDIO_TEMPERATURE", 0.7)),
            max_tokens=int(os.getenv("LMS_STUDIO_MAX_TOKENS", -1)),
            stream=bool(os.getenv("LMS_STUDIO_STREAM", False))
        )
    )
