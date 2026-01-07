# Quickstart: AI-Powered Todo Chatbot

**Feature**: 003-ai-chatbot
**Date**: 2026-01-01
**Audience**: Developers implementing Phase III

## Overview

This quickstart guide provides concrete integration scenarios for implementing the AI-Powered Todo Chatbot. It demonstrates how backend and frontend components interact through the API contract.

## Prerequisites

- Phase II deployed and operational (JWT authentication working)
- OpenAI API key obtained and configured
- PostgreSQL database accessible (Neon)
- Development environment set up (Python 3.13+, Node.js 18+)

## Integration Scenarios

### Scenario 1: User Creates First Task via Chat

**Flow**: User sends first message → Backend creates conversation → AI calls add_task tool → Task created → Response sent

**Frontend (ChatKit)**:
```typescript
// User types: "Add a task to buy groceries tomorrow"
// ChatKit automatically sends POST to /api/chat

// Request sent by ChatKit
POST /api/chat
Headers: { Authorization: "Bearer <jwt_token>" }
Body: {
  "message": "Add a task to buy groceries tomorrow"
  // No conversation_id (first message)
}
```

**Backend Processing**:
```python
# 1. Validate JWT → get user_id = 1
# 2. No conversation_id → create new conversation
conversation = Conversation(user_id=1, title="Add a task to buy groceries tomorro...")
db.add(conversation)
conversation_id = conversation.id  # e.g., 123

# 3. Load history (empty for new conversation)
history = []

# 4. Call OpenAI agent with tools
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Add a task to buy groceries tomorrow"}
]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=openai_tools
)

# 5. Agent returns tool_call for add_task
tool_call = response.choices[0].message.tool_calls[0]
# function.name = "add_task"
# function.arguments = {"title": "Buy groceries", "due_date": "2026-01-02T00:00:00Z"}

# 6. Execute MCP tool
result = await execute_mcp_tool(
    "add_task",
    {"title": "Buy groceries", "due_date": "2026-01-02T00:00:00Z"},
    context={"user_id": 1}
)
# result = {"success": true, "task": {"id": 42, ...}}

# 7. Get final response with tool result
messages.append({"role": "tool", "content": json.dumps(result)})
final_response = client.chat.completions.create(model="gpt-4", messages=messages)
# final_response.content = "I've added 'Buy groceries' to your tasks for tomorrow."

# 8. Save messages to database
await save_message(conversation_id, "user", "Add a task to buy groceries tomorrow")
await save_message(
    conversation_id,
    "assistant",
    "I've added 'Buy groceries' to your tasks for tomorrow.",
    tool_calls=[{"tool_name": "add_task", "result": result}]
)

# 9. Return response
return {
    "response": "I've added 'Buy groceries' to your tasks for tomorrow.",
    "conversation_id": "123",
    "tool_calls": [{"tool_name": "add_task", "result": result}]
}
```

**Frontend Display**:
```typescript
// ChatKit displays:
// User: "Add a task to buy groceries tomorrow"
// AI: "I've added 'Buy groceries' to your tasks for tomorrow."
//     ✓ add_task: Created task #42
```

---

### Scenario 2: User Lists Tasks in Existing Conversation

**Flow**: User asks to see tasks → Backend loads history → AI calls list_tasks → Results returned → Response formatted

**Frontend**:
```typescript
// User types: "Show me my incomplete tasks"
POST /api/chat
Headers: { Authorization: "Bearer <jwt_token>" }
Body: {
  "message": "Show me my incomplete tasks",
  "conversation_id": "123"  // Existing conversation
}
```

**Backend Processing**:
```python
# 1. Validate JWT → user_id = 1
# 2. Verify conversation ownership
conversation = await get_conversation(123, user_id=1)  # Verify belongs to user

# 3. Load last 20 messages
history = await load_conversation_history(123, limit=20)
# history = [
#   {"role": "user", "content": "Add a task to buy groceries tomorrow"},
#   {"role": "assistant", "content": "I've added...", "tool_calls": [...]},
#   ...
# ]

# 4. Call agent with history + new message
messages = [system_prompt] + history + [
    {"role": "user", "content": "Show me my incomplete tasks"}
]
response = client.chat.completions.create(model="gpt-4", messages=messages, tools=tools)

# 5. Agent calls list_tasks
tool_call.function.arguments = {"status": "incomplete", "limit": 50}

# 6. Execute tool
result = await execute_mcp_tool(
    "list_tasks",
    {"status": "incomplete"},
    context={"user_id": 1}
)
# result = {
#   "success": true,
#   "tasks": [
#     {"id": 42, "title": "Buy groceries", "completed": false, ...},
#     {"id": 43, "title": "Call mom", "completed": false, ...}
#   ],
#   "total": 2
# }

# 7. Get final response
final = "You have 2 incomplete tasks:\n1. Buy groceries (due tomorrow)\n2. Call mom (due today)"

# 8. Save messages
await save_conversation_turn(123, user_message, final, tool_calls=[...])

# 9. Return
return {"response": final, "conversation_id": "123", "tool_calls": [...]}
```

