from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from .database import get_db
from .models import User
from .exceptions import BusinessException
import os
import secrets
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # In production, we should fail if SECRET_KEY is not set
    if os.getenv("ENV") == "production":
        logger.critical("SECRET_KEY must be set in production environment")
        raise RuntimeError("SECRET_KEY must be set in production environment")

    # Generate a secure secret key for development
    SECRET_KEY = secrets.token_urlsafe(32)
    logger.info("Generated temporary SECRET_KEY for development")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# HTTP Bearer security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {type(e).__name__}")
        return False

def hash_password(password: str) -> str:
    if not password or len(password) < 8:
        raise BusinessException(
            message="Password must be at least 8 characters long",
            error_code="PASSWORD_TOO_SHORT",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise BusinessException(
            message="Failed to secure password",
            error_code="HASHING_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT encoding error: {str(e)}")
        raise BusinessException(
            message="Failed to create session token",
            error_code="TOKEN_CREATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        error_msg = str(e)
        if "Signature has expired" in error_msg:
            raise BusinessException(
                message="Session has expired. Please log in again.",
                error_code="TOKEN_EXPIRED",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        logger.warning(f"Invalid token attempt: {error_msg}")
        raise BusinessException(
            message="Invalid session credentials",
            error_code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id_str = payload.get("sub")

        if user_id_str is None:
            raise BusinessException(
                message="Invalid session information",
                error_code="INVALID_PAYLOAD",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        user_id = int(user_id_str)

        statement = select(User).where(User.id == user_id)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User {user_id} not found from valid token")
            raise BusinessException(
                message="Account not found",
                error_code="USER_NOT_FOUND",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return user

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise BusinessException(
            message="Authentication failed",
            error_code="AUTH_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    # Future enhancement: check for deactivated accounts
    return current_user
