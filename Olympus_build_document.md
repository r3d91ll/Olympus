### Build Document: Simple Chat Interface with Reflex

#### Objective

To build a modular, extensible chat interface for local models using Reflex, Pydantic v2, and tmpfs (in-memory storage) for memory/continual learning. This phase focuses on creating a functional baseline, emphasizing reusability and simplicity. Future features will build upon this foundation.

---

### 1. Core Architecture

**Overall System Design:**

```
.
├── app/                      # Reflex application folder
│   ├── app.py               # Main Reflex app
│   ├── utils/               # Utility scripts for modularity
│   │   ├── memory.py       # Memory management utilities
│   │   ├── inference.py    # Inference logic utilities
│   │   ├── verifier.py     # Verification and validation utilities
│   │   └── logger.py       # Logging utility
│   └── components/          # Reflex UI components
└── public/                  # Static assets (if any)
```

**Key Technologies:**

- **Framework**: Reflex for integrated front-end and back-end development.
- **Configuration Management**: Pydantic v2 for structured configuration handling.
- **Memory Storage**: tmpfs-based file storage for temporary session management.
- **Logging**: Python's built-in logging with centralized configuration.

---

### 2. Stateless Design with Future-Proofing

#### **Stateless Application**

- The application will initially be stateless, handling requests independently without persisting states beyond tmpfs storage.
- Benefits:
  - Simplicity in development and deployment.
  - Reduced resource overhead for a small user base.

#### **Stateful Future Expansion**

- Future updates can introduce stateful components, such as:
  - User-specific session tracking.
  - Persistent memory for advanced workflows.
- Modular design ensures easy integration of statefulness when required.

---

### 3. Memory Management

#### **tmpfs for Temporary Storage**

- Use a tmpfs directory to store:
  - Input prompts.
  - Model-generated responses.
  - Context snapshots for ongoing sessions.
- Example directory structure:

  ```
  /mnt/ai_tmpfs/
  ├── session_{user_id}/
  │   ├── prompts/
  │   └── responses/
  ```

#### **Utility File: memory.py**

- Functions:

  ```python
  import os
  from uuid import uuid4

  TMPFS_BASE = "/mnt/ai_tmpfs"

  def get_session_path(user_id: str) -> str:
      path = f"{TMPFS_BASE}/session_{user_id}"
      os.makedirs(path, exist_ok=True)
      return path

  def store_prompt(user_id: str, prompt_id: str, content: str):
      session_path = get_session_path(user_id)
      file_path = os.path.join(session_path, f"{prompt_id}.txt")
      with open(file_path, "w") as f:
          f.write(content)

  def retrieve_prompt(user_id: str, prompt_id: str) -> str:
      session_path = get_session_path(user_id)
      file_path = os.path.join(session_path, f"{prompt_id}.txt")
      with open(file_path, "r") as f:
          return f.read()

  def clear_session(user_id: str):
      session_path = get_session_path(user_id)
      if os.path.exists(session_path):
          for file in os.listdir(session_path):
              os.remove(os.path.join(session_path, file))
  ```

---

### 4. Inference Logic

#### **Utility File: inference.py**

- Functions:

  ```python
  def generate_response(prompt: str) -> str:
      # Placeholder for LLM interaction
      return f"Processed: {prompt}"

  def refine_response(draft: str, feedback: str) -> str:
      # Placeholder for refinement logic
      return f"Refined: {draft} with feedback: {feedback}"
  ```

#### **LLM Integration**

- Start with direct integration of LMStudio or other lightweight local models.
- Future-proofing:
  - Modularize inference logic to allow switching between models or adding ensemble methods.

---

### 5. Verification and Validation

#### **Utility File: verifier.py**

- Functions:

  ```python
  def basic_validation(response: str) -> bool:
      # Basic checks for response
      return bool(response and len(response) > 0)

  def feedback_loop(response: str, feedback: str) -> str:
      # Incorporate feedback into the response
      return f"Validated response: {response}, Feedback: {feedback}"
  ```

---

### 6. Logging Utility

#### **Utility File: logger.py**

- Functions:

  ```python
  import logging
  from logging.handlers import RotatingFileHandler

  def get_logger(name: str) -> logging.Logger:
      logger = logging.getLogger(name)
      if not logger.hasHandlers():  # Prevent duplicate handlers
          logger.setLevel(logging.DEBUG)

          # Console handler
          console_handler = logging.StreamHandler()
          console_handler.setLevel(logging.INFO)
          console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
          console_handler.setFormatter(console_formatter)
          logger.addHandler(console_handler)

          # File handler
          file_handler = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3)
          file_handler.setLevel(logging.DEBUG)
          file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
          file_handler.setFormatter(file_formatter)
          logger.addHandler(file_handler)

      return logger
  ```

#### **Usage Example**

- Import and use the logger in utility files:

  ```python
  from logger import get_logger

  logger = get_logger(__name__)

  def example_function():
      logger.info("Example function executed")
      try:
          # Your logic here
          logger.debug("Debugging information")
      except Exception as e:
          logger.error(f"An error occurred: {e}")
  ```

---

### 7. Reflex Integration

#### **Frontend Components**

- Chat interface:
  - Input box for user queries.
  - Display area for model responses.
  - Optional feedback mechanism for iterative refinement.

#### **Backend Handlers**

- Connect utility functions from `memory.py`, `inference.py`, `verifier.py`, and `logger.py` to Reflex backend handlers.
- Example endpoints:
  - `/submit_query`: Handle user input, store prompts, generate responses.
  - `/get_response`: Retrieve responses from tmpfs.
  - `/validate_response`: Validate and refine responses based on feedback.

---

### 8. Fundamental Rules for Consistency

1. **Single Language Stack**:
   - Use Python exclusively for front-end and back-end development to simplify maintenance.

2. **Utility-Driven Modularity**:
   - Encapsulate reusable logic in utility files (`memory.py`, `inference.py`, `verifier.py`, `logger.py`).

3. **Stateless First**:
   - Design the application to be stateless initially. Introduce statefulness only when necessary.

4. **Iterative Development**:
   - Build incrementally: Focus on a simple chat interface first, then add features like refinement and verification.

5. **Future-Ready Design**:
   - Modularize components to allow for easy updates or integration of stateful features and advanced workflows.

6. **Documentation**:
   - Keep utility files and application logic well-documented for clarity and maintainability.

---

### 9. Implementation Steps

1. **Reflex Setup:**
   - Install Reflex and initialize the application structure.
   - Define placeholders for utility files and components.

2. **Frontend and Backend Integration:**
   - Build the chat interface in Reflex.
   - Link UI components to backend endpoints for query submission and response retrieval.

3. **Utility Development:**
   - Implement memory management, inference logic, verification utilities, and logging.

4. **Testing and Debugging:**
   - Test each utility independently.
   - Debug interactions between frontend and backend.

5. **Iterate and Expand:**
   - Add advanced features like iterative refinement and user feedback collection.

---

### 10. Future Extensions

1. **Stateful Components**: Add user-specific session tracking.
2. **Advanced Memory Management**: Expand tmpfs logic for persistent storage.
3. **Enhanced Verification**: Develop trainable reward models for output validation.
4. **Dynamic Model Selection**: Enable switching between different local models.

---

### 11. Conclusion

This simplified build document focuses on creating a modular, extensible chat interface using Reflex and Python utilities. By leveraging tmpfs for session isolation and adhering to the stateless-first approach, the system remains flexible, efficient, and ready for future enhancements.
