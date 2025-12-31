# Implementation Plan: Phase II - Full-Stack Web Application

**Branch**: `002-fullstack-web-app` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for transforming Phase I console app into a modern multi-user web application with persistent storage and authentication

## Summary

Phase II transforms the Phase I in-memory Python console application into a full-stack web application with user authentication, persistent database storage, and a responsive frontend interface. The architecture follows spec-driven development (SDD) principles using Claude Code and reusable intelligence (skills and agents) for maximum efficiency.

**Primary Technical Approach**:
- Frontend: Next.js 16+ App Router with TypeScript and Tailwind CSS
- Backend: Python FastAPI with async SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Authentication: JWT-based with bcrypt password hashing

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**: FastAPI 0.115+, Next.js 16+, SQLModel 0.0+, Pydantic 2.10+, python-jose 3.3+, passlib 1.7.4, bcrypt 4.2+
**Storage**: Neon Serverless PostgreSQL with async SQLModel ORM
**Testing**: pytest (Python), Jest/Vitest (TypeScript), Playwright (E2E)
**Target Platform**: Web browsers (desktop, tablet, mobile)
**Project Type**: Full-stack web (frontend + backend)
**Performance Goals**: Task list loads <3s, completion toggle <500ms, 95% API success rate
**Constraints**: JWT token expiration, CORS configuration, responsive breakpoints (320px, 768px, 1024px)
**Scale/Scope**: Single-user authenticated tasks, multi-user data isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Using spec.md as source of truth for all implementations |
| II. Progressive Complexity | ✅ PASS | Builds on Phase I patterns, extends to web stack |
| III. Reusable Intelligence | ✅ PASS | Using nextjs-developer, fastapi-developer, fullstack-developer agents; nextjs-frontend, fastapi-backend, sqlmodel-db, jwt-auth skills |
| IV. AI-First Architecture | ✅ PASS | Designed for future AI integration (Phase III) |
| V. Test-First (NON-NEGOTIABLE) | ✅ PASS | TDD cycle: tests → fail → implement |
| VI. Cloud-Native Ready | ✅ PASS | Neon PostgreSQL, container-ready FastAPI |
| VII. Modular Design | ✅ PASS | Separated frontend/backend, reusable components |

**Gate Status**: ✅ PASS - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (inline below)
├── data-model.md        # Phase 1 output (inline below)
├── quickstart.md        # Phase 1 output (inline below)
├── contracts/           # Phase 1 output
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Full-stack web application structure
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # SQLModel database models (User, Task)
│   ├── schemas.py           # Pydantic schemas (request/response)
│   ├── database.py          # Async database connection
│   ├── auth.py              # JWT authentication utilities
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # /auth/register, /auth/login endpoints
│       └── tasks.py         # /api/{user_id}/tasks CRUD endpoints
├── alembic/                 # Database migrations
├── requirements.txt
├── .env                     # Environment variables (NEVER commit)
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_models.py
    │   ├── test_schemas.py
    │   └── test_auth.py
    └── integration/
        └── test_api.py

frontend/
├── src/
│   ├── app/                 # Next.js 16 App Router
│   │   ├── layout.tsx       # Root layout with providers
│   │   ├── page.tsx         # Home page (login/redirect)
│   │   ├── globals.css      # Tailwind CSS
│   │   ├── tasks/
│   │   │   ├── page.tsx     # Task list page
│   │   │   ├── new/
│   │   │   │   └── page.tsx # Create task page
│   │   │   └── [id]/
│   │   │       ├── page.tsx         # Task detail/edit page
│   │   │       └── edit/
│   │   │           └── page.tsx     # Edit task form
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   └── register/
│   │       └── page.tsx     # Registration page
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Modal.tsx
│   │   └── tasks/
│   │       ├── TaskList.tsx
│   │       ├── TaskItem.tsx
│   │       └── TaskForm.tsx
│   └── lib/
│       ├── api.ts           # API client with auth
│       ├── auth.ts          # Auth utilities
│       └── hooks.ts         # React hooks
├── package.json
├── tailwind.config.ts
├── next.config.js
├── .env.local               # Environment variables (NEVER commit)
└── tests/
    ├── unit/
    │   └── components/
    │       └── *.test.tsx
    └── e2e/
        └── *.spec.ts
