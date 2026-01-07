---
name: chatbot-architecture
description: Design stateless, database-persisted chatbot architectures for full-stack applications. Use when architecting conversational AI systems, designing conversation state management, planning database schemas for chat history, or implementing stateless backend architectures with PostgreSQL persistence.
---

# Chatbot Architecture

## Overview

Design and implement stateless chatbot architectures with database-persisted conversation state for scalable, production-ready conversational AI applications.

## Architecture Principles

### 1. Stateless Server Design

**Core Principle**: Server holds no in-memory conversation state

```
Benefits:
- Horizontal scaling: Any server instance can handle any request
- Crash resilience: No data loss on server restart
- Load balancing: Simple round-robin distribution
- Cost efficiency: No sticky sessions required
```

**Implementation**:
```python
# ❌ BAD: Stateful (in-memory)
conversation_cache = {}  # Lost on restart

@app.post("/chat")
async def chat(message: str, user_id: int):
    if user_id not in conversation_cache:
        conversation_cache[user_id] = []
    conversation_cache[user_id].append(message)

# ✅ GOOD: Stateless (database-persisted)
@app.post("/chat")
async def chat(request: ChatRequest):
    # Load state from database
    history = await load_conversation_history(request.conversation_id)

    # Process message
    response = await agent.process(request.message, history)

    # Persist state to database
    await save_message(request.conversation_id, request.message, response)

    return response
```

### 2. Database Schema Design

**Core Tables**:

```sql
-- Users table (from Phase II)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),  -- Auto-generated from first message
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'  -- Store context, settings, etc.
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system', 'tool'
    content TEXT,
    tool_calls JSONB,  -- Store tool execution details
    created_at TIMESTAMP DEFAULT NOW(),

    CHECK (role IN ('user', 'assistant', 'system', 'tool'))
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**SQLModel Models**:

```python
# backend/src/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    title: Optional[str] = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, sa_column_kwargs={"type_": JSON})

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", ondelete="CASCADE")
    role: str = Field(max_length=20)  # 'user', 'assistant', 'system', 'tool'
    content: Optional[str] = Field(default=None)
    tool_calls: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": JSON})
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

### 3. Request Flow Architecture

```
┌─────────────┐
│   Frontend  │  (Next.js + ChatKit)
└──────┬──────┘
       │ POST /api/chat
       │ {message, conversation_id, token}
       ▼
┌─────────────────────────────────────────┐
│         API Gateway / Load Balancer      │
└──────┬──────────────────────┬────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│  Server A    │      │  Server B    │  (Any server can handle request)
└──────┬───────┘      └──────┬───────┘
       │                     │
       │  1. Validate JWT    │
       │  2. Load conversation from DB
       │  3. Call OpenAI Agent with history
       │  4. Execute MCP tools
       │  5. Save messages to DB
       │  6. Return response
       │                     │
       ▼                     ▼
┌─────────────────────────────────────────┐
│         PostgreSQL Database              │
│  - conversations                         │
│  - messages                              │
│  - users                                 │
│  - tasks                                 │
└──────────────────────────────────────────┘
```

### 4. Conversation State Management

**Create New Conversation**:

```python
# backend/src/routes/chat.py
async def create_conversation(user_id: int, first_message: str):
    """Create new conversation with auto-generated title"""

    # Generate title from first message (first 50 chars)
    title = first_message[:50] + ("..." if len(first_message) > 50 else "")

    async with AsyncSession(async_engine) as session:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        return conversation
```

**Load Conversation History**:

```python
async def load_conversation_history(
    conversation_id: int,
    limit: int = 20
) -> List[dict]:
    """Load recent messages for context window"""

    async with AsyncSession(async_engine) as session:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        results = await session.execute(statement)
        messages = list(reversed(results.scalars().all()))

        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {})
            }
            for msg in messages
        ]
```

**Save Conversation Turn**:

```python
async def save_conversation_turn(
    conversation_id: int,
    user_message: str,
    assistant_message: str,
    tool_calls: Optional[List] = None
):
    """Atomically save user + assistant messages"""

    async with AsyncSession(async_engine) as session:
        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        session.add(user_msg)

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            tool_calls=tool_calls
        )
        session.add(assistant_msg)

        # Update conversation timestamp
        conversation = await session.get(Conversation, conversation_id)
        conversation.updated_at = datetime.utcnow()

        await session.commit()
```

