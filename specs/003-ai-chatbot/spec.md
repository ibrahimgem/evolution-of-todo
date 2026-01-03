# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `003-ai-chatbot`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Phase III: AI-Powered Todo Chatbot - Build an AI-powered conversational interface for the todo application using OpenAI ChatKit for the frontend, OpenAI Agents SDK for orchestration, and the official MCP (Model Context Protocol) SDK for tool calling. The system enables users to manage tasks through natural language conversations while maintaining stateless architecture with database-persisted conversation state."

**Implementation Location**: All Phase III work must be implemented in the `Phase-III-AI-Chatbot/` directory at the project root.

## User Scenarios & Testing

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a user, I want to create tasks by typing natural language commands (e.g., "Add a task to buy groceries tomorrow" or "Remind me to review the project by Friday"), so I can quickly add todos without filling out forms.

**Why this priority**: Task creation is the core value proposition of the todo application. Natural language input removes friction and makes task entry 10x faster than traditional forms. This is the minimum viable chatbot feature.

**Independent Test**: Can be fully tested by sending a message to create a task and verifying the task appears in the database with correct title, description, and due date extracted from natural language.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they type "Add a task to buy groceries tomorrow", **Then** a new task is created with title "Buy groceries" and due date set to tomorrow's date
2. **Given** a user is authenticated, **When** they type "Remind me to call mom at 3pm", **Then** a new task is created with title "Call mom" and due date set to today at 3pm
3. **Given** a user types "Add buy milk", **When** the AI processes the message, **Then** a task is created with title "Buy milk" and no due date
4. **Given** a user types an ambiguous request like "Add something", **When** the AI cannot extract a clear task, **Then** the AI asks for clarification with a helpful message

---

### User Story 2 - View and Filter Tasks Conversationally (Priority: P1)

As a user, I want to ask the AI to show my tasks in various ways (e.g., "Show me incomplete tasks" or "What do I need to do today?"), so I can quickly review my todo list without navigating through UI filters.

**Why this priority**: Viewing tasks is equally critical as creating them. Users must be able to see what they've added to derive value. Natural language querying makes finding specific tasks intuitive.

**Independent Test**: Can be fully tested by creating several tasks (some complete, some incomplete, some with due dates) and asking various natural language queries to verify correct filtering and display.

**Acceptance Scenarios**:

1. **Given** a user has 5 incomplete and 3 complete tasks, **When** they ask "Show me my incomplete tasks", **Then** the AI displays the 5 incomplete tasks with their details
2. **Given** a user has tasks with various due dates, **When** they ask "What's due today?", **Then** the AI shows only tasks with today's due date
3. **Given** a user has no tasks, **When** they ask "Show me my tasks", **Then** the AI responds with a friendly message indicating no tasks exist
4. **Given** a user asks "Show me everything from last week", **When** the AI processes the query, **Then** tasks created or due in the past 7 days are displayed

---

### User Story 3 - Mark Tasks Complete via Conversation (Priority: P2)

As a user, I want to tell the AI to mark tasks complete (e.g., "Mark 'buy groceries' as done" or "I finished the project review"), so I can update task status naturally without clicking checkboxes.

**Why this priority**: Completing tasks is a frequent action but less critical than creating/viewing. Users can still derive value from P1 features even if completion requires manual UI interaction.

**Independent Test**: Can be fully tested by creating tasks and using various natural language completion commands to verify status updates correctly.

**Acceptance Scenarios**:

1. **Given** a user has an incomplete task "Buy groceries", **When** they say "Mark buy groceries as done", **Then** the task status is updated to complete
2. **Given** a user has multiple tasks, **When** they say "I finished task 3", **Then** the task with ID 3 is marked complete
3. **Given** a user references a non-existent task, **When** they say "Complete the meeting task", **Then** the AI responds that no matching task was found
4. **Given** a task is already complete, **When** the user tries to mark it complete again, **Then** the AI confirms it's already done

---

### User Story 4 - Delete Tasks via Natural Language (Priority: P3)

As a user, I want to ask the AI to delete tasks (e.g., "Delete my grocery task" or "Remove all completed tasks"), so I can clean up my todo list conversationally.

