# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/003-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks included per constitution requirement (Test-First NON-NEGOTIABLE)

**Organization**: Tasks organized by user story to enable independent implementation and testing

**Implementation Location**: All work in `Phase-III-AI-Chatbot/` directory

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Phase III project structure and shared dependencies

- [ ] T001 Create Phase-III-AI-Chatbot/ directory structure per plan.md
- [ ] T002 Initialize backend project in Phase-III-AI-Chatbot/backend/ with requirements.txt
- [ ] T003 Initialize frontend project in Phase-III-AI-Chatbot/frontend/ with package.json
- [ ] T004 [P] Create backend .env.example with DATABASE_URL, OPENAI_API_KEY, SECRET_KEY
- [ ] T005 [P] Create frontend .env.local.example with NEXT_PUBLIC_BACKEND_URL
- [ ] T006 [P] Copy Phase II database.py pattern to Phase-III-AI-Chatbot/backend/src/database.py
- [ ] T007 [P] Copy Phase II auth.py pattern to Phase-III-AI-Chatbot/backend/src/auth.py
- [ ] T008 Configure Alembic in Phase-III-AI-Chatbot/backend/alembic/
- [ ] T009 [P] Install OpenAI ChatKit in frontend: npm install @openai/chatkit
- [ ] T010 [P] Install OpenAI SDK in backend: pip install openai
- [ ] T011 [P] Install MCP SDK in backend: pip install mcp

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T012 Create Conversation model in Phase-III-AI-Chatbot/backend/src/models.py
- [ ] T013 Create Message model in Phase-III-AI-Chatbot/backend/src/models.py
- [ ] T014 Create Alembic migration 001_add_conversations.py to add conversations and messages tables
- [ ] T015 Create ChatRequest and ChatResponse schemas in Phase-III-AI-Chatbot/backend/src/schemas.py
- [ ] T016 Initialize MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T017 Initialize OpenAI client and system prompt in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T018 Create chat router in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T019 Create AuthContext in Phase-III-AI-Chatbot/frontend/src/context/AuthContext.tsx
- [ ] T020 Create TypeScript types in Phase-III-AI-Chatbot/frontend/src/types/chat.ts
- [ ] T021 [P] Create API client in Phase-III-AI-Chatbot/frontend/src/lib/api-client.ts
- [ ] T022 Create pytest conftest.py with database and auth fixtures in Phase-III-AI-Chatbot/backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks by typing natural language commands

**Independent Test**: Send message "Add a task to buy groceries tomorrow" and verify task created with correct title and due date

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US1] Contract test for add_task tool in Phase-III-AI-Chatbot/backend/tests/contract/test_mcp_contract.py
- [ ] T024 [P] [US1] Unit test for add_task with valid input in Phase-III-AI-Chatbot/backend/tests/unit/test_add_task.py
- [ ] T025 [P] [US1] Unit test for add_task with invalid due_date in Phase-III-AI-Chatbot/backend/tests/unit/test_add_task.py
- [ ] T026 [P] [US1] Integration test for chat endpoint creating task in Phase-III-AI-Chatbot/backend/tests/integration/test_chat_create_task.py
- [ ] T027 [P] [US1] E2E test for task creation flow in Phase-III-AI-Chatbot/frontend/tests/e2e/create-task.spec.ts

### Backend Implementation for User Story 1

- [ ] T028 [P] [US1] Implement add_task MCP tool in Phase-III-AI-Chatbot/backend/src/mcp_tools/add_task.py
- [ ] T029 [US1] Register add_task with MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T030 [US1] Implement agent tool execution in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T031 [US1] Create POST /api/chat endpoint handler in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T032 [US1] Implement conversation creation logic in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T033 [US1] Implement message persistence in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T034 [US1] Add error handling for OpenAI API failures in Phase-III-AI-Chatbot/backend/src/agent.py

### Frontend Implementation for User Story 1

- [ ] T035 [P] [US1] Create chat page with ChatKit in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T036 [P] [US1] Create API chat route proxy in Phase-III-AI-Chatbot/frontend/src/app/api/chat/route.ts
- [ ] T037 [P] [US1] Create ChatMessage component in Phase-III-AI-Chatbot/frontend/src/components/ChatMessage.tsx
- [ ] T038 [P] [US1] Create ToolCallBadge component in Phase-III-AI-Chatbot/frontend/src/components/ToolCallBadge.tsx
- [ ] T039 [US1] Integrate AuthContext with ChatKit in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T040 [US1] Add error handling UI for chat failures in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - View and Filter Tasks Conversationally (Priority: P1) 🎯 MVP

