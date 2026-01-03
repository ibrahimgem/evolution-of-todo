# Data Model: AI-Powered Todo Chatbot

**Feature**: 003-ai-chatbot
**Date**: 2026-01-01
**Database**: PostgreSQL (Neon Serverless) - extends Phase II schema

## Entity Overview

This feature extends the existing Phase II database with two new tables for conversation management. Existing tables (users, tasks) are referenced but not modified.

## Entities

### Conversation

**Purpose**: Represents a chat session between a user and the AI assistant

**Attributes**:
- `id` (SERIAL PRIMARY KEY): Unique conversation identifier
- `user_id` (INTEGER, FOREIGN KEY → users.id): Owner of the conversation
- `title` (VARCHAR(200)): Auto-generated from first user message
- `created_at` (TIMESTAMP): When conversation was created
- `updated_at` (TIMESTAMP): Last message timestamp
- `metadata` (JSONB): Extensible field for conversation settings, context, or future features

**Relationships**:
- Belongs to User (many conversations per user)
- Has many Messages (one conversation has many messages)

**Validation Rules**:
- user_id must reference existing user
- title auto-generated: first 50 chars of first message + "..." if longer
- created_at defaults to NOW() on creation
- updated_at defaults to NOW(), updated on every new message
- metadata defaults to empty object `{}`

**State Transitions**:
- Created: When user sends first message without conversation_id
- Updated: On every new message (updates updated_at timestamp)
- Deleted: When user deletes conversation (CASCADE deletes all messages)

**Business Rules**:
- Users can only access their own conversations
- Conversations with zero messages should not exist (first message creates conversation)
- Conversations are soft-deletable via metadata flag (future enhancement)

---

### Message

**Purpose**: Represents a single message in a conversation (user input, AI response, or system message)

**Attributes**:
- `id` (SERIAL PRIMARY KEY): Unique message identifier
- `conversation_id` (INTEGER, FOREIGN KEY → conversations.id): Parent conversation
- `role` (VARCHAR(20), CHECK IN ('user', 'assistant', 'system')): Message sender type
- `content` (TEXT): Message text content
- `tool_calls` (JSONB, NULLABLE): Stores MCP tool invocations and results
- `created_at` (TIMESTAMP): When message was sent/received

**Relationships**:
- Belongs to Conversation (many messages per conversation)

**Validation Rules**:
- conversation_id must reference existing conversation
- role must be one of: 'user', 'assistant', 'system'
- content can be null for messages that only contain tool_calls
- tool_calls structure: `{tool_name: string, arguments: object, result: object}`
- created_at defaults to NOW() on creation

**State Transitions**:
- Created: When user sends message or AI responds
- Immutable: Messages are never updated after creation (append-only log)
- Deleted: Only via CASCADE when parent conversation is deleted

**Business Rules**:
- Messages are append-only (never edited)
- Tool calls are logged for audit trail
- Message order determined by created_at (ascending)
- Only last 20 messages loaded for AI context window

---

### Task (Phase II - Reference Only)

**Purpose**: Represents a todo item (existing entity from Phase II)

**Attributes**:
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY → users.id)
- `title` (VARCHAR(200), NOT NULL)
- `description` (TEXT, NULLABLE)
- `completed` (BOOLEAN, DEFAULT FALSE)
- `due_date` (TIMESTAMP, NULLABLE)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Relationships**:
- Belongs to User
- Referenced by MCP tools (no schema changes)

**Usage in Phase III**:
- MCP tools query/modify tasks
- No schema modifications
- All operations scoped to user_id from JWT

---

### User (Phase II - Reference Only)

**Purpose**: Represents an authenticated user (existing entity from Phase II)

**Attributes**:
- `id` (SERIAL PRIMARY KEY)
- `email` (VARCHAR(255), UNIQUE, NOT NULL)
- `hashed_password` (VARCHAR(255), NOT NULL)
- `created_at` (TIMESTAMP)

**Relationships**:
- Has many Tasks
- Has many Conversations (new in Phase III)

**Usage in Phase III**:
- JWT tokens contain user_id
- Conversations scoped by user_id
- No schema modifications

---

## Relationships Diagram

```
┌─────────────┐
│    User     │ (Phase II - no changes)
│  (Phase II) │
└──────┬──────┘
       │
       │ 1:N (existing)
       │
       ▼
┌─────────────┐       ┌──────────────────┐
│    Task     │       │  Conversation    │ (NEW)
│  (Phase II) │       │   (Phase III)    │
└─────────────┘       └────────┬─────────┘
                               │
                               │ 1:N
                               │
                               ▼
                      ┌──────────────────┐
                      │     Message      │ (NEW)
                      │   (Phase III)    │
                      └──────────────────┘
```

**Relationships**:
- User → Conversation (1:N): One user has many conversations
- User → Task (1:N): One user has many tasks (Phase II)
- Conversation → Message (1:N): One conversation has many messages

## Database Migration Strategy

### Migration File Structure

```
Phase-III-AI-Chatbot/backend/alembic/versions/
└── 001_add_conversations_and_messages.py
```

### Migration Content

**Upgrade**:
1. Create conversations table
2. Create messages table
3. Add foreign keys (users → conversations, conversations → messages)
4. Create indexes (user_id, conversation_id, created_at)

**Downgrade**:
1. Drop indexes
2. Drop messages table (CASCADE handles foreign keys)
3. Drop conversations table (CASCADE handles foreign keys)

### Testing Strategy

- Run migration on local development database
- Verify tables created with correct schema
- Test foreign key constraints (CASCADE delete)
- Verify indexes created
- Test rollback procedure
- Backup production database before production migration

## Query Patterns

### Common Queries

**Get user's conversations**:
```sql
SELECT * FROM conversations
WHERE user_id = ?
ORDER BY updated_at DESC
LIMIT 50;
```

**Load conversation history**:
```sql
SELECT * FROM messages
WHERE conversation_id = ?
ORDER BY created_at ASC
LIMIT 20;
```

**Create new conversation**:
```sql
INSERT INTO conversations (user_id, title)
VALUES (?, ?)
RETURNING *;
```

**Save message**:
```sql
INSERT INTO messages (conversation_id, role, content, tool_calls)
VALUES (?, ?, ?, ?);

UPDATE conversations
SET updated_at = NOW()
WHERE id = ?;
```

## Data Integrity Rules

1. **User Isolation**: All queries MUST filter by user_id from JWT token
2. **Cascade Deletes**: Deleting conversation removes all messages
3. **Referential Integrity**: Foreign keys enforce valid relationships
4. **Append-Only Messages**: Messages never updated after creation
5. **Transaction Safety**: Message saves wrapped in transactions
6. **Index Usage**: All user/conversation queries use indexes
7. **JSONB Validation**: tool_calls validated before storage
8. **Timestamp Accuracy**: All timestamps use UTC timezone

## Performance Considerations

- **Indexes**: Ensure fast lookups on user_id, conversation_id, created_at
- **Connection Pooling**: Limit to 20 concurrent connections
- **Query Limits**: Always use LIMIT on conversation/message queries
- **JSONB Performance**: tool_calls stored as JSONB for flexibility without schema changes
- **Pagination**: Large conversation lists paginated (50 per page)
- **History Truncation**: Only load last 20 messages for AI context

## Security Considerations

- **User Scoping**: All queries filtered by user_id from authenticated token
- **SQL Injection**: Use parameterized queries (SQLModel handles this)
- **XSS Prevention**: Sanitize message content before storage
- **Data Isolation**: No cross-user data access via foreign keys
- **Audit Trail**: tool_calls provide audit log of AI actions