```

**Structure Decision**: Full-stack web application with separate `backend/` and `frontend/` directories. Backend uses Python/FastAPI with SQLModel for database operations. Frontend uses Next.js 16 App Router with TypeScript and Tailwind CSS. Tests organized as unit, integration, and E2E.

---

# Phase 0: Research

## Research Findings

### R1: Next.js 16 App Router Best Practices

**Decision**: Use Next.js 16 App Router with React Server Components (RSC) for data fetching, Client Components for interactivity.

**Rationale**:
- RSC reduces bundle size by rendering on server
- Better SEO for task lists (future enhancement)
- Built-in streaming and Suspense support
- Native support for layouts and nested routes

**Patterns from nextjs-frontend skill**:
- `'use client'` directive for interactive components
- Server Components for initial data fetch
- Client Components for forms and state management
- Tailwind CSS for responsive design

### R2: FastAPI Async Database Operations

**Decision**: Use SQLModel with async engine (`create_async_engine`) and `AsyncSession` for all database operations.

**Rationale**:
- Better concurrency handling for web requests
- Compatible with modern async Python patterns
- Native SQLModel support for async operations
- Neon PostgreSQL fully supports async connections

**Patterns from sqlmodel-db skill**:
- Async session factory with `expire_on_commit=False`
- Dependency injection for `get_db()` sessions
- Proper error handling with SQLModel exceptions
- Indexing strategy for user_id and completed fields

### R3: JWT Authentication Implementation

**Decision**: Use `python-jose` for JWT operations, `passlib` with bcrypt for password hashing, HTTPBearer for token extraction.

**Rationale**:
- `python-jose` is the standard JWT library for Python
- bcrypt is the most secure password hashing algorithm
- HTTPBearer integrates with FastAPI security
- JWT allows stateless authentication

**Patterns from jwt-auth skill**:
- 30-minute token expiration with refresh capability
- `sub` claim contains user ID for identification
- Password never stored in plaintext
- Protected routes use `Depends(get_current_user)`

### R4: Neon Serverless PostgreSQL Configuration

**Decision**: Use asyncpg driver with connection pooling (min 5, max 20 connections).

**Rationale**:
- Serverless PostgreSQL has connection limits
- Connection pooling prevents exhaustion
- Async driver maximizes throughput
- Environment-based connection string

---

# Phase 1: Design

## Data Model

### User Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PK, auto-increment | Unique user identifier |
| email | str | UNIQUE, NOT NULL, index | User email (login identifier) |
| hashed_password | str | NOT NULL | bcrypt hashed password |
| name | str | NULL | Display name |
| created_at | datetime | NOT NULL, default=now() | Account creation timestamp |

**Relationships**: One-to-many with Task (user.tasks)

### Task Entity

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | int | PK, auto-increment | Unique task identifier |
| user_id | int | FK → User.id, NOT NULL, index | Owner user ID |
| title | str | NOT NULL, 1≤len≤200 | Task title |
| description | str | NULL, max=1000 | Optional task details |
| completed | bool | NOT NULL, default=false | Completion status |
| created_at | datetime | NOT NULL, default=now() | Creation timestamp |
| updated_at | datetime | NOT NULL, default=now() | Last update timestamp |

**Relationships**: Many-to-one with User (task.user)

### Composite Indexes

```sql
-- Optimize task list queries (user_id + created_at)
CREATE INDEX idx_tasks_user_created ON tasks (user_id, created_at DESC);

