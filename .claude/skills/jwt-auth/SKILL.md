---
name: jwt-auth
description: Use when implementing authentication and authorization. Covers JWT token creation/verification, password hashing, protected routes, and user session management for FastAPI applications.
---

# JWT Authentication

## Overview

JWT (JSON Web Token) authentication for securing FastAPI endpoints. Use for user registration, login, password hashing, and protected route access.

## Quick Start

```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Protected Route Dependency

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from database
    user = await db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Usage
@app.get("/api/tasks")
async def list_tasks(current_user: User = Depends(get_current_user)):
    return await db.get_user_tasks(current_user.id)
```

## Auth Endpoints

```python
# routes/auth.py
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(data: UserCreate):
    if await db.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(data.password)
    user = await db.create_user(email=data.email, hashed_password=hashed, name=data.name)

    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
async def login(data: LoginRequest):
    user = await db.get_user_by_email(data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}
```

## Token Refresh

```python
@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token(data={"sub": current_user.id})
    return {"access_token": new_token, "token_type": "bearer"}
```

## Frontend Token Storage

```typescript
// Store token after login
localStorage.setItem('auth_token', response.access_token)

// Attach to API requests
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token')
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    }
  })
}
```

## Security Best Practices

- Use bcrypt for password hashing (never store plain text)
- Set appropriate token expiration (30-60 minutes typical)
- Store secrets in environment variables
- Use HTTPS in production
- Implement token refresh mechanism
- Validate all user input before processing
