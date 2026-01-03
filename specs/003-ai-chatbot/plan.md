# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot` | **Date**: 2026-01-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

## Summary

Build a conversational AI interface for task management using OpenAI ChatKit (frontend), OpenAI Agents SDK (backend orchestration), and MCP SDK (tool calling protocol). The system enables natural language task operations through a stateless, database-persisted architecture deployed across separate frontend/backend codebases in `Phase-III-AI-Chatbot/` directory.

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript 5 (frontend), Next.js 14
**Primary Dependencies**: OpenAI ChatKit, OpenAI Agents SDK (openai>=1.0), MCP SDK (mcp>=1.0), FastAPI 0.115+, Next.js 14+, SQLModel 0.0.20+
**Storage**: PostgreSQL (Neon Serverless) - extends Phase II schema with conversations and messages tables
**Testing**: pytest (backend), Jest/React Testing Library (frontend), Playwright (E2E)
**Target Platform**: Web (Vercel frontend, Railway backend)
**Project Type**: web (separate frontend/backend in Phase-III-AI-Chatbot/)
**Performance Goals**: <3s chat response (p95), <5s task creation end-to-end, handle 100 concurrent users
**Constraints**: <200ms database queries (p95), 20-message conversation history limit, 30 req/min rate limit per user
**Scale/Scope**: Support 1000 users, 10k conversations, 100k messages, stateless for horizontal scaling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Review

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Spec-Driven Development** | ✅ PASS | All code generated from spec.md via /sp.specify → /sp.plan → /sp.tasks → /sp.implement |
| **II. Progressive Complexity** | ✅ PASS | Phase III builds on Phase II (JWT auth, task models) without modification, adds AI layer |
| **III. Reusable Intelligence** | ✅ PASS | Created 4 skills (openai-chatkit, mcp-tools-builder, openai-agents-sdk, chatbot-architecture) and 2 agents (chatbot-architect, chatbot-frontend-expert) |
| **IV. AI-First Architecture** | ✅ PASS | Core feature is AI integration - ChatKit UI, Agents SDK orchestration, MCP tools |
| **V. Test-First (NON-NEGOTIABLE)** | ✅ PASS | Contract tests for API, unit tests for MCP tools, integration tests for agent, E2E for full flow - all written before implementation |
| **VI. Cloud-Native Ready** | ✅ PASS | Stateless architecture, PostgreSQL persistence, horizontal scaling support, containerizable |
| **VII. Modular Design** | ✅ PASS | Separate Phase-III-AI-Chatbot/ codebase, MCP tools as independent modules, clear API contracts |

