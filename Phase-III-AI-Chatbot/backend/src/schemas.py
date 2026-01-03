"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any


# Chat request and response schemas
class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000, description="User's message to the AI")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (omit to create new conversation)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Add a task to buy groceries tomorrow",
                    "conversation_id": "123"
                }
            ]
        }
    }


class ToolCall(BaseModel):
    """Schema for tool execution information."""
    tool_name: str = Field(..., description="Name of the MCP tool called")
    result: dict = Field(..., description="Tool execution result")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tool_name": "add_task",
                    "result": {
                        "success": True,
                        "task": {
                            "id": 42,
                            "title": "Buy groceries",
                            "due_date": "2026-01-02T00:00:00Z"
                        }
                    }
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    response: str = Field(..., description="AI's natural language response")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (newly created or existing, None for test mode)")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tools executed by AI during this turn")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "I've added 'Buy groceries' to your tasks for tomorrow.",
                    "conversation_id": "123",
                    "tool_calls": [
                        {
                            "tool_name": "add_task",
                            "result": {
                                "success": True,
                                "task": {
                                    "id": 42,
                                    "title": "Buy groceries",
                                    "due_date": "2026-01-02T00:00:00Z"
                                }
                            }
                        }
                    ]
                }
            ]
        }
    }


# Error response schema (shared with Phase II)
class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[dict] = Field(None, description="Additional error context")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Unauthorized",
                    "message": "Invalid or expired JWT token",
                    "code": "AUTH_ERROR"
                }
            ]
        }
    }


# Conversation list schemas
class ConversationListItem(BaseModel):
    """Schema for conversation list item."""
    id: str
    title: str
    created_at: str
    updated_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123",
                    "title": "Add a task to buy groceries tomorrow...",
                    "created_at": "2026-01-01T10:00:00Z",
                    "updated_at": "2026-01-01T10:15:00Z"
                }
            ]
        }
    }


class ConversationListResponse(BaseModel):
    """Response schema for conversation list."""
    conversations: List[ConversationListItem]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversations": [
                        {
                            "id": "123",
                            "title": "Add a task to buy groceries tomorrow...",
                            "created_at": "2026-01-01T10:00:00Z",
                            "updated_at": "2026-01-01T10:15:00Z"
                        }
                    ],
                    "total": 1
                }
            ]
        }
    }
