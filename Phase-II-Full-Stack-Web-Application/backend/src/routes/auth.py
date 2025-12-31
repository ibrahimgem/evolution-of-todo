from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta
from ..database import get_db
from ..models import User, UserCreate, UserLogin, UserResponse
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..exceptions import BusinessException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    """
    try:
        # Enhanced input validation
        email = user_data.email.strip().lower()
        if not email or "@" not in email:
            raise BusinessException(
                message="Invalid email address",
                error_code="INVALID_EMAIL",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        name = user_data.name.strip() if user_data.name else None
        if name and len(name) > 50:
            raise BusinessException(
                message="Name must be 50 characters or less",
                error_code="NAME_TOO_LONG",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        password = user_data.password
        if not password or len(password) < 8:
            raise BusinessException(
                message="Password must be at least 8 characters long",
                error_code="PASSWORD_TOO_SHORT",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {email}")
            raise BusinessException(
                message="Email already registered",
                error_code="EMAIL_ALREADY_REGISTERED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Hash the password
        hashed_password = hash_password(password)

        # Create new user
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create access token
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        logger.info(f"User {user.id} registered successfully")
        return {"access_token": access_token, "token_type": "bearer"}

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise BusinessException(
            message="Failed to register user",
            error_code="REGISTRATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    try:
        # Enhanced input validation
        email = credentials.email.strip().lower()
        password = credentials.password

        if not email or "@" not in email:
            raise BusinessException(
                message="Invalid email address",
                error_code="INVALID_EMAIL",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            raise BusinessException(
                message="Password is required",
                error_code="PASSWORD_REQUIRED",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {email}")
            raise BusinessException(
                message="Incorrect email or password",
                error_code="INVALID_CREDENTIALS",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        # Create access token
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        logger.info(f"User {user.id} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}

    except BusinessException:
        raise
    except Exception as e:
        logger.error(f"Error during user login: {str(e)}")
        raise BusinessException(
            message="Failed to authenticate user",
            error_code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    }
