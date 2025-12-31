---
id: 3
title: Implement robust error handling across full-stack application
stage: green
date_iso: 2025-12-30
surface: agent
model: claude-sonnet-4.5-20250929
feature: 002-fullstack-web-app
branch: 002-fullstack-web-app
user: apple
command: none
labels: ["error-handling", "observability", "resilience"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - Phase-II-Full-Stack-Web-Application/backend/src/main.py
  - Phase-II-Full-Stack-Web-Application/backend/src/schemas.py
  - Phase-II-Full-Stack-Web-Application/backend/src/auth.py
  - Phase-II-Full-Stack-Web-Application/backend/src/routes/tasks.py
  - Phase-II-Full-Stack-Web-Application/backend/src/routes/auth.py
  - Phase-II-Full-Stack-Web-Application/frontend/src/lib/api.ts
  - Phase-II-Full-Stack-Web-Application/frontend/src/app/tasks/page.tsx
  - Phase-II-Full-Stack-Web-Application/frontend/src/app/layout.tsx
  - Phase-II-Full-Stack-Web-Application/frontend/src/components/common/ErrorBoundary.tsx
tests_yaml:
  - Manual verification of exception handlers
---

## Prompt
I need you to implement robust error handling across the entire application based on the audit report.

### CRITICAL TASKS:

1. **Backend (FastAPI)**:
    - Standardize error response shape in `main.py` using the `ErrorResponse` pydantic model for all exception handlers.
    - Implement global exception handlers for `SQLAlchemyError` and `DBAPIError` to prevent database credential leaks.
    - Add structured logging throughout `/routes/auth.py` and `/routes/tasks.py`.
    - Create a custom `BusinessException` class to handle common failures like "Task not found" or "Unauthorized" with specific error codes.

2. **Frontend (Next.js)**:
    - Update `lib/api.ts` to properly parse JSON error responses and throw structured errors.
    - Add `AbortController` support to `lib/api.ts` and use it in `app/tasks/page.tsx` to prevent race conditions and memory leaks.
    - Implement an `ErrorBoundary` component and wrap the root layout in `app/layout.tsx`.
    - Fix all 'naked' catch blocks in `ThemeContext.tsx` and `lib/auth.ts` to properly handle failure modes.

3. **Security**:
    - Ensure database connection strings are never leaked in logs.
    - Sanitize all error messages returned to the client.

Please follow the `error-handling` skill patterns and the priority list from the audit report. Provide clear diffs for the changes.

## Response
I have implemented a comprehensive error handling layer across both the backend and frontend.

Key changes:
- Created `ErrorResponse` model for consistent API error shapes.
- Introduced `BusinessException` in FastAPI for domain-specific errors.
- Added global handlers for database errors to prevent sensitive data leaks.
- Enhanced `lib/api.ts` with `AbortController` support and structured `ApiRequestError`.
- Added a global `ErrorBoundary` in Next.js.
- Implemented structured logging in all API routes.

## Outcome
The application is now resilient to common failure modes, provides clear feedback to users, and maintains security by masking internal database errors.
