"""FastAPI application entry point for Phase III AI Chatbot."""
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError
from datetime import datetime, timezone
from .routes.auth import router as auth_router
from .routes.chat import router as chat_router
from .routes.test import router as test_router
from .routes.health import router as health_router
from .routes.tasks import router as tasks_router
from .database import create_db_and_tables, close_db
from .schemas import ErrorResponse
from .exceptions import BusinessException
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: create database tables
    logger.info("Starting up Phase III AI Chatbot application...")
    await create_db_and_tables()
    logger.info("Database initialized successfully")

    # Register MCP tools
    logger.info("Registering MCP tools...")
    from .mcp.mcp_server import get_mcp_registry
    from .database import get_db

    registry = get_mcp_registry()

    # Import tools
    from .mcp_tools.add_task import add_task, AddTaskInput, TOOL_METADATA as ADD_TASK_META
    from .mcp_tools.list_tasks import list_tasks, ListTasksInput, TOOL_METADATA as LIST_TASKS_META
    from .mcp_tools.complete_task import complete_task, CompleteTaskInput, TOOL_METADATA as COMPLETE_TASK_META
    from .mcp_tools.delete_task import delete_task, DeleteTaskInput, TOOL_METADATA as DELETE_TASK_META
    from .mcp_tools.update_task import update_task, UpdateTaskInput, TOOL_METADATA as UPDATE_TASK_META

    # Registration map: Tool name -> (Handler, InputSchema, Metadata)
    TOOLS_TO_REGISTER = [
        (add_task, AddTaskInput, ADD_TASK_META),
        (list_tasks, ListTasksInput, LIST_TASKS_META),
        (complete_task, CompleteTaskInput, COMPLETE_TASK_META),
        (delete_task, DeleteTaskInput, DELETE_TASK_META),
        (update_task, UpdateTaskInput, UPDATE_TASK_META),
    ]

    for handler, input_schema, meta in TOOLS_TO_REGISTER:
        def make_wrapper(h, schema):
            async def tool_wrapper(arguments: dict, context: dict) -> dict:
                try:
                    obj = schema(**arguments)
                except Exception as e:
                    return {"success": False, "error": f"Invalid input: {str(e)}"}

                async for d in get_db():
                    res = await h(obj, d, context)
                    return res.model_dump()
            return tool_wrapper

        registry.register_tool(
            name=meta["name"],
            description=meta["description"],
            input_schema=meta["input_schema"],
            handler=make_wrapper(handler, input_schema)
        )
        logger.info(f"Registered MCP tool: {meta['name']}")

    logger.info(f"Total MCP tools registered: {registry.tool_count()}")

    yield
    # Shutdown: cleanup
    logger.info("Shutting down the application...")
    await close_db()


app = FastAPI(
    title="AI-Powered Todo Chatbot API",
    version="1.0.0",
    description="Conversational AI interface for task management using OpenAI and MCP",
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

# For development/testing - allow all origins
allow_all_origins = True

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
    allow_origins=["*"] if allow_all_origins else origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"] if allow_all_origins else allowed_headers,
    expose_headers=["Content-Length", "Content-Type"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Allow all hosts for now - restrict in production
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


# Include routers
app.include_router(auth_router, prefix="/api")  # Auth router: /api/auth/*
app.include_router(chat_router, prefix="/api")  # Chat router: /api/chat, /api/conversations/*
app.include_router(tasks_router, prefix="/api")  # Task router: /api/{user_id}/tasks/*
app.include_router(test_router)  # Test router has its own /api/test prefix
app.include_router(health_router)  # Health router: /api/health (for K8s probes)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint that doesn't depend on database.
    This ensures Railway health checks pass even during startup.
    """
    return {
        "status": "healthy",
        "service": "ai-chatbot-api",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the AI-Powered Todo Chatbot API",
        "version": "1.0.0",
        "phase": "Phase III - AI Chatbot",
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