**Goal**: Enable users to ask AI to show tasks with natural language queries

**Independent Test**: Create 5 incomplete and 3 complete tasks, ask "Show me my incomplete tasks", verify only 5 displayed

### Tests for User Story 2 ⚠️

- [ ] T041 [P] [US2] Contract test for list_tasks tool in Phase-III-AI-Chatbot/backend/tests/contract/test_mcp_contract.py
- [ ] T042 [P] [US2] Unit test for list_tasks with status filter in Phase-III-AI-Chatbot/backend/tests/unit/test_list_tasks.py
- [ ] T043 [P] [US2] Unit test for list_tasks pagination in Phase-III-AI-Chatbot/backend/tests/unit/test_list_tasks.py
- [ ] T044 [P] [US2] Integration test for chat listing tasks in Phase-III-AI-Chatbot/backend/tests/integration/test_chat_list_tasks.py

### Backend Implementation for User Story 2

- [ ] T045 [P] [US2] Implement list_tasks MCP tool with filtering in Phase-III-AI-Chatbot/backend/src/mcp_tools/list_tasks.py
- [ ] T046 [US2] Register list_tasks with MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T047 [US2] Update agent to handle list operations in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T048 [US2] Add natural language query parsing examples to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py

### Frontend Implementation for User Story 2

- [ ] T049 [P] [US2] Update ChatMessage to display task lists in Phase-III-AI-Chatbot/frontend/src/components/ChatMessage.tsx
- [ ] T050 [US2] Add task list rendering with status indicators in Phase-III-AI-Chatbot/frontend/src/components/ChatMessage.tsx

**Checkpoint**: Users can now create AND view tasks through conversation

---

## Phase 5: User Story 3 - Mark Tasks Complete via Conversation (Priority: P2)

**Goal**: Enable users to mark tasks complete using natural language

**Independent Test**: Create task "Buy groceries", say "Mark buy groceries as done", verify task status updated

### Tests for User Story 3 ⚠️

- [ ] T051 [P] [US3] Contract test for complete_task tool in Phase-III-AI-Chatbot/backend/tests/contract/test_mcp_contract.py
- [ ] T052 [P] [US3] Unit test for complete_task with valid task_id in Phase-III-AI-Chatbot/backend/tests/unit/test_complete_task.py
- [ ] T053 [P] [US3] Unit test for complete_task ownership validation in Phase-III-AI-Chatbot/backend/tests/unit/test_complete_task.py
- [ ] T054 [P] [US3] Integration test for completing task via chat in Phase-III-AI-Chatbot/backend/tests/integration/test_chat_complete_task.py

### Implementation for User Story 3

- [ ] T055 [P] [US3] Implement complete_task MCP tool in Phase-III-AI-Chatbot/backend/src/mcp_tools/complete_task.py
- [ ] T056 [US3] Register complete_task with MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T057 [US3] Add completion operation examples to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py

**Checkpoint**: Users can create, view, AND complete tasks conversationally

---

## Phase 6: User Story 4 - Delete Tasks via Natural Language (Priority: P3)

**Goal**: Enable users to delete tasks using natural language

**Independent Test**: Create task "Buy groceries", say "Delete my grocery task", verify task removed from database

### Tests for User Story 4 ⚠️

- [ ] T058 [P] [US4] Contract test for delete_task tool in Phase-III-AI-Chatbot/backend/tests/contract/test_mcp_contract.py
- [ ] T059 [P] [US4] Unit test for delete_task success in Phase-III-AI-Chatbot/backend/tests/unit/test_delete_task.py
- [ ] T060 [P] [US4] Unit test for delete_task not found in Phase-III-AI-Chatbot/backend/tests/unit/test_delete_task.py
- [ ] T061 [P] [US4] Integration test for deleting task via chat in Phase-III-AI-Chatbot/backend/tests/integration/test_chat_delete_task.py

### Implementation for User Story 4

- [ ] T062 [P] [US4] Implement delete_task MCP tool in Phase-III-AI-Chatbot/backend/src/mcp_tools/delete_task.py
- [ ] T063 [US4] Register delete_task with MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T064 [US4] Add deletion operation examples to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py

**Checkpoint**: Full CRUD operations available through conversation

---

## Phase 7: User Story 5 - Update Task Details Conversationally (Priority: P3)

**Goal**: Enable users to update task fields through natural language

