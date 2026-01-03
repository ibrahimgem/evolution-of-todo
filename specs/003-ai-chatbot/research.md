# Research: AI-Powered Todo Chatbot

**Feature**: 003-ai-chatbot
**Date**: 2026-01-01
**Purpose**: Resolve technical unknowns and establish implementation patterns

## Research Questions and Findings

### R1: OpenAI ChatKit Integration Pattern

**Question**: How to integrate OpenAI ChatKit in Next.js with existing JWT authentication?

**Decision**: Use ChatKit as a client-side component with JWT token passed via `authToken` prop

**Rationale**:
- ChatKit natively supports custom authentication via `authToken` prop
- Seamless integration with existing Phase II JWT system
- Frontend handles token management, backend validates on API calls
- No modification to Phase II auth required

**Alternatives Considered**:
- Custom chat UI without ChatKit: Rejected - reinventing the wheel, longer development time
- OAuth integration: Rejected - would require modifying Phase II auth system

**Implementation Pattern**:
```typescript
<ChatKit
  apiUrl="/api/chat"
  authToken={jwtToken}  // From Phase II
  // ... other props
/>
```

---

### R2: MCP SDK Tool Registration Pattern

**Question**: How to implement and register MCP tools with OpenAI Agents SDK?

**Decision**: Use official MCP SDK with Pydantic schemas, register tools with OpenAI function calling format

**Rationale**:
- MCP SDK provides standardized tool interface
- Pydantic models ensure type safety and validation
- OpenAI function calling requires JSON schema - Pydantic generates this automatically
- Clear separation between tool definition and execution

**Alternatives Considered**:
- Custom tool interface: Rejected - lacks standardization, no schema validation
- Direct function calling without MCP: Rejected - less maintainable, no protocol benefits

**Implementation Pattern**:
```python
# Define tool with MCP
@Tool.register(
    name="add_task",
    description="Create a new task",
    input_schema=AddTaskInput  # Pydantic model
)
async def add_task(input: AddTaskInput, context: dict) -> dict:
    # Implementation
    pass

# Convert to OpenAI format
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema.model_json_schema()
        }
    }
    for tool in mcp_tools
]
```

---

### R3: Stateless Conversation Management

**Question**: How to implement stateless architecture with database-persisted conversation state?

**Decision**: Load conversation history from PostgreSQL on every request, use last 20 messages for AI context

**Rationale**:
- Enables horizontal scaling - any server can handle any request
- No sticky sessions or in-memory caches required
- PostgreSQL provides ACID guarantees for message persistence
- 20-message limit balances context quality with token costs

**Alternatives Considered**:
- Redis for conversation cache: Rejected - adds dependency, still requires persistence layer
- In-memory with periodic sync: Rejected - not truly stateless, data loss on crash
- Full conversation history in context: Rejected - token costs too high, performance degradation

**Implementation Pattern**:
```python
# Every request
history = await load_conversation_history(conversation_id, limit=20)
messages = [system_prompt] + history + [{"role": "user", "content": user_message}]
response = await agent.process(messages)
await save_messages(conversation_id, user_message, response)
```

---

### R4: Database Schema for Conversations

**Question**: How to structure conversations and messages tables for optimal querying and data integrity?

**Decision**: Two tables (conversations, messages) with proper foreign keys, indexes, and JSONB for tool_calls

**Rationale**:
- Conversations provide grouping and metadata (title, timestamps)
- Messages store individual turns with role, content, and tool_calls
- JSONB for tool_calls allows flexible structure without schema changes
- Indexes on user_id, conversation_id, created_at optimize common queries
- CASCADE delete ensures referential integrity

**Alternatives Considered**:
- Single messages table with embedded conversation data: Rejected - data duplication, harder to query conversations
- Separate tables for each tool type: Rejected - over-normalization, complex queries
- NoSQL document store: Rejected - need ACID guarantees for message ordering

**Schema**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

---

### R5: Message Streaming Implementation

**Question**: How to implement real-time streaming responses from OpenAI to frontend?

**Decision**: Use Server-Sent Events (SSE) with FastAPI StreamingResponse and OpenAI streaming API

**Rationale**:
- SSE is simpler than WebSockets for one-way server-to-client streaming
- OpenAI SDK natively supports streaming with `stream=True`
- FastAPI StreamingResponse handles SSE with async generators
- ChatKit supports SSE via `streaming={true}` prop

**Alternatives Considered**:
- WebSockets: Rejected - overkill for one-way streaming, more complex
- Long polling: Rejected - inefficient, delays in response
- Non-streaming: Rejected - poor UX for long responses

