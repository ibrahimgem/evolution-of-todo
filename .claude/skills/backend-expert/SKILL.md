---
name: backend-expert
description: Use when building or modifying Python FastAPI backends for web applications. Covers REST API endpoints, Pydantic models, SQLModel integration, JWT authentication middleware, and async database operations.
---

# Backend Expert

This skill provides comprehensive guidance for architecting and implementing modern FastAPI backends.

## Core Capabilities

1.  **FastAPI Architecture**: Designing modular routers, dependency injection systems, and middleware.
2.  **SQLModel & Databases**: Developing async database integrations, relationship modeling, and efficient querying patterns.
3.  **Validation & Serialization**: Creating Pydantic models for strict request validation and response formatting.
4.  **Security**: Implementing JWT-based authentication and granular permission management.

## Technical Patterns

### 1. REST API Design
- Adhere to HTTP method standards (GET, POST, PUT, DELETE, PATCH).
- Use [fastapi-patterns.md](references/fastapi-patterns.md) for project structure and routing.

### 2. Database Integration
- Manage async sessions and model relationships using [sqlmodel-db.md](references/sqlmodel-db.md).
- Use pooled connections for serverless environments.

### 3. Authentication Flow
- Integrate JWT logic and secure password hashing.
- Refer to [auth-flow.md](references/auth-flow.md) for implementation details.

## Deliverables Checklist
- [ ] Modular router configuration
- [ ] Async-compatible database session management
- [ ] Pydantic request/response schemas
- [ ] JWT-protected endpoints
- [ ] Unit and integration tests for service logic
