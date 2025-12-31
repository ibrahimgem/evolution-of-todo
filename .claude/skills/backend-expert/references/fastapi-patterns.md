# FastAPI Project Patterns

## Project Structure

A clean separation of concerns facilitates long-term maintenance.

```text
src/
├── routes/         # APIRouter definitions
├── schemas/        # Pydantic models for validation
├── models/         # SQLModel database tables
├── service/        # Business logic layer
├── auth.py         # Security and JWT logic
├── database.py     # Engine and session setup
└── main.py         # Application entry point
```

## Router Configuration

Use prefix-based routing for modularity.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks():
    ...
```

## Dependency Injection

Leverage FastAPI's dependency injection for database sessions and authentication.

```python
from fastapi import Depends

@app.get("/profile")
async def profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    ...
```
