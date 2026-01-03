# Phase III AI Chatbot Backend

FastAPI backend for AI-powered conversational task management using OpenAI and Model Context Protocol (MCP).

## Overview

This backend extends Phase II with conversational AI capabilities, allowing users to manage tasks through natural language chat interface.

## Architecture

### Core Components

1. **MCP Tool Registry** (`src/mcp/mcp_server.py`)
   - Manages task management tools (add, list, complete, delete, update)
   - Provides OpenAI function calling integration
   - Handles tool execution with context and error handling

2. **OpenAI Agent** (`src/agent.py`)
   - Conversational AI using OpenAI GPT-4o-mini
   - System prompt for task management guidance
   - Tool calling and conversation history management

3. **Chat Router** (`src/routes/chat.py`)
   - POST `/api/chat` - Send messages to AI chatbot
   - GET `/api/conversations` - List user conversations
   - GET `/api/conversations/{id}` - Get conversation with messages
   - DELETE `/api/conversations/{id}` - Delete conversation

4. **Database Models** (`src/models.py`)
   - `Conversation` - User chat sessions
   - `Message` - Individual messages (user, assistant, system)
   - `User`, `Task` - Inherited from Phase II

### Request/Response Flow

```
User → Frontend → POST /api/chat
  ↓
  Authentication (JWT)
  ↓
  Get/Create Conversation
  ↓
  Load Conversation History (last 20 messages)
  ↓
  Call OpenAI Agent with tools
  ↓
  Execute MCP Tools (e.g., add_task)
  ↓
  Get AI Response
  ↓
  Save Messages (user + assistant)
  ↓
  Return ChatResponse
```

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL database (or SQLite for development)
- OpenAI API key

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (create `.env` from `.env.example`):
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat

**POST /api/chat**
- Send message to AI chatbot
- Request: `{"message": "Add a task to buy groceries tomorrow", "conversation_id": "123"}`
- Response: `{"response": "I've added...", "conversation_id": "123", "tool_calls": [...]}`

**GET /api/conversations**
- List user's conversations
- Query params: `limit`, `offset`
- Response: `{"conversations": [...], "total": 10}`

**GET /api/conversations/{id}**
- Get conversation with full message history
- Response: `{"conversation": {...}, "messages": [...]}`

**DELETE /api/conversations/{id}**
- Delete conversation and all messages
- Response: `{"message": "Conversation deleted successfully"}`

### Health

**GET /health**
- Health check endpoint (no authentication required)

## MCP Tools

Tools available to the AI agent:

1. **add_task** - Create new task with title, description, due_date
2. **list_tasks** - List tasks with filtering (all, complete, incomplete)
3. **complete_task** - Mark task as complete/incomplete
4. **delete_task** - Permanently delete task
5. **update_task** - Update task fields (partial updates supported)

See `specs/003-ai-chatbot/contracts/mcp-tools.yaml` for detailed schemas.

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m contract      # MCP contract tests
pytest -v              # Verbose output
```

### Test Structure
```
tests/
├── conftest.py              # Fixtures and configuration
├── test_mcp_registry.py     # MCP registry unit tests
├── unit/                    # Unit tests for tools
├── integration/             # API endpoint tests
└── contract/                # MCP contract validation
```

## Development

### Adding New MCP Tools

1. Create tool handler in `src/mcp_tools/`:
```python
async def my_tool_handler(arguments: dict, context: dict) -> dict:
    user_id = context["user_id"]
    # Tool logic here
    return {"success": True, "result": {...}}
```

2. Register tool with MCP registry (in app startup):
```python
from src.mcp.mcp_server import get_mcp_registry

registry = get_mcp_registry()
registry.register_tool(
    name="my_tool",
    description="What the tool does",
    input_schema={...},
    handler=my_tool_handler
)
```

3. Update system prompt in `src/agent.py` to include new tool guidance

### Code Quality

- All code follows PEP 8 style guide
- Type hints used throughout
- Async/await for all I/O operations
- Comprehensive error handling and logging

## Deployment

### Railway (Recommended)

1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway automatically detects Procfile and deploys

### Environment Variables (Production)

```
DATABASE_URL=<neon-postgres-connection-string>
OPENAI_API_KEY=<openai-api-key>
SECRET_KEY=<secure-random-key>
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV=production
```

## Security

- JWT authentication required for all chat endpoints
- Task ownership validation in all MCP tools
- Input validation with Pydantic schemas
- SQL injection prevention via SQLModel ORM
- Rate limiting recommended (30 req/min per user)

## Performance

- Connection pooling: 20 connections for PostgreSQL
- Conversation history limited to 20 messages per request
- Database indexes on user_id, conversation_id, created_at
- Async operations throughout for non-blocking I/O

## Monitoring

Logs include:
- Tool execution (name, user, duration, success/failure)
- OpenAI API calls (model, message count, tool count)
- Authentication attempts
- Error traces with context

## Troubleshooting

**OpenAI API errors:**
- Check `OPENAI_API_KEY` is set correctly
- Verify OpenAI account has credits
- Check rate limits in OpenAI dashboard

**Database connection issues:**
- Verify `DATABASE_URL` format
- Check database is running and accessible
- Review connection pool settings

**Tool execution failures:**
- Check tool logs for error details
- Verify user has permission to access resources
- Validate tool input schemas

## Phase III Completion Status

### Completed (Phase 2 Foundational Tasks)
- ✅ T015: ChatRequest/ChatResponse schemas
- ✅ T016: MCP server with tool registry
- ✅ T017: OpenAI agent client
- ✅ T018: Chat router with POST /chat endpoint
- ✅ T022: Pytest conftest.py with fixtures

### Next Steps (User Story Implementation)
- T023-T027: Tests for US1 (Natural Language Task Creation)
- T028-T034: US1 Backend Implementation (add_task tool)
- T041-T048: US2 Backend Implementation (list_tasks tool)
- T051-T057: US3 Backend Implementation (complete_task tool)

See `specs/003-ai-chatbot/tasks.md` for full task breakdown.

## Documentation

- API Specification: `specs/003-ai-chatbot/contracts/chat-api.yaml`
- MCP Tools: `specs/003-ai-chatbot/contracts/mcp-tools.yaml`
- Data Model: `specs/003-ai-chatbot/data-model.md`
- Implementation Plan: `specs/003-ai-chatbot/plan.md`

## License

Part of Evolution of Todo - Certified Cloud Applied Generative AI Engineering curriculum.