**Result**: NO VIOLATIONS - Constitution fully satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (/sp.specify output)
├── plan.md              # This file (/sp.plan output)
├── research.md          # Technical research and decisions (/sp.plan Phase 0 output)
├── data-model.md        # Database entities and relationships (/sp.plan Phase 1 output)
├── quickstart.md        # Integration scenarios and examples (/sp.plan Phase 1 output)
├── contracts/           # API contracts (/sp.plan Phase 1 output)
│   ├── chat-api.yaml    # REST API for chat endpoints
│   └── mcp-tools.yaml   # MCP tool interface specifications
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification validation (from /sp.specify)
└── tasks.md             # Task breakdown (/sp.tasks command - created later)
```

### Source Code (repository root)

```text
Phase-III-AI-Chatbot/                    # Phase III root directory
├── backend/                             # FastAPI backend
│   ├── src/
│   │   ├── main.py                      # FastAPI app initialization
│   │   ├── database.py                  # Database connection (reuse Phase II pattern)
│   │   ├── auth.py                      # JWT validation (reference Phase II)
│   │   ├── models.py                    # SQLModel models (Conversation, Message)
│   │   ├── schemas.py                   # Pydantic request/response schemas
│   │   ├── agent.py                     # OpenAI Agents SDK integration
│   │   ├── mcp_server.py                # MCP server initialization and tool registry
│   │   ├── mcp_tools/                   # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py              # Create task tool
│   │   │   ├── list_tasks.py            # Query tasks tool
│   │   │   ├── complete_task.py         # Update status tool
│   │   │   ├── delete_task.py           # Delete task tool
│   │   │   └── update_task.py           # Update task fields tool
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── chat.py                  # Chat endpoint handlers
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_mcp_tools.py        # Test each tool
│   │   │   └── test_agent.py            # Test agent logic
│   │   ├── integration/
│   │   │   ├── test_chat_api.py         # Test chat endpoints
│   │   │   └── test_conversation_flow.py # Test full conversation flow
│   │   └── contract/
│   │       └── test_api_contract.py     # Validate API matches chat-api.yaml
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 001_add_conversations.py # Database migration
│   │   └── env.py
│   ├── requirements.txt                  # Python dependencies
│   ├── .env.example                      # Environment template
│   └── README.md                         # Backend setup instructions
│
└── frontend/                            # Next.js frontend
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx               # Root layout
    │   │   ├── page.tsx                 # Landing/redirect to chat
    │   │   ├── chat/
    │   │   │   └── page.tsx             # Main chat interface
    │   │   └── api/
    │   │       └── chat/
    │   │           └── route.ts         # Proxy to backend
    │   ├── components/
    │   │   ├── ChatMessage.tsx          # Custom message renderer
    │   │   ├── ConversationList.tsx     # Sidebar conversation list
    │   │   └── ToolCallBadge.tsx        # Tool execution indicator
    │   ├── context/
    │   │   └── AuthContext.tsx          # JWT token management
    │   ├── lib/
    │   │   └── api-client.ts            # Backend API wrapper
    │   └── types/
    │       └── chat.ts                  # TypeScript interfaces
    ├── tests/
    │   ├── components/
    │   │   └── ChatMessage.test.tsx     # Component tests
    │   ├── integration/
    │   │   └── chat-flow.test.ts        # Integration tests
    │   └── e2e/
    │       └── chat.spec.ts             # Playwright E2E tests
    ├── public/                          # Static assets
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── .env.local.example
    └── README.md                        # Frontend setup instructions
