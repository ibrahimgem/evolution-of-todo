"""Test routes for quick chatbot testing without authentication."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..agent import get_agent_response
from ..schemas import ChatRequest, ChatResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test", tags=["test"])


class TestChatRequest(BaseModel):
    """Test chat request (no auth required)."""
    message: str


@router.post("/chat", response_model=ChatResponse)
async def test_chat(request: TestChatRequest) -> ChatResponse:
    """
    Test chat endpoint - bypasses authentication for quick testing.

    **WARNING**: This is for testing only. Remove in production!

    Uses a mock user_id=999 and no conversation history.
    """
    try:
        # Use mock user ID for testing
        test_user_id = 999

        logger.info(f"Test chat request: {request.message[:50]}...")

        # Get agent response without conversation history
        agent_result = await get_agent_response(
            user_message=request.message,
            conversation_history=[],
            user_id=test_user_id
        )

        if agent_result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"AI agent error: {agent_result['error']}"
            )

        return ChatResponse(
            response=agent_result["response"],
            tool_calls=agent_result.get("tool_calls", []),
            conversation_id=None  # No conversation tracking in test mode
        )

    except Exception as e:
        logger.error(f"Test chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get("/health")
async def test_health():
    """Health check for test routes."""
    return {
        "status": "ok",
        "message": "Test routes are active",
        "warning": "These endpoints bypass authentication - for testing only!"
    }