---

### Scenario 3: User Resumes Conversation After Browser Restart

**Flow**: User opens app → Frontend loads conversations list → User selects conversation → History displayed

**Frontend**:
```typescript
// 1. On app load
useEffect(() => {
  async function loadConversations() {
    const response = await fetch('/api/conversations', {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    setConversations(data.conversations);
    // Display in sidebar
  }
  loadConversations();
}, []);

// 2. User clicks conversation in sidebar
const selectConversation = async (conversationId: string) => {
  const response = await fetch(`/api/conversations/${conversationId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await response.json();

  // Load conversation and messages into ChatKit
  // ChatKit automatically displays message history
  setCurrentConversation(data.conversation);
  setMessages(data.messages);
};
```

**Backend**:
```python
# GET /api/conversations
@router.get("/conversations")
async def list_conversations(current_user: User = Depends(get_current_user)):
    conversations = await get_user_conversations(current_user.id, limit=50)
    return {
        "conversations": [
            {
                "id": str(conv.id),
                "title": conv.title,
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ],
        "total": len(conversations)
    }

# GET /api/conversations/{id}
@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    conversation = await get_conversation_with_messages(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    return {
        "conversation": {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        },
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "created_at": msg.created_at.isoformat()
            }
            for msg in conversation.messages
        ]
    }
```

---

### Scenario 4: Message Streaming for Long Responses

**Flow**: User sends message → Backend streams response chunks → Frontend displays in real-time

**Frontend**:
```typescript
// ChatKit with streaming enabled
<ChatKit
  apiUrl="/api/chat"
  authToken={token}
  streaming={true}
  onMessageStream={(chunk) => {
    // Handle streaming chunks
    // ChatKit automatically appends to message display
  }}
/>
```

**Backend**:
```python
@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    async def generate():
        # Load history
        history = await load_conversation_history(request.conversation_id)

        # Stream from OpenAI
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[system] + history + [{"role": "user", "content": request.message}],
            tools=tools,
            stream=True
        )

        full_content = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield f"data: {json.dumps({'content': content})}\n\n"

        # Save complete message after streaming done
        await save_message(conversation_id, "assistant", full_content)

    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

### Scenario 5: Tool Execution with Error Handling

**Flow**: User requests action → AI calls tool → Tool fails → Error handled gracefully

**Backend**:
```python
async def execute_mcp_tool(tool_name, tool_input, context):
    """Execute MCP tool with comprehensive error handling"""
    try:
        # Get tool
        tool = mcp_server.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool {tool_name} not found"}

        # Validate input
        validated_input = tool.input_schema(**tool_input)

        # Execute
        result = await tool.execute(validated_input, context)
        return result

    except ValidationError as e:
        # Input validation failed
        return {
            "success": False,
            "error": f"Invalid input: {e.errors()[0]['msg']}"
        }

    except PermissionError:
        # User doesn't own the task
        return {
            "success": False,
            "error": "Task not found or access denied"
        }

    except DatabaseError as e:
        # Database operation failed
        logger.error(f"Database error in {tool_name}: {e}")
        return {
            "success": False,
            "error": "Database operation failed"
        }

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error in {tool_name}: {e}", exc_info=True)
        return {
            "success": False,
            "error": "An unexpected error occurred"
        }
```

**Frontend Display**:
```typescript
// On tool error, ChatKit shows:
// AI: "I couldn't complete that action. The task wasn't found."
//     ✗ complete_task: Task not found or access denied
```

---

## Development Workflow

### Backend Development (chatbot-architect agent)

1. Set up project structure in `Phase-III-AI-Chatbot/backend/`
2. Create database models (Conversation, Message)
3. Implement Alembic migration for new tables
4. Create MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
5. Implement MCP server initialization and tool registration
6. Integrate OpenAI Agents SDK with system prompt
7. Create chat router with endpoint handlers
8. Implement conversation management functions
9. Add error handling and logging
10. Write unit tests for tools and integration tests for endpoints

### Frontend Development (chatbot-frontend-expert agent)

1. Set up project structure in `Phase-III-AI-Chatbot/frontend/`
2. Install OpenAI ChatKit and dependencies
3. Create AuthContext for JWT token management
4. Implement chat page with ChatKit component
5. Create ConversationList component for sidebar
6. Implement ChatMessage component with tool call visualization
7. Create API route proxy (/api/chat → backend)
8. Add error boundaries and error handling
9. Style with Tailwind CSS for responsive design
10. Write component tests and E2E tests

### Parallel Execution

**Both agents start simultaneously after API contract is finalized in plan.md**

**Coordination Points**:
- **Upfront**: API contract defined (chat-api.yaml)
- **Day 2**: Verify contract interpretation alignment
- **Day 4**: Run integration tests between partial implementations
- **Day 6**: Final integration and bug fixes