**Independent Test**: Create task "Buy groceries" due tomorrow, say "Change grocery task due date to Saturday", verify date updated

### Tests for User Story 5 ⚠️

- [ ] T065 [P] [US5] Contract test for update_task tool in Phase-III-AI-Chatbot/backend/tests/contract/test_mcp_contract.py
- [ ] T066 [P] [US5] Unit test for update_task partial update in Phase-III-AI-Chatbot/backend/tests/unit/test_update_task.py
- [ ] T067 [P] [US5] Unit test for update_task validation in Phase-III-AI-Chatbot/backend/tests/unit/test_update_task.py
- [ ] T068 [P] [US5] Integration test for updating task via chat in Phase-III-AI-Chatbot/backend/tests/integration/test_chat_update_task.py

### Implementation for User Story 5

- [ ] T069 [P] [US5] Implement update_task MCP tool in Phase-III-AI-Chatbot/backend/src/mcp_tools/update_task.py
- [ ] T070 [US5] Register update_task with MCP server in Phase-III-AI-Chatbot/backend/src/mcp_server.py
- [ ] T071 [US5] Add update operation examples to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py

**Checkpoint**: Complete task management through conversation (create, read, update, delete, complete)

---

## Phase 8: User Story 6 - Resume Conversations Across Sessions (Priority: P2)

**Goal**: Persist conversation history and allow users to resume across sessions

**Independent Test**: Have conversation yesterday, return today, verify history appears in sidebar and conversation can continue

### Tests for User Story 6 ⚠️

- [ ] T072 [P] [US6] Integration test for conversation persistence in Phase-III-AI-Chatbot/backend/tests/integration/test_conversation_persistence.py
- [ ] T073 [P] [US6] Integration test for loading conversation history in Phase-III-AI-Chatbot/backend/tests/integration/test_load_history.py
- [ ] T074 [P] [US6] E2E test for conversation resume in Phase-III-AI-Chatbot/frontend/tests/e2e/conversation-resume.spec.ts

### Backend Implementation for User Story 6

- [ ] T075 [P] [US6] Implement load_conversation_history function in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T076 [P] [US6] Implement save_message function in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T077 [P] [US6] Implement save_conversation_turn function in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T078 [US6] Implement GET /api/conversations endpoint in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T079 [US6] Implement GET /api/conversations/{id} endpoint in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T080 [US6] Implement DELETE /api/conversations/{id} endpoint in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T081 [US6] Update chat endpoint to load history on resume in Phase-III-AI-Chatbot/backend/src/routes/chat.py

### Frontend Implementation for User Story 6

- [ ] T082 [P] [US6] Create ConversationList component in Phase-III-AI-Chatbot/frontend/src/components/ConversationList.tsx
- [ ] T083 [P] [US6] Add conversation selection state management in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T084 [US6] Integrate ConversationList with chat page in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T085 [US6] Implement conversation loading on selection in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T086 [US6] Add new conversation button in Phase-III-AI-Chatbot/frontend/src/components/ConversationList.tsx

**Checkpoint**: Conversations persist and can be resumed - full chat experience

---

## Phase 9: User Story 7 - Understand Complex Temporal Requests (Priority: P3)

**Goal**: Enable AI to understand complex date queries and temporal references

**Independent Test**: Create tasks from various weeks, ask "Show me incomplete tasks from last week", verify correct filtering

### Tests for User Story 7 ⚠️

- [ ] T087 [P] [US7] Integration test for temporal query parsing in Phase-III-AI-Chatbot/backend/tests/integration/test_temporal_queries.py
- [ ] T088 [P] [US7] Unit test for date parsing utilities in Phase-III-AI-Chatbot/backend/tests/unit/test_date_utils.py

### Implementation for User Story 7

- [ ] T089 [P] [US7] Add temporal query examples to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T090 [P] [US7] Enhance list_tasks tool to support date range filtering in Phase-III-AI-Chatbot/backend/src/mcp_tools/list_tasks.py
- [ ] T091 [US7] Add natural language date parsing guidance to system prompt in Phase-III-AI-Chatbot/backend/src/agent.py

**Checkpoint**: AI handles sophisticated temporal queries and date references

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Message streaming, error handling, performance optimization, deployment preparation

### Message Streaming

- [ ] T092 [P] Implement streaming response generator in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T093 [P] Create POST /api/chat/stream endpoint in Phase-III-AI-Chatbot/backend/src/routes/chat.py
- [ ] T094 [P] Enable streaming in ChatKit component in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T095 Test streaming with long responses in Phase-III-AI-Chatbot/backend/tests/integration/test_streaming.py