```

**Structure Decision**: Web application (Option 2) with separate frontend/backend in dedicated Phase-III-AI-Chatbot/ directory. This isolation prevents coupling with Phase II code while allowing database and authentication reuse.

## Complexity Tracking

> No Constitution violations - this section not needed

## Architecture Decisions

### AD-1: Stateless Server Architecture

**Decision**: Implement stateless backend with all conversation state in PostgreSQL

**Rationale**:
- Enables horizontal scaling (any instance handles any request)
- No sticky sessions or in-memory caches
- Crash resilience (no data loss on restart)
- Simpler load balancing

**Tradeoffs**:
- Database query on every request (mitigated by connection pooling and indexes)
- Slightly higher latency vs in-memory (acceptable for chat UX)

**Alternatives Rejected**:
- Redis cache: Adds dependency, still requires persistence
- In-memory: Not scalable, data loss risk

---

### AD-2: Separate Phase III Codebase

**Decision**: Create Phase-III-AI-Chatbot/ directory with independent frontend/backend

**Rationale**:
- No coupling with Phase II code (easier to maintain)
- Independent deployment pipeline
- Clear separation of concerns
- Can reference Phase II patterns without modification

**Tradeoffs**:
- Some code duplication (database.py, auth validation)
- Need to coordinate DATABASE_URL and SECRET_KEY across phases

**Alternatives Rejected**:
- Modify Phase II code: Violates progressive complexity, risky
- Monorepo shared code: Increases coupling, harder to isolate

---

### AD-3: MCP Protocol for Tool Calling

**Decision**: Use official MCP SDK for standardized tool interface

**Rationale**:
- Industry standard protocol
- Type-safe schemas with Pydantic
- Clear separation between definition and execution
- Future extensibility (add more tools easily)

**Tradeoffs**:
- Additional dependency (mcp package)
- Learning curve for MCP protocol

**Alternatives Rejected**:
- Custom tool interface: No standardization
- Direct function calling: Less maintainable

---

### AD-4: OpenAI ChatKit for Frontend

**Decision**: Use pre-built ChatKit components instead of custom chat UI

**Rationale**:
- Faster development (weeks → days)
- Production-tested components
- Built-in streaming, theming, accessibility
- Maintained by OpenAI

**Tradeoffs**:
- Less UI customization control
- Dependency on OpenAI package
- Potential breaking changes in future versions

**Alternatives Rejected**:
- Custom chat UI: Months of development, accessibility challenges
- Open-source chat libraries: Less integration with OpenAI ecosystem

---

### AD-5: Parallel Agent Execution

**Decision**: Run chatbot-architect and chatbot-frontend-expert agents concurrently during implementation

**Rationale**:
- 40%+ time savings via concurrent development
- Frontend and backend are independent (minimal coordination needed)
- API contract defined upfront eliminates blocking dependencies
- Agents have specialized skills for their domains

**Tradeoffs**:
- Requires careful API contract definition upfront
- Coordination checkpoints needed to prevent drift
- Slightly more complex task orchestration

**Alternatives Rejected**:
- Sequential development: Slower, no concurrency benefits
- Single full-stack agent: Less specialized, slower overall

---

## Technology Stack

### Backend Stack (Phase-III-AI-Chatbot/backend/)

**Core Framework**: FastAPI 0.115+
- Async support for non-blocking I/O
- OpenAPI documentation generation
- Dependency injection
- Middleware support

**AI Integration**:
- OpenAI Agents SDK (openai>=1.0): Agent orchestration, function calling
- MCP SDK (mcp>=1.0): Tool definition and execution protocol
- GPT-4: Natural language understanding

**Database**:
- SQLModel 0.0.20+: Pydantic-compatible ORM
- asyncpg 0.30+: Async PostgreSQL driver
- Alembic 1.13+: Database migrations
- PostgreSQL 15+ (Neon Serverless): Data persistence

**Authentication**:
- python-jose 3.3+: JWT validation (shared with Phase II)
- passlib 1.7.4: Password hashing (Phase II reference)

**Testing**:
- pytest 8.3+: Test framework
- httpx 0.27+: Async HTTP client for API tests
- pytest-asyncio: Async test support

**Deployment**:
- Railway: Cloud hosting
- Docker: Containerization
- Uvicorn: ASGI server

### Frontend Stack (Phase-III-AI-Chatbot/frontend/)

**Core Framework**: Next.js 14 with App Router
- React 18: UI components
- TypeScript 5: Type safety
- Server Components: Performance optimization

**Chat Interface**:
- OpenAI ChatKit (@openai/chatkit): Pre-built chat UI
- Server-Sent Events: Real-time message streaming

**Styling**:
- Tailwind CSS 3: Utility-first styling
- Glassmorphism design system (from Phase II)

**State Management**:
- React Context: Authentication state
- React hooks: Component state

**Testing**:
- Jest: Unit testing
- React Testing Library: Component testing
- Playwright: E2E testing

**Deployment**:
- Vercel: Serverless deployment
- Edge runtime: Global CDN

### Shared Infrastructure

**Database**: PostgreSQL on Neon (shared with Phase II)
- Existing tables: users, tasks
- New tables: conversations, messages

**Authentication**: JWT tokens (Phase II system)
- SECRET_KEY shared between phases
- Token validation in both backends

## File Structure Details

### Backend Files (18 implementation files)

**Core Application** (3 files):
1. `main.py` (100 lines): FastAPI app, middleware, exception handlers, health check
2. `database.py` (80 lines): AsyncSession factory, connection pooling, create_db_and_tables
3. `auth.py` (60 lines): JWT validation, get_current_user dependency

**Models and Schemas** (2 files):
4. `models.py` (120 lines): Conversation, Message SQLModel classes with relationships
5. `schemas.py` (80 lines): ChatRequest, ChatResponse, ConversationResponse Pydantic models

**AI Integration** (2 files):
6. `agent.py` (200 lines): OpenAI client, system prompt, agent processing, tool execution, streaming
7. `mcp_server.py` (100 lines): MCPServer initialization, tool registration, execute_mcp_tool function

**MCP Tools** (5 files):
8. `mcp_tools/add_task.py` (80 lines): Pydantic schema, tool decorator, create task logic
9. `mcp_tools/list_tasks.py` (100 lines): Filtering schema, query logic, pagination
10. `mcp_tools/complete_task.py` (70 lines): Update schema, status update logic
11. `mcp_tools/delete_task.py` (60 lines): Delete schema, ownership validation, delete logic
12. `mcp_tools/update_task.py` (90 lines): Partial update schema, field validation, update logic

**Routes** (1 file):
13. `routes/chat.py` (150 lines): Chat endpoint, streaming endpoint, conversation CRUD endpoints

**Database Migration** (1 file):
14. `alembic/versions/001_add_conversations.py` (60 lines): Create tables, indexes, foreign keys

**Tests** (4 files):
15. `tests/unit/test_mcp_tools.py` (200 lines): Test all 5 tools with various scenarios
16. `tests/integration/test_chat_api.py` (150 lines): Test chat endpoints with mocked OpenAI
17. `tests/contract/test_api_contract.py` (100 lines): Validate responses match chat-api.yaml
18. `tests/conftest.py` (80 lines): Pytest fixtures for database, auth tokens

**Total Backend**: ~1,680 lines

### Frontend Files (12 implementation files)

**Pages** (2 files):
1. `app/page.tsx` (40 lines): Landing page, redirect to /chat
2. `app/chat/page.tsx` (120 lines): Chat page with ChatKit, ConversationList, state management

**API Routes** (1 file):
3. `app/api/chat/route.ts` (80 lines): Proxy to backend, auth header forwarding

**Components** (4 files):
4. `components/ChatMessage.tsx` (100 lines): Custom message renderer with tool call badges
5. `components/ConversationList.tsx` (120 lines): Sidebar with conversation list, selection logic
6. `components/ToolCallBadge.tsx` (50 lines): Visual indicator for tool executions
7. `components/Layout.tsx` (60 lines): App layout wrapper

**Context** (1 file):
8. `context/AuthContext.tsx` (150 lines): JWT token management, login/logout, localStorage

**Library** (1 file):
9. `lib/api-client.ts` (100 lines): Typed API client for backend calls

**Types** (1 file):
10. `types/chat.ts` (80 lines): TypeScript interfaces for Conversation, Message, ToolCall

**Tests** (2 files):
11. `tests/components/ChatMessage.test.tsx` (100 lines): Component unit tests
12. `tests/e2e/chat.spec.ts` (150 lines): Playwright E2E tests for full chat flow

**Total Frontend**: ~1,150 lines

**Grand Total**: ~2,830 lines across both codebases

**Structure Decision**: Web application architecture with complete separation between Phase-III-AI-Chatbot/backend/ and Phase-III-AI-Chatbot/frontend/. Backend follows FastAPI modular structure with dedicated mcp_tools/ directory for tool implementations. Frontend uses Next.js App Router with client components for interactive chat UI. This structure enables parallel development by chatbot-architect and chatbot-frontend-expert agents working concurrently on independent codebases.

## Complexity Tracking

> **Not applicable** - No Constitution violations to justify

## Parallel Agent Execution Plan

### Agent Assignment

**chatbot-architect** (Backend):
- Responsible for: Database migrations, MCP tools, Agents SDK, Chat API, conversation management
- Skills: chatbot-architecture, openai-agents-sdk, mcp-tools-builder, fastapi-backend, sqlmodel-db
- Working directory: `Phase-III-AI-Chatbot/backend/`
- Dependencies: OpenAI API key, database credentials, Phase II auth reference

**chatbot-frontend-expert** (Frontend):
- Responsible for: ChatKit integration, chat UI, conversation list, auth context, API proxy
- Skills: openai-chatkit, nextjs-frontend, frontend-expert
- Working directory: `Phase-III-AI-Chatbot/frontend/`
- Dependencies: Backend API URL, JWT token from Phase II

### Coordination Strategy

**Upfront (Before parallel work)**:
- ✅ API contract defined in `contracts/chat-api.yaml`
- ✅ MCP tools contract in `contracts/mcp-tools.yaml`
- ✅ Data models documented in `data-model.md`
- ✅ Integration scenarios in `quickstart.md`

**During Development**:
- **25% checkpoint**: Verify contract interpretation (both agents read contract, confirm understanding)
- **50% checkpoint**: Run integration tests (backend exposes endpoints, frontend calls them)
- **75% checkpoint**: Final alignment (fix any mismatches, coordinate final features)
- **100%**: Full integration testing and validation

**Communication**:
- Shared artifacts: contracts/, data-model.md, quickstart.md
- No inter-agent dependencies (work independently)
- Integration via API contract only

### Launch Pattern

**Implementation command**:
```
/sp.implement
→ Launches TWO agents in parallel via ONE message with TWO Task tool calls:
  1. Task(agent="chatbot-architect", prompt="Implement backend per spec...")
  2. Task(agent="chatbot-frontend-expert", prompt="Implement frontend per spec...")
