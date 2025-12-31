---
title: Todo FastAPI Backend
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Todo App - FastAPI Backend

A modern, high-performance REST API for task management built with FastAPI, SQLModel, and PostgreSQL.

## Features

- **JWT Authentication**: Secure user authentication with token-based auth
- **Task Management**: Full CRUD operations for tasks
- **PostgreSQL Database**: Async SQLModel ORM with Neon serverless database
- **Error Handling**: Comprehensive error handling with structured responses
- **API Documentation**: Auto-generated OpenAPI docs at `/docs`
- **Health Check**: Endpoint at `/health` for monitoring

## Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql+asyncpg://user:pass@host/db`)
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: JWT algorithm (default: `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: `30`)

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get access token

### Tasks
- `GET /tasks/` - Get all tasks for current user
- `POST /tasks/` - Create new task
- `GET /tasks/{id}` - Get task by ID
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Health
- `GET /health` - Health check endpoint

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload --port 8000
```

## Deployment

This app is configured for deployment on Hugging Face Spaces with Docker.

### Environment Setup

Set these secrets in your Hugging Face Space:

1. `DATABASE_URL` - Your Neon PostgreSQL connection string
2. `SECRET_KEY` - A secure random string for JWT signing
3. `ALGORITHM` - JWT algorithm (HS256)
4. `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

## Tech Stack

- **FastAPI** 0.115+ - Modern, fast web framework
- **SQLModel** 0.0+ - ORM with Pydantic integration
- **Pydantic** 2.10+ - Data validation
- **python-jose** 3.3+ - JWT token handling
- **passlib** 1.7.4 - Password hashing
- **bcrypt** 4.2+ - Secure password hashing
- **PostgreSQL** - Neon serverless database

## License

MIT