**Expected Timeline**: 7 days with parallel execution vs 12 days sequential (42% reduction)

---

## Environment Configuration

### Frontend (.env.local)

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_PHASE2_API=http://localhost:8000  # For JWT auth
```

### Backend (.env)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@neon-host/dbname
OPENAI_API_KEY=sk-...
SECRET_KEY=<same_as_phase2>  # For JWT validation
ALGORITHM=HS256
```

## Testing Integration

### Contract Testing

```python
# Backend contract test
def test_chat_endpoint_contract():
    response = client.post(
        "/api/chat",
        json={"message": "Add a task"},
        headers={"Authorization": f"Bearer {valid_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response matches contract
    assert "response" in data
    assert "conversation_id" in data
    assert "tool_calls" in data
    assert isinstance(data["tool_calls"], list)
```

```typescript
// Frontend contract test
test('chat API returns expected structure', async () => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: 'Test' })
  });

  const data = await response.json();

  expect(data).toHaveProperty('response');
  expect(data).toHaveProperty('conversation_id');
  expect(data).toHaveProperty('tool_calls');
  expect(Array.isArray(data.tool_calls)).toBe(true);
});
```

### End-to-End Testing

```typescript
// E2E test: Complete task creation flow
test('user can create task via chat', async () => {
  // 1. Login (Phase II)
  const { token } = await login('user@test.com', 'password');

  // 2. Send chat message
  const chatResponse = await fetch('/api/chat', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ message: 'Add a task to test E2E' })
  });

  const chatData = await chatResponse.json();

  // 3. Verify task created
  expect(chatData.response).toContain('added');
  expect(chatData.tool_calls[0].tool_name).toBe('add_task');
  expect(chatData.tool_calls[0].result.success).toBe(true);

  // 4. Verify task in database (call Phase II list endpoint)
  const tasksResponse = await fetch('/api/tasks', {
    headers: { Authorization: `Bearer ${token}` }
  });
  const tasks = await tasksResponse.json();

  expect(tasks).toContainEqual(
    expect.objectContaining({ title: 'Test E2E' })
  );
});
```

---

## Deployment Checklist

### Before Deployment

- [ ] OpenAI API key configured in backend environment
- [ ] Database migration tested locally
- [ ] JWT secret shared between Phase II and Phase III backends
- [ ] CORS configured to allow frontend domain
- [ ] Rate limiting tested with load tests
- [ ] Error handling tested with OpenAI API mocked failures
- [ ] Contract tests passing on both backend and frontend
- [ ] E2E tests passing

### Backend Deployment (Railway)

```bash
# 1. Set environment variables
railway env set OPENAI_API_KEY=sk-...
railway env set DATABASE_URL=postgresql://...
railway env set SECRET_KEY=<same_as_phase2>

# 2. Deploy
railway up

# 3. Run migration
railway run alembic upgrade head

# 4. Verify health
curl https://backend-url/health
```

### Frontend Deployment (Vercel)

```bash
# 1. Set environment variables
vercel env add NEXT_PUBLIC_BACKEND_URL production
# Enter: https://backend-url

# 2. Deploy
vercel --prod

# 3. Verify
curl https://frontend-url
```

---

## Troubleshooting

### Issue: ChatKit not sending messages

**Symptoms**: Message input exists but send button doesn't work

**Diagnosis**:
- Check browser console for errors
- Verify `apiUrl` prop points to correct backend
- Confirm `authToken` is valid JWT

**Fix**: Ensure ChatKit has valid authToken and apiUrl props

---

### Issue: Tool calls failing with permission errors

**Symptoms**: AI responds but tool execution fails with "access denied"

**Diagnosis**:
- Check JWT token contains correct user_id
- Verify task belongs to authenticated user
- Check database foreign key relationships

**Fix**: Ensure context passed to tools includes user_id from JWT

---

### Issue: Conversation history not loading

**Symptoms**: Previous messages don't appear when reopening conversation

**Diagnosis**:
- Check database for saved messages
- Verify conversation_id passed correctly
- Check query filters for user_id scoping

**Fix**: Ensure conversation queries filter by user_id and conversation_id

---

## Quick Reference

### Key Endpoints

- `POST /api/chat` - Send message, get response
- `POST /api/chat/stream` - Send message, stream response
- `GET /api/conversations` - List user's conversations
- `GET /api/conversations/{id}` - Get specific conversation
- `DELETE /api/conversations/{id}` - Delete conversation

### MCP Tools

- `add_task(title, description?, due_date?)` - Create task
- `list_tasks(status?, limit?, offset?)` - Query tasks
- `complete_task(task_id, completed)` - Update status
- `delete_task(task_id)` - Remove task
- `update_task(task_id, title?, description?, due_date?)` - Modify task

### Database Tables (Phase III)

- `conversations` - Chat sessions
- `messages` - Chat messages
- `users` - Phase II (reference)
- `tasks` - Phase II (reference)
