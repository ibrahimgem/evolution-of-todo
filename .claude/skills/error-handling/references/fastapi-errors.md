# FastAPI Error Handling Patterns

## Standard Error Response Schema

Every error response should follow a consistent structure to help the frontend handle them predictably.

```python
from pydantic import BaseModel
from typing import Optional, Any

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    code: str
    details: Optional[Any] = None
```

## Global Exception Handlers

Register global handlers in `main.py` to catch unhandled exceptions and return consistent JSON responses.

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER__ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred.",
            "code": "INTERNAL_SERVER_ERROR"
        }
    )
```

## Custom Business Exceptions

Define custom exceptions for business logic failures (e.g., `TaskNotFound`, `InvalidPermissions`).

```python
class BusinessException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "code": exc.code
        }
    )
```
