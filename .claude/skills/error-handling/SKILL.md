---
name: error-handling
description: Best practices and patterns for full-stack error handling in FastAPI and Next.js applications. Use when implementing global exception handlers, API error responses, error boundaries, or client-side error states.
---

# Full-Stack Error Handling

This skill provides patterns for consistent error treatment across the entire stack.

## Core Strategy

1.  **Fail Fast**: Validate early at system boundaries.
2.  **Consistent Response**: Use a uniform JSON structure for all API errors.
3.  **Client Resilience**: Use Error Boundaries and loading states to prevent app crashes.
4.  **Security**: Avoid leaking stack traces or sensitive environment data in production responses.

## Quick Reference

### Backend (FastAPI)

- See [fastapi-errors.md](references/fastapi-errors.md) for global exception handlers and business logic exceptions.

**Typical Error Structure:**
```json
{
  "success": false,
  "message": "Human readable message",
  "code": "ERROR_SLUG",
  "details": null
}
```

### Frontend (Next.js)

- See [nextjs-errors.md](references/nextjs-errors.md) for Error Boundaries and API response interceptors.

## Common HTTP Status Codes

| Code | Usage |
| :--- | :--- |
| **400** | Bad Request (Validation failure) |
| **401** | Unauthorized (Not logged in) |
| **403** | Forbidden (Logged in, but no permission) |
| **404** | Not Found (Resource doesn't exist) |
| **422** | Unprocessable Entity (Pydantic validation failure) |
| **500** | Internal Server Error (Unexpected crash) |