**Why this priority**: Deletion is useful but not critical for MVP. Users can accumulate tasks without immediate harm, and manual deletion via UI is acceptable initially.

**Independent Test**: Can be fully tested by creating tasks and using various deletion commands to verify tasks are removed from the database.

**Acceptance Scenarios**:

1. **Given** a user has a task "Buy groceries", **When** they say "Delete my grocery task", **Then** the task is removed from the database
2. **Given** a user has 3 complete and 2 incomplete tasks, **When** they say "Remove all completed tasks", **Then** only the 3 complete tasks are deleted
3. **Given** a user tries to delete a non-existent task, **When** they say "Delete the meeting", **Then** the AI responds that no matching task was found
4. **Given** deletion would remove a user's only task, **When** they confirm deletion, **Then** the task is removed and the AI confirms with an empty state message

---

### User Story 5 - Update Task Details Conversationally (Priority: P3)

As a user, I want to update task details through conversation (e.g., "Change the grocery task due date to Saturday" or "Update project review description to include budget analysis"), so I can modify tasks without editing forms.

**Why this priority**: Updating is less frequent than creating/viewing/completing. Users can work around by deleting and recreating tasks if updates aren't available initially.

**Independent Test**: Can be fully tested by creating a task and using various update commands to verify title, description, and due date changes persist correctly.

**Acceptance Scenarios**:

1. **Given** a user has a task "Buy groceries" due tomorrow, **When** they say "Change the grocery task due date to Saturday", **Then** the due date is updated to Saturday
2. **Given** a user has a task without a description, **When** they say "Add description 'organic produce only' to my grocery task", **Then** the description field is updated
3. **Given** a user tries to update a non-existent task, **When** they reference it, **Then** the AI responds that no matching task was found
4. **Given** a user says "Update my task", **When** no specific field is mentioned, **Then** the AI asks what they want to update

---

### User Story 6 - Resume Conversations Across Sessions (Priority: P2)

As a user, I want my conversation history preserved, so I can resume context across browser sessions and continue where I left off.

**Why this priority**: Conversation persistence improves user experience significantly but isn't required for core functionality. Users can still manage tasks even if each session starts fresh.

**Independent Test**: Can be fully tested by having a conversation, closing/reopening the browser, and verifying previous messages and context are restored.

**Acceptance Scenarios**:

1. **Given** a user had a conversation yesterday, **When** they return today, **Then** they see their conversation history in the sidebar
2. **Given** a user has multiple conversations, **When** they select one from the sidebar, **Then** the conversation loads with full message history
3. **Given** a user creates a new conversation, **When** they send the first message, **Then** a conversation title is auto-generated from that message
4. **Given** a conversation has 50 messages, **When** it's loaded, **Then** only the most recent 20 messages are used for AI context (for performance)

---

### User Story 7 - Understand Complex Temporal Requests (Priority: P3)

As a user, I want the AI to understand complex requests with dates and priorities (e.g., "Show me incomplete tasks from last week" or "What's high priority and due this week?"), so I can perform sophisticated queries naturally.

**Why this priority**: Advanced querying is a nice-to-have that enhances power users' experience but isn't essential for basic task management.

**Independent Test**: Can be fully tested by creating tasks with various dates and priorities, then issuing complex queries to verify correct filtering.

**Acceptance Scenarios**:

1. **Given** a user has tasks from various weeks, **When** they ask "Show me incomplete tasks from last week", **Then** only incomplete tasks created 7-14 days ago are shown
2. **Given** a user has tasks with different priorities, **When** they ask "What's high priority and due this week?", **Then** only high-priority tasks due within 7 days are displayed
3. **Given** a user asks about "next Friday", **When** the AI calculates the date, **Then** it correctly identifies the date of the upcoming Friday (not one from a past week)
4. **Given** ambiguous temporal references like "soon", **When** the AI processes them, **Then** it makes reasonable assumptions (e.g., "soon" = within 3 days) and can explain its interpretation

---

### Edge Cases

