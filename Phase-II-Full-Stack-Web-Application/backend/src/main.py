from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError
from datetime import datetime, timezone
from .routes.auth import router as auth_router
from .routes.tasks import router as tasks_router
from .database import create_db_and_tables, close_db
from .schemas import ErrorResponse
from .exceptions import BusinessException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    logger.info("Starting up the application...")
    await create_db_and_tables()
    yield
    # Shutdown: cleanup
    logger.info("Shutting down the application...")
    await close_db()

app = FastAPI(
    title="Evolution of Todo API",
    version="1.0.0",
    description="A robust and scalable todo management API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
]

allowed_headers = [
    "Accept",
    "Accept-Language",
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Origin",
    "Cache-Control",
    "Pragma",
    "DNT",
    "User-Agent",
    "X-Custom-Header"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=allowed_headers,
    expose_headers=["Content-Length", "Content-Type"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "*.vercel.app"]
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            message="Invalid request data",
            code="VALIDATION_ERROR",
            details={"errors": exc.errors()}
        ).model_dump()
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    logger.error(f"Database integrity error: {exc}")
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(
            error="Conflict",
            message="Data integrity violation",
            code="DATABASE_INTEGRITY_ERROR"
        ).model_dump()
    )

@app.exception_handler(SQLAlchemyError)
@app.exception_handler(DBAPIError)
async def database_error_handler(request, exc):
    # Log specific error for internal debugging but return sanitized message
    logger.error(f"Database error: {type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Database Error",
            message="A database error occurred",
            code="DATABASE_ERROR"
        ).model_dump()
    )

@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc: BusinessException):
    logger.warning(f"Business error: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Business Error",
            message=exc.message,
            code=exc.error_code
        ).model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=str(exc.detail),
            code=f"HTTP_{exc.status_code}"
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    )

# Include the routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "todo-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Evolution of Todo API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
