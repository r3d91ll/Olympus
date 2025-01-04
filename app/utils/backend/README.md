# Backend Utilities

This directory contains utility scripts that provide backend-specific functionality for the Olympus project. Each script encapsulates reusable logic and follows the single responsibility principle to ensure modularity and maintainability.

## Utility Files

1. **memory.py**
   - **Purpose**: Manages temporary storage using tmpfs.
   - **Usage**:
     ```python
     from app.utils.backend.memory import MemoryManager

     # Initialize memory manager with a base directory (default is "ramdisk")
     memory_manager = MemoryManager(base_dir="ramdisk")

     # Store data in temporary storage
     success = memory_manager.store(key="user1_prompt1", data={"prompt": "Hello, world!"}, namespace="session_123")

     # Retrieve data from temporary storage
     data = memory_manager.retrieve(key="user1_prompt1", namespace="session_123")

     # Clear all data in a specific namespace
     cleared_namespace = memory_manager.clear_namespace(namespace="session_123")

     # Clear all data in all namespaces
     cleared_all = memory_manager.clear_all()
     ```

2. **inference.py**
   - **Purpose**: Handles inference logic for generating and refining responses.
   - **Usage**:
     ```python
     from app.utils.backend.inference import InferenceManager, Message, ModelConfig

     # Initialize the inference manager with a model client (optional)
     inference_manager = InferenceManager()

     # Define model configuration
     config = ModelConfig(name="gpt-3", max_tokens=100)

     # Initialize the inference manager with the configuration
     success = await inference_manager.initialize(config=config)

     # Generate a response from the model
     messages = [Message(role="user", content="What is the weather today?")]
     response = await inference_manager.generate_response(messages=messages, config=config)

     # Get current model status and information
     status_info = await inference_manager.get_model_status()
     ```
3. **verifier.py**
   - **Purpose**: Provides verification and validation utilities.
   - **Usage**:
     ```python
     from app.utils.backend.verifier import Verifier, Message, ModelConfig

     # Validate a message object
     message = Message(role="user", content="Hello, world!")
     message_validation_result = Verifier.validate_message(message)

     # Validate a model configuration
     config = ModelConfig(name="gpt-3", temperature=0.7, max_tokens=150)
     config_validation_result = Verifier.validate_model_config(config)

     # Sanitize a string
     sanitized_string = Verifier.sanitize_string("<script>alert('xss')</script>")

     # Validate a file system path
     path_validation_result = Verifier.validate_path("/home/user/data.txt")
     ```
4. **model_utils.py**
   - **Purpose**: Interfaces with local models.
   - **Usage**:
     ```python
     from app.utils.backend.model_utils import ModelClient, LMStudioClient

     # Initialize the model client for a specific model and API URL
     async with ModelClient(model_name="gpt-3", api_url="http://localhost:1234/v1/completions") as client:
         prompt = "What is the weather today?"
         config = {"max_tokens": 100}
         response = await client.generate(prompt=prompt, config=config)

     # Initialize the LM Studio client with default API URL
     async with LMStudioClient(model_name="gpt-3") as client:
         prompt = "Tell me a joke."
         response = await client.generate(prompt=prompt)
     ```
## Directory Structure

```text
app/
└── utils/
    └── backend/
        ├── memory.py            # Memory management utilities
        ├── inference.py         # Inference logic utilities
        ├── verifier.py          # Verification and validation utilities
        ├── model_utils.py       # Model interaction utilities
        └── logger.py            # Logging utility
```

## Key Principles

- **Utility-Driven Modularity**: Encapsulate reusable logic in utility files.
- **Stateless First**: Design the application to be stateless initially, using tmpfs for all temporary data storage.
- **Documentation**: Maintain comprehensive documentation for all components.
- **Testing Standards**: Implement unit tests for all utility functions.

## Future Extensions

1. **Enhanced State Management**
   - Implement persistent storage solutions.
   - Add user session tracking and management.

2. **Advanced Features**
   - Develop sophisticated feedback mechanisms.
   - Implement advanced context management.

3. **Performance Optimization**
   - Optimize memory usage and response times.
   - Implement caching strategies.

4. **Security Enhancements**
   - Add authentication and authorization.
   - Implement secure data handling.