-- Optimize completion toggle queries (user_id + completed)
CREATE INDEX idx_tasks_user_completed ON tasks (user_id, completed);
```

### Data Model Diagram

```
┌─────────────────────────────────────┐
│              User                   │
├─────────────────────────────────────┤
│ id: PK (int)                        │
│ email: UNIQUE, INDEX (str)          │
│ hashed_password: NOT NULL (str)     │
│ name: NULL (str)                    │
│ created_at: NOT NULL (datetime)     │
└─────────────────────────────────────┘
                 │
                 │ 1:n
                 ▼
┌─────────────────────────────────────┐
│              Task                   │
├─────────────────────────────────────┤
│ id: PK (int)                        │
│ user_id: FK → User.id, INDEX (int)  │
│ title: NOT NULL, 1-200 (str)        │
│ description: NULL, max-1000 (str)   │
│ completed: NOT NULL (bool)          │
│ created_at: NOT NULL (datetime)     │
│ updated_at: NOT NULL (datetime)     │
└─────────────────────────────────────┘
```

## API Contracts

### Authentication Endpoints

#### POST /auth/register

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (201 Created)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors**:
- 400: Email already registered
- 422: Validation error

#### POST /auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors**:
- 401: Invalid credentials
- 422: Validation error

### Task Endpoints (All require Authorization: Bearer <token>)

#### GET /api/{user_id}/tasks

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "title": "Complete Phase II",
    "description": "Finish full-stack implementation",
    "completed": false,
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z"
  }
]
```

**Errors**:
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (accessing another user's tasks)
- 404: User not found

#### POST /api/{user_id}/tasks

**Request**:
```json
{
  "title": "New task title",
  "description": "Optional description"
}
```

**Response (201 Created)**: Same as GET response

**Errors**:
- 400: Title empty or >200 chars, description >1000 chars
- 401/403/404: As above

#### GET /api/{user_id}/tasks/{task_id}

**Response (200 OK)**: Single task object

**Errors**:
- 401/403/404: As above (plus 404 if task not found)

#### PUT /api/{user_id}/tasks/{task_id}

**Request** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Response (200 OK)**: Updated task object

**Errors**:
- 400: Validation error
- 401/403/404: As above

#### DELETE /api/{user_id}/tasks/{task_id}

**Response (204 No Content)**: Empty body

**Errors**:
- 401/403/404: As above

#### PATCH /api/{user_id}/tasks/{task_id}/complete

**Response (200 OK)**: Updated task with toggled completed status

**Errors**:
- 401/403/404: As above

### OpenAPI Specification

See [contracts/openapi.yaml](./contracts/openapi.yaml) for complete OpenAPI 3.0 specification.

## Quickstart Guide

### Prerequisites

```bash
# Backend
python3.13+
pip install -r backend/requirements.txt

# Frontend
node18+
npm install --prefix frontend
```

### Environment Setup

**Backend (.env)**:
```bash
DATABASE_URL="postgresql+asyncpg://user:pass@host/dbname?sslmode=require"
SECRET_KEY="your-super-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM="HS256"
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Running Development Servers

**Backend**:
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm run dev
```

### Database Setup

```bash
cd backend
alembic upgrade head  # Run migrations
```

### Testing

**Backend**:
```bash
cd backend
pytest -v
```

**Frontend**:
```bash
cd frontend
npm test
npm run test:e2e  # Playwright
```

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | All design decisions align with constitutional principles | N/A |

---

## Next Steps

1. **Run `/sp.tasks`** to generate implementation tasks from this plan
2. **Execute tasks** in dependency order using the fullstack-developer agent
3. **Follow TDD cycle**: Write tests → Verify fail → Implement → Verify pass
4. **Update agents** as needed using `.specify/scripts/bash/update-agent-context.sh`

---

**Plan Generated**: 2025-12-28
**Using Reusable Intelligence**:
- Skills: nextjs-frontend, fastapi-backend, sqlmodel-db, jwt-auth
- Agents: nextjs-developer, fastapi-developer, fullstack-developer
