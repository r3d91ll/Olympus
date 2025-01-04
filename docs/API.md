# Olympus API Documentation

## State Management (`state.py`)

### Classes

#### Message
Represents a chat message in the system.
- **Properties**:
  - `role: str` - Role of the message sender
  - `content: str` - Content of the message

#### State
Main application state management.
- **Properties**:
  - `messages: List[Message]` - Chat message history
  - `current_message: str` - Current message being processed
  - `loaded_model: Optional[dict]` - Currently loaded model information
  - `processing: bool` - Message processing status
  - `temperature: List[float]` - Model temperature settings
  - `max_tokens: int` - Maximum tokens for model responses

- **Methods**:
  - `is_model_loaded() -> bool`: Check if a model is currently loaded
  - `model_name() -> str`: Get the name of the loaded model
  - `increment()`: Test event handler for counter

## Model Selection (`components/model_selection.py`)

Handles model loading and configuration for the AI system.

## Memory Management

### ElysiumRealm
Manages critical context preservation.
- **Methods**:
  - `preserve(context: str) -> bool`: Preserve critical context in n_keep region

### AsphodelRealm
Handles working memory operations.
- **Methods**:
  - `process(message: str) -> None`: Process new messages in working memory

## Web Interface

### API Endpoints
- `/` - Main application interface
- `/api/chat` - Chat interaction endpoint
- `/api/models` - Model management endpoint

### WebSocket Events
- `message` - Real-time message updates
- `model_status` - Model status updates
- `processing_status` - Message processing status updates
