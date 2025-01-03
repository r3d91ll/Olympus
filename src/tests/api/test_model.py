import unittest
from fastapi.testclient import TestClient
from src.backend.main import app

class TestModelAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_load_model(self):
        response = self.client.post("/api/load", json={"model_name": "test_model"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Loading model test_model", response.json()["message"])

    def test_unload_model(self):
        response = self.client.post("/api/unload", json={"model_name": "test_model"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Unloading model test_model", response.json()["message"])

    def test_configure_model(self):
        request_data = {"model_name": "test_model", "config": {"param1": "value1", "param2": "value2"}}
        response = self.client.post("/api/configure", json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Configuring model test_model with {'param1': 'value1', 'param2': 'value2'}", response.json()["message"])

if __name__ == "__main__":
    unittest.main()