```

**Expected Outcome**: Both agents complete within 7 days, integration takes 1 day, total 8 days vs 14 days sequential (43% faster)

## Implementation Phases

### Phase 0: Research ✅ COMPLETE

**Output**: research.md

**Findings**:
- OpenAI ChatKit integration pattern defined
- MCP tool registration approach documented
- Stateless conversation management strategy established
- Database schema designed
- Message streaming implementation clarified
- Tool execution flow documented
- Authentication token flow specified
- Parallel agent coordination plan created

**Research Artifacts**:
- 8 research questions resolved
- Technology best practices documented
- Implementation patterns defined

---

### Phase 1: Design & Contracts ✅ COMPLETE

**Output**: data-model.md, contracts/, quickstart.md

**Deliverables**:

1. **data-model.md** (95 lines):
   - Conversation entity (6 attributes, relationships, validation rules)
   - Message entity (6 attributes, relationships, state transitions)
   - Task entity reference (Phase II - no changes)
   - User entity reference (Phase II - no changes)
   - Relationships diagram
   - Migration strategy
   - Query patterns
   - Data integrity rules

2. **contracts/chat-api.yaml** (OpenAPI 3.0):
   - POST /api/chat endpoint specification
   - POST /api/chat/stream (SSE) specification
   - GET /api/conversations endpoint
   - GET /api/conversations/{id} endpoint
   - DELETE /api/conversations/{id} endpoint
   - Request/response schemas
   - Error response formats
   - Authentication requirements

3. **contracts/mcp-tools.yaml**:
   - 5 tool interface specifications
   - Input/output schemas for each tool
   - Validation rules
   - Example requests/responses
   - Shared patterns (auth context, error responses)
   - Logging requirements
   - Testing requirements

4. **quickstart.md** (280 lines):
   - 5 integration scenarios with code examples
   - Development workflow for parallel agents
   - Environment configuration
   - Testing integration patterns
   - Deployment checklist
   - Troubleshooting guide
   - Quick reference

**Agent Context Update**: Will run after plan completion

---

### Phase 2: Task Breakdown

**Status**: ⏳ PENDING - Use `/sp.tasks` command next

**Expected Output**: tasks.md with dependency-ordered implementation tasks

**Task Categories**:
- Setup: Project initialization, dependencies, environment
- Database: Migration, models, indexes
- Backend Core: MCP tools, Agents SDK, chat endpoints
- Frontend Core: ChatKit setup, chat UI, conversation list
- Integration: Contract testing, E2E testing
- Deployment: Railway backend, Vercel frontend

---

## Testing Strategy

### Backend Tests

**Unit Tests** (pytest):
```python
# Test MCP tools independently
def test_add_task_success()
def test_add_task_invalid_due_date()
def test_list_tasks_filter_incomplete()
def test_complete_task_ownership_validation()
def test_delete_task_not_found()
def test_update_task_partial_update()
```

**Integration Tests** (pytest + httpx):
```python
# Test chat API with mocked OpenAI
@pytest.mark.asyncio
async def test_chat_endpoint_creates_task()
async def test_chat_endpoint_streams_response()
async def test_conversation_history_loaded()
async def test_rate_limiting()
```

**Contract Tests** (pytest + jsonschema):
```python
# Validate API responses match OpenAPI spec
def test_chat_response_matches_contract()
def test_error_responses_match_contract()
```

### Frontend Tests

**Component Tests** (Jest + RTL):
```typescript
test('ChatMessage displays tool calls correctly')
test('ConversationList loads and selects conversations')
test('ToolCallBadge shows status icons')
```

**E2E Tests** (Playwright):
```typescript
test('user can create task via chat', async ({ page }) => {
  await page.goto('/chat');
  await page.fill('input[placeholder*="message"]', 'Add task to test');
  await page.click('button:has-text("Send")');
  await expect(page.locator('text=added')).toBeVisible();
});
```

### Integration Tests (Both)

```typescript
// Full flow test
test('chat message creates task in database', async () => {
  // 1. Send chat message via frontend
  // 2. Verify backend processes with agent
  // 3. Confirm task exists in database
  // 4. Verify conversation saved
});
```

## Deployment Strategy

### Backend Deployment (Railway)

**Environment Variables**:
```bash
DATABASE_URL=postgresql+asyncpg://...  # Neon connection string
OPENAI_API_KEY=sk-...
SECRET_KEY=<same_as_phase2>
ALGORITHM=HS256
PORT=8000
```

**Build Command**: `pip install -r requirements.txt`
**Start Command**: `alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT}`

**Health Check**: `GET /health` (should return 200)

### Frontend Deployment (Vercel)

**Environment Variables**:
```bash
NEXT_PUBLIC_BACKEND_URL=https://phase3-backend.railway.app
NEXT_PUBLIC_PHASE2_API=https://phase2-backend.railway.app  # For JWT auth
```

**Build Command**: `npm run build`
**Output Directory**: `.next`

**Deploy**: `vercel --prod`

## Risk Mitigation Implementation

### OpenAI Rate Limiting

**Implementation**:
```python
# Exponential backoff
for attempt in range(3):
    try:
        return await client.chat.completions.create(...)
    except RateLimitError:
        if attempt < 2:
            await asyncio.sleep(2 ** attempt)
        else:
            raise
```

### Cost Monitoring

**Implementation**:
- Limit conversation history to 20 messages
- Set OpenAI dashboard budget alerts
- Log token usage per request
- Implement daily per-user limits if needed

### Natural Language Fallbacks

**Implementation**:
```python
# System prompt includes fallback guidance
SYSTEM_PROMPT = """...
If you don't understand the request, respond with:
"I couldn't understand that. I can help you:
- Add tasks
- Show your tasks
- Mark tasks complete
- Delete tasks
- Update task details

What would you like to do?"
"""
```

## Next Steps

1. ✅ Specification created (spec.md)
2. ✅ Research completed (research.md)
3. ✅ Design completed (data-model.md, contracts/, quickstart.md)
4. ⏳ **Next**: Run `/sp.tasks` to generate implementation tasks
5. ⏳ **Then**: Run `/sp.implement` with parallel agents (chatbot-architect + chatbot-frontend-expert)
6. ⏳ **Finally**: Deploy to Railway (backend) and Vercel (frontend)

---

**Plan Status**: ✅ COMPLETE - Ready for task generation (`/sp.tasks`)