### 5. Authentication Flow

**JWT Token Propagation**:

```typescript
// Frontend: app/chat/page.tsx
const { token } = useAuth();

<ChatKit
  apiUrl="/api/chat"
  authToken={token}  // Automatically adds Authorization header
/>
```

```python
# Backend: src/routes/chat.py
from fastapi import Depends, HTTPException
from .auth import get_current_user

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)  # Validates JWT
):
    # User authenticated - process request
    # current_user.id available for database queries
    ...
```

**User Isolation**:

```python
# Always scope queries to current user
async def get_user_conversations(user_id: int):
    """Get conversations for specific user only"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    ...

async def verify_conversation_ownership(
    conversation_id: int,
    user_id: int
) -> bool:
    """Ensure user owns conversation before access"""
    conversation = await session.get(Conversation, conversation_id)
    return conversation and conversation.user_id == user_id
```

### 6. Performance Optimization

**Connection Pooling**:

```python
# backend/src/database.py
async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Max connections in pool
    max_overflow=0,         # No additional connections
    pool_pre_ping=True,     # Verify connection before use
    pool_recycle=3600       # Recycle connections every hour
)
```

**Query Optimization**:

```python
# Limit conversation history to prevent large queries
MAX_HISTORY_MESSAGES = 20

# Use indexes for fast lookups
# Already created in schema above:
# - idx_conversations_user_id
# - idx_messages_conversation_id
# - idx_messages_created_at
```

**Caching Strategy** (Optional):

```python
# Cache conversation metadata (but not messages)
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_conversation_metadata(conversation_id: int):
    """Cache conversation title/user_id"""
    # Only cache immutable data
    ...
```

### 7. Error Handling Patterns

**Database Transaction Failures**:

```python
async def safe_save_conversation_turn(...):
    """Save with transaction rollback on error"""
    async with AsyncSession(async_engine) as session:
        try:
            # Save operations
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(400, "Invalid conversation ID")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise HTTPException(500, "Failed to save conversation")
```

**Conversation Not Found**:

```python
@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    conversation = await session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    return conversation
```

## Best Practices

1. **Stateless Design**: Never store conversation state in memory
2. **Database Persistence**: All state in PostgreSQL with proper indexes
3. **User Isolation**: Always filter queries by user_id
4. **Transaction Safety**: Use database transactions for atomic operations
5. **Connection Pooling**: Configure appropriate pool sizes
6. **History Limits**: Limit loaded messages to prevent large queries
7. **Error Handling**: Handle database errors gracefully
8. **Monitoring**: Log conversation creation/access patterns
9. **Scalability**: Design for horizontal scaling from day one
10. **Testing**: Test concurrent access and race conditions

## Common Patterns

**New Conversation with First Message**:
```python
# Create conversation + save first turn atomically
conversation = await create_conversation(user_id, first_message)
await save_conversation_turn(
    conversation.id,
    first_message,
    agent_response
)
```

**Resume Existing Conversation**:
```python
# Verify ownership, load history, continue
if not await verify_conversation_ownership(conversation_id, user_id):
    raise HTTPException(403)

history = await load_conversation_history(conversation_id)
response = await agent.process(new_message, history)
await save_conversation_turn(conversation_id, new_message, response)
```

**List User Conversations**:
```python
# Show conversation list with preview
conversations = await get_user_conversations(user_id, limit=50)
return [
    {
        "id": conv.id,
        "title": conv.title,
        "updated_at": conv.updated_at,
        "message_count": await get_message_count(conv.id)
    }
    for conv in conversations
]
```

## Architecture Checklist

- [ ] Server stores no conversation state in memory
- [ ] All conversations persisted to PostgreSQL
- [ ] Messages table stores full conversation history
- [ ] Indexes created on user_id, conversation_id, created_at
- [ ] JWT authentication validates every request
- [ ] User isolation enforced in all queries
- [ ] Connection pooling configured
- [ ] Transaction safety for atomic operations
- [ ] Conversation history limited to last N messages
- [ ] Error handling for database failures
- [ ] Horizontal scaling supported (no sticky sessions)
