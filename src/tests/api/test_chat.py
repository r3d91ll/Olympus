import unittest
from src.backend.core.services.chat_service import ChatService

class TestChatService(unittest.TestCase):
    def setUp(self):
        self.prompt_dir = "ramdisk/prompts"
        self.chat_service = ChatService(n_keep=5, prompt_dir=self.prompt_dir)

    def test_add_message(self):
        self.chat_service.add_message("Test message")
        history = self.chat_service.get_conversation_history()
        self.assertEqual(history[-1], "Test message")

    def test_handle_chat_request(self):
        response = self.chat_service.handle_chat_request("Hello, model!")
        history = self.chat_service.get_conversation_history()
        self.assertIn("User: Hello, model!", history)
        self.assertIn("Model: This is a placeholder response", history)

    def test_n_keep_limit(self):
        for i in range(6):
            self.chat_service.add_message(f"Message {i}")
        history = self.chat_service.get_conversation_history()
        self.assertEqual(len(history), 5)
        self.assertNotIn("Message 0", history)

if __name__ == "__main__":
    unittest.main()
