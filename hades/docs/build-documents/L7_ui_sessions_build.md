# Layer 7: UI and Session Management

## Overview

Layer 7 provides the user interface and session management for HADES, implementing:

1. Real-time Interactive UI
2. Session State Management
3. Authentication and Authorization
4. WebSocket-based Updates
5. Visualization Components

### Architecture Components

1. **Session Manager**

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

@dataclass
class Session:
    id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    context: Dict[str, Any]
    trust_level: float

class SessionManager:
    async def create_session(self, user_id: str) -> Session:
        """Create new user session with context."""
        session = Session(
            id=generate_session_id(),
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            context={},
            trust_level=1.0
        )
        await redis.set(f"session:{session.id}", session.to_json())
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve active session."""
        if session_data := await redis.get(f"session:{session_id}"):
            return Session.from_json(session_data)
        return None

    async def update_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Update session context with new data."""
        if session := await self.get_session(session_id):
            session.context.update(context)
            session.last_active = datetime.now()
            await redis.set(f"session:{session.id}", session.to_json())
```

2. **WebSocket Handler**

```python
from fastapi import WebSocket
from typing import Set

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Establish WebSocket connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    async def broadcast_update(self, session_id: str, message: dict):
        """Broadcast updates to all session connections."""
        if connections := self.active_connections.get(session_id):
            for connection in connections:
                await connection.send_json(message)

    async def handle_message(self, websocket: WebSocket, session_id: str):
        """Handle incoming WebSocket messages."""
        try:
            while True:
                data = await websocket.receive_json()
                # Process real-time updates
                response = await process_realtime_update(data)
                await self.broadcast_update(session_id, response)
        except Exception as e:
            await self.disconnect(websocket, session_id)
```

3. **UI Components**

```typescript
// React-based UI components
interface KnowledgeGraphProps {
    data: GraphData;
    layout: LayoutOptions;
    interactions: InteractionConfig;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({ data, layout, interactions }) => {
    const graphRef = useRef<HTMLDivElement>(null);
    const [graph, setGraph] = useState<Graph | null>(null);

    useEffect(() => {
        if (graphRef.current) {
            const g = new Graph({
                container: graphRef.current,
                layout: {
                    type: layout.type,
                    options: layout.options
                },
                interactions: {
                    zoom: interactions.allowZoom,
                    drag: interactions.allowDrag,
                    select: interactions.allowSelect
                }
            });

            g.data(data);
            g.render();
            setGraph(g);
        }
    }, [data, layout]);

    return <div ref={graphRef} style={{ height: '100%', width: '100%' }} />;
};

// Real-time updates handler
const useWebSocketUpdates = (sessionId: string) => {
    const [updates, setUpdates] = useState<Update[]>([]);
    const ws = useWebSocket(`ws://api/ws/${sessionId}`);

    useEffect(() => {
        ws.onmessage = (event) => {
            const update = JSON.parse(event.data);
            setUpdates(prev => [...prev, update]);
        };
    }, [sessionId]);

    return updates;
};
```

4. **Authentication Handler**

```python
from fastapi_security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

class AuthHandler:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.secret_key = get_secret_key()

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        if user := await get_user(username):
            if self.pwd_context.verify(password, user.hashed_password):
                return user
        return None

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")

    async def get_current_user(self, token: str) -> User:
        """Validate token and return current user."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        if user := await get_user(username):
            return user
        raise credentials_exception
```

### Integration Points

1. **With Layer 6 (Query)**

```python
class UIQueryHandler:
    async def handle_query(self, query: str, session: Session) -> dict:
        """Handle UI queries with session context."""
        
        # Enrich query with session context
        enriched_query = enrich_with_context(query, session.context)
        
        # Route to Layer 6
        result = await layer6.process_query(enriched_query)
        
        # Update session context with new information
        await session_manager.update_context(session.id, extract_context(result))
        
        return result
```

2. **With Layer 5 (Orchestration)**

```python
class UIOrchestrationHandler:
    async def handle_orchestration(self, action: str, session: Session) -> dict:
        """Handle UI orchestration requests."""
        
        # Get orchestration context
        context = await layer5.get_orchestration_context(session)
        
        # Execute orchestration
        result = await layer5.execute_orchestration(action, context)
        
        # Broadcast updates to connected clients
        await websocket_manager.broadcast_update(session.id, result)
        
        return result
```

## Configuration

```yaml
ui_layer:
  session:
    timeout: 3600  # 1 hour
    max_sessions_per_user: 5
    cleanup_interval: 300  # 5 minutes

  websocket:
    ping_interval: 30
    max_connections_per_session: 3
    message_queue_size: 100

  auth:
    token_expiry: 900  # 15 minutes
    refresh_token_expiry: 604800  # 7 days
    password_min_length: 12

  ui:
    theme: "dark"
    default_layout: "force"
    max_graph_nodes: 1000
    update_interval: 1000  # 1 second
```

## Usage Examples

1. **Session Management**

```python
# Create and manage session
session = await session_manager.create_session(user_id)
await session_manager.update_context(session.id, {"current_view": "knowledge_graph"})
```

2. **Real-time Updates**

```typescript
// Subscribe to updates
const Updates: React.FC = () => {
    const updates = useWebSocketUpdates(sessionId);
    
    return (
        <div>
            {updates.map(update => (
                <UpdateNotification key={update.id} data={update} />
            ))}
        </div>
    );
};
```

3. **Authentication Flow**

```python
# Login flow
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_handler.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth_handler.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```