- What happens when a user types a message that doesn't relate to task management? (AI should politely redirect to task-related functions)
- How does the system handle extremely long messages (>1000 characters)? (Truncate or warn user about length limits)
- What happens when OpenAI API is unavailable or rate-limited? (Show user-friendly error and suggest retry)
- How does the system handle simultaneous requests from the same user? (Queue requests or handle concurrently with proper database locking)
- What happens when a user refers to "my task" but has 20 tasks? (AI should ask for clarification or show a list to choose from)
- How does the system handle profanity or inappropriate content in task titles? (Allow it - user's personal space, but sanitize for XSS)
- What happens when a user tries to create a task with a past due date? (Allow it - user might be recording something they already needed to do)
- How does conversation history handle very long conversations (>100 messages)? (Only load last 20 for context, but display all in UI with pagination)

## Requirements

### Functional Requirements

#### Frontend Requirements (Phase-III-AI-Chatbot/frontend/)

- **FR-001**: System MUST implement OpenAI ChatKit UI component in a full-screen chat layout with a conversation history sidebar
- **FR-002**: System MUST display conversation threads with user messages and AI responses, including timestamps and role indicators
- **FR-003**: System MUST support real-time message streaming with typing indicators to show AI response progress
- **FR-004**: System MUST reuse JWT authentication from Phase II and pass tokens to ChatKit for API authentication
- **FR-005**: System MUST display tool call executions visually with status indicators (e.g., "✓ Added task: Buy groceries")
- **FR-006**: System MUST render markdown in AI responses for rich text formatting
- **FR-007**: System MUST be responsive for mobile and desktop screen sizes
- **FR-008**: Users MUST be able to create new conversations and select existing conversations from a sidebar
- **FR-009**: System MUST provide a message input field with send button and Enter key support
- **FR-010**: System MUST show loading states and typing indicators during message processing

#### Backend Requirements (Phase-III-AI-Chatbot/backend/)

- **FR-011**: System MUST create POST /api/chat endpoint that accepts message and conversation_id
- **FR-012**: System MUST validate JWT tokens on every chat API request using Phase II authentication
- **FR-013**: System MUST initialize OpenAI Agents SDK with system prompt configured for task management persona
- **FR-014**: System MUST register 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) with the agent
- **FR-015**: System MUST execute MCP tool calls based on agent decisions and return structured results
- **FR-016**: System MUST support streaming responses via Server-Sent Events for real-time message delivery
- **FR-017**: System MUST implement rate limiting of 30 requests per minute per user on the chat endpoint
- **FR-018**: System MUST retry failed OpenAI API calls with exponential backoff (max 3 retries)
- **FR-019**: System MUST create GET /api/conversations endpoint to list user's conversations

#### MCP Tool Requirements

- **FR-020**: add_task tool MUST accept title (required, 1-200 chars), description (optional), and due_date (optional, ISO8601 format)
- **FR-021**: add_task tool MUST validate that due_date is in the future if provided
- **FR-022**: add_task tool MUST create task in database scoped to authenticated user and return task object with id
- **FR-023**: list_tasks tool MUST accept status filter ('complete'|'incomplete'|'all', default 'all'), limit (default 50, max 100), and offset (default 0)
- **FR-024**: list_tasks tool MUST query user's tasks with filtering and return array of task objects with full metadata
- **FR-025**: complete_task tool MUST accept task_id and completed boolean, and validate task belongs to user
- **FR-026**: complete_task tool MUST update task completion status and return updated task object
- **FR-027**: delete_task tool MUST accept task_id, validate ownership, and remove task from database
- **FR-028**: delete_task tool MUST return success confirmation with deleted task_id
- **FR-029**: update_task tool MUST accept task_id and at least one of title, description, or due_date
- **FR-030**: update_task tool MUST validate task ownership and update only provided fields (partial update)
- **FR-031**: All MCP tools MUST return structured error responses with success field and error message for failures
- **FR-032**: All MCP tools MUST validate inputs using Pydantic models before execution

#### Database Requirements

- **FR-033**: System MUST extend PostgreSQL schema with conversations table (id, user_id, title, created_at, updated_at, metadata)
- **FR-034**: System MUST extend PostgreSQL schema with messages table (id, conversation_id, role, content, tool_calls, created_at)
- **FR-035**: conversations table MUST have foreign key to users table with CASCADE delete
- **FR-036**: messages table MUST have foreign key to conversations table with CASCADE delete
- **FR-037**: System MUST create indexes on user_id, conversation_id, and created_at for query performance
- **FR-038**: System MUST auto-generate conversation title from first user message (first 50 chars + "..." if longer)
- **FR-039**: System MUST persist all user and assistant messages immediately after exchange
- **FR-040**: System MUST store tool_calls as JSONB in messages table for audit trail