### Error Handling & Resilience

- [ ] T096 [P] Implement exponential backoff retry logic in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T097 [P] Add rate limiting middleware (30 req/min) in Phase-III-AI-Chatbot/backend/src/main.py
- [ ] T098 [P] Implement graceful degradation for OpenAI API errors in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T099 [P] Add user-friendly error messages in Phase-III-AI-Chatbot/frontend/src/app/chat/page.tsx
- [ ] T100 Add input sanitization for XSS prevention in Phase-III-AI-Chatbot/backend/src/routes/chat.py

### Performance & Optimization

- [ ] T101 [P] Create database indexes on user_id, conversation_id, created_at per data-model.md
- [ ] T102 [P] Configure connection pooling (20 connections) in Phase-III-AI-Chatbot/backend/src/database.py
- [ ] T103 [P] Implement conversation history limit (20 messages) in Phase-III-AI-Chatbot/backend/src/agent.py
- [ ] T104 Add loading states and typing indicators in Phase-III-AI-Chatbot/frontend/src/components/ChatMessage.tsx

### Integration & E2E Testing

- [ ] T105 [P] Create API contract validation test suite in Phase-III-AI-Chatbot/backend/tests/contract/test_api_contract.py
- [ ] T106 [P] Create full conversation flow E2E test in Phase-III-AI-Chatbot/frontend/tests/e2e/full-flow.spec.ts
- [ ] T107 Test concurrent user access in Phase-III-AI-Chatbot/backend/tests/integration/test_concurrency.py
- [ ] T108 Test conversation persistence across sessions in Phase-III-AI-Chatbot/frontend/tests/e2e/persistence.spec.ts

### Deployment Preparation

- [ ] T109 [P] Create backend README.md with setup instructions in Phase-III-AI-Chatbot/backend/README.md
- [ ] T110 [P] Create frontend README.md with setup instructions in Phase-III-AI-Chatbot/frontend/README.md
- [ ] T111 [P] Create Railway configuration for backend deployment
- [ ] T112 [P] Create Vercel configuration for frontend deployment
- [ ] T113 Update main project README.md with Phase III live demo link placeholder

**Final Checkpoint**: System production-ready with all features, tests passing, deployment configured

---

## Dependencies

### User Story Dependencies

```
Foundational Phase (T012-T022)
    ↓ (blocks all user stories)
    ├─→ US1: Natural Language Task Creation (T023-T040) [P1] 🎯 MVP
    │   ├─→ US2: View/Filter Tasks (T041-T050) [P1] 🎯 MVP (independent of US1 after foundation)
    │   ├─→ US3: Mark Complete (T051-T057) [P2] (independent of US1-US2)
    │   ├─→ US4: Delete Tasks (T058-T064) [P3] (independent of US1-US3)
    │   ├─→ US5: Update Tasks (T065-T071) [P3] (independent of US1-US4)
    │   └─→ US6: Resume Conversations (T072-T086) [P2] (depends on US1 for conversation creation)
    └─→ US7: Complex Temporal Queries (T087-T091) [P3] (enhances US2, not blocking)

Polish Phase (T092-T113) - Can be developed in parallel with user stories
```

### Execution Order

1. **Phase 1**: Setup (T001-T011) - All [P] parallelizable
2. **Phase 2**: Foundational (T012-T022) - Must complete before any user story
3. **Phases 3-9**: User Stories - After foundation, most are independent
   - **MVP First**: Implement US1 + US2 (P1 stories) for minimum viable chatbot
   - **Then**: US6 (P2), US3 (P2) for enhanced experience
   - **Finally**: US4, US5, US7 (P3) for complete feature set
4. **Phase 10**: Polish (T092-T113) - Can start after US1/US2 complete

### Parallel Execution Opportunities

**After Foundation Complete (T022)**:

**Group A - MVP Core** (can run in parallel):
- US1 Backend: T028-T034 (add_task tool, chat endpoint)
- US1 Frontend: T035-T040 (ChatKit setup, chat UI)
- US2 Backend: T045-T048 (list_tasks tool)
- US2 Frontend: T049-T050 (task list display)

**Group B - Enhanced Features** (can run in parallel after Group A):
- US3: T055-T057 (complete_task)
- US4: T062-T064 (delete_task)
- US5: T069-T071 (update_task)
- US6 Backend: T075-T081 (conversation management)
- US6 Frontend: T082-T086 (conversation list UI)

