from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ContextBlock(BaseModel):
    content: str
    metadata: dict

class VectorStore:
    def __init__(self):
        self.store = {}

    async def store(self, vector, metadata) -> str:
        # Placeholder for storing vector and metadata
        context_id = len(self.store)
        self.store[context_id] = {"vector": vector, "metadata": metadata}
        return str(context_id)

class NetworkGraph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, node1, node2, weight=1.0):
        # Placeholder for adding an edge to the graph
        if node1 not in self.graph:
            self.graph[node1] = {}
        self.graph[node1][node2] = weight

    def get_neighbors(self, node):
        # Placeholder for getting neighbors of a node
        return self.graph.get(node, {})

class ModelRequest(BaseModel):
    model_name: str
    parameters: dict

class LMStudioModel(BaseModel):
    model_id: str
    api_url: str = "http://localhost:1234/api/v0/chat/completions"
    temperature: float = 0.7
    max_tokens: int = -1
    stream: bool = False