#### Conversation Management Requirements

- **FR-041**: System MUST load last 20 messages from conversation history when resuming a conversation
- **FR-042**: System MUST support multiple concurrent conversations per user
- **FR-043**: System MUST create new conversation automatically when user sends first message without conversation_id
- **FR-044**: System MUST update conversation.updated_at timestamp on every new message
- **FR-045**: System MUST scope all conversation queries by user_id to prevent cross-user data access

#### Architecture Requirements

- **FR-046**: System MUST maintain stateless server design with no in-memory conversation state
- **FR-047**: System MUST persist all conversation state to PostgreSQL database
- **FR-048**: System MUST support horizontal scaling (any backend instance can handle any request)
- **FR-049**: System MUST configure database connection pooling with 20 connections max
- **FR-050**: System MUST use async/await throughout backend for non-blocking operations

#### Error Handling Requirements

- **FR-051**: System MUST gracefully degrade when OpenAI API is unavailable, showing user-friendly error message
- **FR-052**: System MUST sanitize user messages before storage to prevent XSS attacks
- **FR-053**: System MUST log all errors with conversation context for debugging
- **FR-054**: System MUST handle partial tool execution failures and report specific errors to user
- **FR-055**: System MUST validate all tool call inputs to prevent SQL injection and other attacks

### Key Entities

- **Conversation**: Represents a chat session between user and AI, contains title (auto-generated from first message), creation/update timestamps, user ownership, and optional metadata (JSONB for extensibility)

- **Message**: Represents a single message in a conversation, contains role (user/assistant/system), text content, optional tool_calls (JSONB storing MCP tool invocations and results), and creation timestamp

- **Task** (from Phase II): Existing entity for todo items, contains title, description, completion status, due date, user ownership, and timestamps. Referenced by MCP tools but not modified in schema.

- **User** (from Phase II): Existing entity for authentication, contains email, hashed password, and timestamps. Used for conversation and task ownership.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create tasks using natural language in under 5 seconds from typing to confirmation
- **SC-002**: AI correctly interprets and executes task operations (add, list, complete, delete, update) with 90%+ accuracy on common requests
- **SC-003**: Chat API responds to user messages in under 3 seconds (p95 latency) including AI processing and tool execution
- **SC-004**: System handles 100 concurrent users without response time degradation beyond 10%
- **SC-005**: Conversation history persists correctly across browser sessions with 100% data retention
- **SC-006**: Zero cross-user data leakage - users only see their own tasks and conversations in all scenarios
- **SC-007**: System remains operational with 99.9% uptime for chat endpoint over a 30-day period
- **SC-008**: Natural language task creation reduces average task entry time by 60% compared to Phase II form-based approach
- **SC-009**: 80% of users successfully complete at least one full task workflow (create, view, complete) through conversation on first attempt
- **SC-010**: Parallel agent implementation reduces development time by 40% compared to sequential development approach

### Parallel Implementation Success

- **SC-011**: Backend (chatbot-architect agent) and Frontend (chatbot-frontend-expert agent) can be developed concurrently without blocking dependencies
- **SC-012**: API contract (chat endpoint schema) is defined upfront and remains stable throughout parallel development
- **SC-013**: Both agents complete their work within the same timeframe (neither waits more than 20% of total time for the other)
- **SC-014**: Integration testing between frontend and backend requires minimal fixes (< 5% of development time)

## Parallel Agent Execution Strategy

**CRITICAL IMPLEMENTATION REQUIREMENT**: During the implementation phase (`/sp.implement`), use parallel agent execution for maximum efficiency.

### Backend Implementation (chatbot-architect agent)

The `chatbot-architect` agent will handle all backend work:

- Database schema extensions (conversations and messages tables with indexes)
- MCP tools implementation (all 5 tools: add_task, list_tasks, complete_task, delete_task, update_task)
- OpenAI Agents SDK integration (agent initialization, system prompts, tool registration)
- Chat API endpoint with streaming support (POST /api/chat with SSE)
- Conversation state management (load/save messages, conversation CRUD)
- Backend error handling and logging (retry logic, rate limiting, error responses)

### Frontend Implementation (chatbot-frontend-expert agent)

The `chatbot-frontend-expert` agent will handle all frontend work:

- OpenAI ChatKit component integration (installation, configuration, theming)
- Chat page and conversation UI (full-screen layout, sidebar, message display)
- Message streaming display (real-time updates, typing indicators)
- Tool call visualization (status badges showing AI actions)
- Authentication context integration (JWT token management from Phase II)
- Frontend error handling (connection errors, API failures, user feedback)

### Parallel Execution Pattern

**Implementation Instructions**:

1. **Launch BOTH agents in parallel** using ONE message with TWO Task tool calls
2. `chatbot-architect` handles ALL backend work in `Phase-III-AI-Chatbot/backend/`
3. `chatbot-frontend-expert` handles ALL frontend work in `Phase-III-AI-Chatbot/frontend/`
4. Both agents work concurrently on independent codebases
5. Coordinate only on API contract (chat endpoint request/response schema)
6. Wait for BOTH agents to complete before validation

**API Contract** (define upfront for coordination):

```typescript
// POST /api/chat request
{
  message: string;
  conversation_id?: string;
}

// POST /api/chat response
{
  response: string;
  conversation_id: string;
  tool_calls: Array<{
    tool_name: string;
    result: any;
  }>;
}

// GET /api/conversations response
{
  conversations: Array<{
    id: string;
    title: string;
    updated_at: string;
  }>;
}
```

## Dependencies

### External Dependencies

- OpenAI API key (organization account) configured as OPENAI_API_KEY environment variable
- OpenAI ChatKit npm package (frontend): `npm install @openai/chatkit`
- OpenAI Python package (backend): `pip install openai`
- MCP SDK Python package (backend): `pip install mcp`

### Internal Dependencies

- Phase II JWT authentication system (reuse existing auth models and token validation)
- Phase II task models and database tables (reference for MCP tool operations)
- Phase II user models (for conversation ownership and task scoping)
- Neon PostgreSQL database (extend with new conversations and messages tables)

### Phase II Code References (Do Not Modify)

- JWT token generation and validation functions
- User authentication models and endpoints
- Task models (Task, TaskCreate, TaskUpdate schemas)
- Database configuration and connection management
- Existing users and tasks tables

## Assumptions

1. **OpenAI API Access**: User has valid OpenAI API key with sufficient quota for development and testing
2. **Database Migration**: Alembic is already configured from Phase II and can be used for schema extensions
3. **Authentication**: Phase II JWT authentication is working correctly and can be referenced without modification
4. **Database Connectivity**: Phase III backend will connect to the same PostgreSQL database as Phase II using existing credentials
5. **Deployment Pattern**: Frontend deploys to Vercel and backend to Railway, following Phase II pattern
6. **Cost Management**: OpenAI API costs are acceptable for prototype; production will require usage monitoring and budget alerts
7. **Natural Language Scope**: AI will handle common English task management phrases; non-English support is out of scope for MVP
8. **Task Ownership**: All tasks remain scoped to individual users; no shared tasks or collaboration features
9. **Conversation Privacy**: Conversations are private; no sharing or team collaboration features
10. **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge) with JavaScript enabled; no IE11 support

## Out of Scope

The following items are explicitly excluded from Phase III:

- **Multi-language Support**: AI responses and natural language understanding are English-only
- **Voice Input/Output**: No speech-to-text or text-to-speech capabilities
- **Task Sharing**: No ability to share conversations or tasks with other users
- **Advanced NLP**: No sentiment analysis, tone detection, or advanced linguistic features beyond basic task extraction
- **Mobile Native Apps**: Web-responsive only; no native iOS/Android apps
- **Offline Mode**: Requires internet connection; no offline functionality or PWA features
- **Custom AI Training**: Uses pre-trained OpenAI models; no fine-tuning or custom model training
- **Task Templates**: No predefined task templates or quick actions
- **Integrations**: No integration with external calendars, email, or third-party task managers
- **Analytics Dashboard**: No usage analytics, conversation metrics, or AI performance tracking UI
- **Conversation Export**: No ability to export conversation history or generate reports
- **Multi-modal Input**: No image, file, or link attachments in conversations
- **Scheduled Messages**: No ability to schedule tasks or set recurring reminders through chat
- **Phase II Modification**: Existing Phase II code remains untouched; Phase III is additive only