**Implementation Pattern**:
```python
# Backend
async def stream_response() -> AsyncGenerator[str, None]:
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

@router.post("/chat/stream")
async def chat_stream():
    return StreamingResponse(stream_response(), media_type="text/event-stream")
```

---

### R6: Tool Execution Flow

**Question**: How to handle tool calls from OpenAI agent and execute against database?

**Decision**: Two-phase approach - agent decides tools, then execute each with user context

**Rationale**:
- OpenAI returns tool_calls array with function name and arguments
- Each tool needs user_id from JWT for permission scoping
- Tools return structured responses that get appended to conversation
- Second agent call with tool results generates final natural language response

**Alternatives Considered**:
- Execute tools during agent call: Rejected - not possible with OpenAI API
- Skip tool result incorporation: Rejected - agent can't confirm actions to user
- Client-side tool execution: Rejected - security risk, no server validation

**Implementation Pattern**:
```python
# 1. First agent call
response = client.chat.completions.create(messages=messages, tools=openai_tools)

# 2. Execute tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = await execute_mcp_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
            context={"user_id": user_id}
        )
        messages.append({"role": "tool", "content": json.dumps(result)})

# 3. Second agent call for final response
final = client.chat.completions.create(messages=messages)
return final.choices[0].message.content
```

---

### R7: Authentication Token Flow

**Question**: How to pass JWT tokens from Phase II to Phase III without coupling codebases?

**Decision**: Environment variable for Phase II backend URL, HTTP Authorization header for token passing

**Rationale**:
- Phase III frontend calls Phase II `/api/auth/login` to get JWT token
- Token stored in localStorage and AuthContext (same as Phase II pattern)
- Phase III backend validates token using Phase II's JWT secret (shared via env var)
- No code dependencies between phases - only shared database and JWT secret

**Alternatives Considered**:
- Duplicate auth system in Phase III: Rejected - violates DRY, maintenance burden
- OAuth proxy: Rejected - unnecessary complexity
- Session-based auth: Rejected - doesn't work with stateless architecture

**Implementation Pattern**:
```typescript
// Frontend: Get token from Phase II
const response = await fetch(`${PHASE_II_API}/api/auth/login`, {...});
const { access_token } = await response.json();
localStorage.setItem('token', access_token);

// Frontend: Pass to Phase III
<ChatKit authToken={access_token} />

// Backend Phase III: Validate using shared secret
from jose import jwt
token_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

---

### R8: Parallel Agent Coordination

**Question**: How to coordinate chatbot-architect and chatbot-frontend-expert agents working in parallel?

**Decision**: Define API contract upfront, launch both agents with contract specification, minimal coordination checkpoints

**Rationale**:
- Clear API contract eliminates blocking dependencies
- Backend can implement contract from spec
- Frontend can implement against contract from spec
- Integration testing catches mismatches early
- 40%+ time savings from concurrent development

**Alternatives Considered**:
- Sequential development: Rejected - slower, no concurrency benefits
- Shared state coordination: Rejected - complex, defeats stateless architecture
- Continuous sync: Rejected - overhead negates parallel benefits

**Coordination Points**:
1. **Upfront**: Define API contract in spec (request/response schemas)
2. **25% checkpoint**: Verify both agents align on contract interpretation
3. **50% checkpoint**: Run integration tests between partial implementations
4. **75% checkpoint**: Final alignment before completion
5. **100%**: Integration testing and validation

---

## Technology Best Practices

### OpenAI Agents SDK
- Use GPT-4 for better tool calling accuracy
- Keep system prompts clear and example-driven
- Limit conversation history to 20 messages for cost control
- Implement retry logic with exponential backoff
- Monitor token usage per request

### MCP Tools
- Always return structured responses with `success` field
- Use Pydantic validators for date parsing and range checks
- Log all tool executions for debugging
- Validate user permissions before database operations
- Keep tool descriptions clear and specific

### ChatKit UI
- Enable streaming for better perceived performance
- Show tool calls visually with status badges
- Handle errors gracefully with user-friendly messages
- Implement loading states and typing indicators
- Make UI keyboard-accessible

### Database Operations
- Use transactions for atomic message saves
- Query with indexes (user_id, conversation_id)
- Limit history loads to 20 messages
- Use connection pooling (20 connections)
- Test concurrent access patterns

## Implementation Priorities

**Phase 0 Complete**: All research questions resolved

**Next**: Proceed to Phase 1 (data models, contracts, quickstart)
