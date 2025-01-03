import os
import json
import aiohttp
from .memory_realms import ElysiumRealm, AsphodelRealm, TartarusRealm
from .context_controllers import StyxController, LetheManager
from src.shared.models import ContextBlock, LMStudioModel

class ChatService:
    def __init__(self, n_keep: int, prompt_dir: str, lmstudio_model: LMStudioModel):
        self.n_keep = n_keep
        self.prompt_dir = prompt_dir
        self.conversation_history_file = os.path.join(prompt_dir, "conversation_history.json")
        
        if not os.path.exists(self.conversation_history_file):
            with open(self.conversation_history_file, 'w') as f:
                json.dump([], f)
        
        with open(self.conversation_history_file, 'r') as f:
            self.conversation_history = json.load(f)

        # Initialize memory realms
        self.elysium = ElysiumRealm(n_keep_limit=n_keep)
        self.asphodel = AsphodelRealm(window_size=100)  # Example window size
        self.tartarus = TartarusRealm()

        # Initialize controllers
        self.styx_controller = StyxController(elysium=self.elysium, asphodel=self.asphodel, tartarus=self.tartarus)
        self.lethe_manager = LetheManager(elysium=self.elysium, asphodel=self.asphodel, tartarus=self.tartarus)

        # Initialize LMStudio model
        self.lmstudio_model = lmstudio_model

    def add_message(self, message: str):
        if len(self.conversation_history) >= self.n_keep:
            self.conversation_history.pop(0)
        self.conversation_history.append(message)
        with open(self.conversation_history_file, 'w') as f:
            json.dump(self.conversation_history, f)

    def get_conversation_history(self):
        return self.conversation_history

    async def handle_chat_request(self, request: str):
        # Add the user's message to the conversation history
        user_message = ContextBlock(content=f"User: {request}", metadata={})
        self.add_message(user_message.content)

        # Send request to LMStudio REST API
        model_response = await self.send_to_lmstudio(request)

        # Manage context flow using StyxController
        response_block = ContextBlock(content=model_response, metadata={})
        await self.styx_controller.manage_flow(response_block)
        
        # Add the model's response to the conversation history
        self.add_message(model_response)

        return {"response": model_response}

    async def send_to_lmstudio(self, request: str):
        lmstudio_url = self.lmstudio_model.api_url
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": self.lmstudio_model.model_id,
            "messages": [
                {"role": "user", "content": request}
            ],
            "temperature": self.lmstudio_model.temperature,
            "max_tokens": self.lmstudio_model.max_tokens,
            "stream": self.lmstudio_model.stream
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(lmstudio_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f"Failed to get response from LMStudio: {response.status}")

    async def forget_irrelevant_context(self, context_id: str):
        """Forget irrelevant context using LetheManager."""
        await self.lethe_manager.forget(context_id)