## Risks and Mitigation

### Risk 1: OpenAI API Rate Limits and Reliability

**Impact**: Medium-High
**Probability**: Medium

**Description**: OpenAI API may hit rate limits during peak usage or experience downtime, blocking all chat functionality.

**Mitigation**:
- Implement exponential backoff retry logic (3 attempts with 2^n second delays)
- Display user-friendly error messages explaining the issue
- Monitor API usage in development to predict production needs
- Set up OpenAI usage alerts at 50%, 75%, and 90% of quota
- Consider implementing request queuing for brief outages

### Risk 2: Cost Management and Budget Overruns

**Impact**: Medium
**Probability**: Medium-High

**Description**: OpenAI API costs could exceed budget expectations, especially with context window loading 20 messages per request.

**Mitigation**:
- Set monthly budget alerts in OpenAI dashboard ($50, $100, $200 thresholds)
- Implement usage tracking per user to identify heavy users
- Limit context window to 20 messages (current requirement) to control token usage
- Monitor average cost per conversation and adjust context window if needed
- Consider implementing daily per-user request limits (e.g., 100 messages/day) if costs spike

### Risk 3: Complex Query Understanding Limitations

**Impact**: Medium
**Probability**: High

**Description**: AI may struggle with complex temporal queries ("tasks from last week"), ambiguous references ("my task"), or implicit requests.

**Mitigation**:
- Start with simple, explicit patterns (add, list, complete, delete) for P1/P2 stories
- Implement explicit fallback responses: "I couldn't understand that. Try asking me to add, show, complete, or delete a task."
- Provide example prompts in UI (suggestion chips: "Show my tasks", "Add a task", "Mark task 3 done")
- Expand natural language capabilities iteratively based on user testing and feedback
- Log unrecognized queries to identify common patterns for future training

### Risk 4: Database Migration Complexity

**Impact**: Medium
**Probability**: Low

**Description**: Adding conversations and messages tables could conflict with existing schema or cause migration failures.

**Mitigation**:
- Use Alembic migrations with explicit upgrade/downgrade scripts
- Test migrations locally before production deployment
- Backup database before running production migrations
- Test rollback procedures to ensure safe revert if needed
- Run migrations during low-traffic periods

### Risk 5: Parallel Agent Coordination Challenges

**Impact**: High
**Probability**: Medium

**Description**: Backend and frontend agents working in parallel may misalign on API contract or duplicate work, reducing efficiency gains.

**Mitigation**:
- Define API contract (chat endpoint request/response schema) upfront before parallel work begins
- Document contract in shared specification accessible to both agents
- Implement integration tests early to catch contract mismatches
- Schedule coordination checkpoints at 25%, 50%, 75% completion
- Use feature flags to enable gradual integration testing

## Notes

- Phase III is a completely separate codebase in `Phase-III-AI-Chatbot/` directory with its own frontend and backend subdirectories
- Phase II code serves as reference architecture and authentication provider but should not be modified
- Database is shared between Phase II and Phase III - both connect to the same PostgreSQL instance
- MCP SDK is official Model Context Protocol implementation for standardized AI tool calling
- OpenAI Agents SDK handles natural language understanding and tool orchestration
- OpenAI ChatKit provides pre-built React components for conversational UI
- Stateless architecture is critical for horizontal scaling - server never stores conversation state in memory
- Conversation history is loaded from database on every request - only last 20 messages used for AI context
- Tool calls are logged in JSONB format for debugging and audit trail
- All user input must be sanitized before storage to prevent XSS attacks
- JWT tokens from Phase II authentication system are passed through to Phase III backend
- Rate limiting prevents API abuse - 30 requests/minute per user is reasonable for chat interactions
- Parallel agent execution is a critical implementation strategy documented in Parallel Agent Execution Strategy section