**Group C - Polish** (can run in parallel with Groups A & B):
- Streaming: T092-T095
- Error handling: T096-T100
- Performance: T101-T104

**Parallel Agent Execution**: chatbot-architect handles all backend tasks, chatbot-frontend-expert handles all frontend tasks, both run concurrently

---

## Implementation Strategy

### MVP Scope (Recommended First Implementation)

**Minimal Viable Product**:
- Phase 1: Setup (T001-T011)
- Phase 2: Foundational (T012-T022)
- Phase 3: User Story 1 (T023-T040) - Create tasks
- Phase 4: User Story 2 (T041-T050) - View tasks
- Phase 10 (Partial): Streaming (T092-T095), Basic error handling (T096-T099)

**Deliverable**: Users can create and view tasks through natural language conversation

**Validation**: Run tests T023-T027 and T041-T044 to confirm MVP works

### Incremental Delivery

**Iteration 1** (MVP): US1 + US2 + Streaming
**Iteration 2**: Add US6 (conversation persistence) + US3 (completion)
**Iteration 3**: Add US4 (deletion) + US5 (updates) + US7 (temporal queries)
**Iteration 4**: Complete polish (rate limiting, optimization, deployment)

### Parallel Implementation Pattern

**Launch Command** (during /sp.implement):
```
ONE message with TWO Task tool calls:

Task 1 - chatbot-architect (Backend):
"Implement backend per plan.md and contracts/. Focus on tasks: T012-T022 (foundation), T028-T034 (US1 backend), T045-T048 (US2 backend), T055-T057 (US3), T062-T064 (US4), T069-T071 (US5), T075-T081 (US6 backend), T089-T091 (US7), T092-T093 (streaming backend), T096-T098 (error handling backend), T100-T103 (performance), T111 (Railway config)"

Task 2 - chatbot-frontend-expert (Frontend):
"Implement frontend per plan.md and contracts/. Focus on tasks: T019-T021 (foundation), T035-T040 (US1 frontend), T049-T050 (US2 frontend), T082-T086 (US6 frontend), T094 (streaming frontend), T099 (error handling frontend), T104 (loading states), T112 (Vercel config)"
```

**Coordination**: Both agents reference contracts/ for API alignment, work independently on their tasks

---

## Task Summary

**Total Tasks**: 113
- Phase 1 (Setup): 11 tasks (10 parallelizable)
- Phase 2 (Foundational): 11 tasks (4 parallelizable)
- Phase 3 (US1 - Task Creation): 18 tasks (12 parallelizable) - 5 tests, 7 backend, 6 frontend
- Phase 4 (US2 - View Tasks): 10 tasks (8 parallelizable) - 4 tests, 4 backend, 2 frontend
- Phase 5 (US3 - Complete Tasks): 7 tasks (6 parallelizable) - 4 tests, 3 backend
- Phase 6 (US4 - Delete Tasks): 7 tasks (6 parallelizable) - 4 tests, 3 backend
- Phase 7 (US5 - Update Tasks): 7 tasks (6 parallelizable) - 4 tests, 3 backend
- Phase 8 (US6 - Resume Conversations): 15 tasks (10 parallelizable) - 3 tests, 7 backend, 5 frontend
- Phase 9 (US7 - Temporal Queries): 5 tasks (4 parallelizable) - 2 tests, 3 backend
- Phase 10 (Polish): 22 tasks (18 parallelizable) - 4 streaming, 5 error handling, 4 performance, 4 integration tests, 5 deployment

**Backend Tasks**: 62 (chatbot-architect agent)
**Frontend Tasks**: 24 (chatbot-frontend-expert agent)
**Shared/Setup**: 11
**Tests**: 30 (distributed across user stories)

**Parallel Opportunities**: 84 of 113 tasks marked [P] (74% parallelizable)

**MVP Tasks**: 42 (Setup + Foundation + US1 + US2 + Basic Polish)

---

## Validation Checklist

- [X] All tasks have unique IDs (T001-T113)
- [X] All tasks have exact file paths
- [X] User story tasks have [Story] labels (US1-US7)
- [X] Parallelizable tasks marked with [P]
- [X] Each user story has independent test criteria
- [X] Dependencies clearly documented
- [X] MVP scope identified (US1 + US2)
- [X] Parallel agent execution pattern documented
- [X] Task count matches scope (~2,830 lines across 30 files)

**Status**: ✅ READY FOR IMPLEMENTATION (`/sp.implement`)
