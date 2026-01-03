"""Chat routes for AI-powered conversational interface."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import logging
import asyncio

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Conversation, Message, get_utc_now
from ..schemas import ChatRequest, ChatResponse, ToolCall, ErrorResponse
from ..agent import get_agent_response
from ..exceptions import BusinessException

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Simple in-memory rate limiting (Replace with Redis/Redis-based slowapi in production)
# Key: user_id, Value: List of timestamps of requests in the last minute
user_rate_limit: Dict[int, List[datetime]] = {}
RATE_LIMIT_PER_MINUTE = 30

def check_rate_limit(user_id: int):
    """Check if user has exceeded the rate limit."""
    now = datetime.now(timezone.utc)
    if user_id not in user_rate_limit:
        user_rate_limit[user_id] = [now]
        return

    # Filter timestamps older than 1 minute
    user_rate_limit[user_id] = [ts for ts in user_rate_limit[user_id] if now - ts < timedelta(minutes=1)]

    if len(user_rate_limit[user_id]) >= RATE_LIMIT_PER_MINUTE:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise BusinessException(
            message="Rate limit exceeded. Please try again after a minute.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    user_rate_limit[user_id].append(now)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Send message to AI chatbot.

    Process user message with AI agent, execute tool calls, and return response.
    Creates a new conversation if conversation_id is not provided.
    Includes context window management (last 10 messages).
    """
    try:
        # 1. Rate Limiting
        check_rate_limit(current_user.id)

        # 2. Input Validation (Sanitization)
        message_content = request.message.strip()
        if not message_content:
            raise BusinessException(
                message="Message content cannot be empty or just whitespace",
                error_code="INVALID_INPUT",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        logger.info(
            f"Processing chat message for user {current_user.id} "
            f"(conversation_id: {request.conversation_id or 'new'})"
        )

        # 3. Get or create conversation
        conversation = None
        conversation_history = []

        if request.conversation_id:
            # Load existing conversation
            try:
                conv_id = int(request.conversation_id)
            except ValueError:
                raise BusinessException(
                    message="Invalid conversation ID format",
                    error_code="INVALID_ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            statement = select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == current_user.id
            )
            result = await db.execute(statement)
            conversation = result.scalar_one_or_none()

            if not conversation:
                logger.warning(
                    f"Conversation {request.conversation_id} not found "
                    f"or access denied for user {current_user.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or access denied"
                )

            # 4. Context Window Management
            # Load last 10 messages (5 turns) to fit in context window and keep it relevant
            history_statement = select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.desc()).limit(10)

            history_result = await db.execute(history_statement)
            messages = list(history_result.scalars().all())
            messages.reverse() # Sort back to chronological for the agent

            # Convert to OpenAI message format
            for msg in messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content or ""
                })

            logger.info(
                f"Loaded {len(conversation_history)} historical messages (Context Window) "
                f"for conversation {conversation.id}"
            )

        else:
            # Create new conversation with title from first message (truncated)
            conversation_title = message_content[:200] if len(message_content) <= 200 else message_content[:197] + "..."

            conversation = Conversation(
                user_id=current_user.id,
                title=conversation_title,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
                meta={}
            )
            db.add(conversation)
            await db.flush()  # Get conversation ID without committing

            logger.info(f"Created new conversation {conversation.id} for user {current_user.id}")

        # 5. Save user message
        user_message_db = Message(
            conversation_id=conversation.id,
            role="user",
            content=message_content,
            tool_calls=None,
            created_at=get_utc_now()
        )
        db.add(user_message_db)

        # 6. Get AI response with timeout handling
        try:
            # Wrap agent call in wait_for for an extra layer of protection
            agent_result = await asyncio.wait_for(
                get_agent_response(
                    user_message=message_content,
                    conversation_history=conversation_history,
                    user_id=current_user.id
                ),
                timeout=30.0 # Upper bound for total agent processing
            )
        except asyncio.TimeoutError:
            logger.error("Agent processing timed out")
            raise BusinessException(
                message="The AI assistant is taking too long to respond. Please try again later.",
                error_code="AGENT_TIMEOUT",
                status_code=status.HTTP_504_GATEWAY_TIMEOUT
            )

        if agent_result.get("error"):
            logger.error(f"Agent error: {agent_result['error']}")
            # Mask internal errors for security
            raise BusinessException(
                message="The AI assistant encountered an error. Please try a simpler request.",
                error_code="AGENT_FAILURE",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 7. Save assistant message
        assistant_message_db = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=agent_result["response"],
            tool_calls={"tools": agent_result["tool_calls"]} if agent_result["tool_calls"] else None,
            created_at=get_utc_now()
        )
        db.add(assistant_message_db)

        # 8. Update conversation timestamp
        conversation.updated_at = get_utc_now()

        # 9. Commit all changes
        await db.commit()
        await db.refresh(conversation)

        logger.info(
            f"Chat turn completed for conversation {conversation.id} "
            f"with {len(agent_result['tool_calls'])} tool call(s)"
        )

        # 10. Build response
        tool_calls_response = [
            ToolCall(tool_name=tc["tool_name"], result=tc["result"])
            for tc in agent_result["tool_calls"]
        ]

        return ChatResponse(
            response=agent_result["response"],
            conversation_id=str(conversation.id),
            tool_calls=tool_calls_response
        )

    except (BusinessException, HTTPException):
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        # Ensure generic error for unhandled exceptions to prevent path leakage
        logger.error(f"Unexpected error in chat endpoint: {type(e).__name__}", exc_info=True)
        raise BusinessException(
            message="An internal error occurred. Our team has been notified.",
            error_code="SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/conversations",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    List user's conversations.

    Retrieve all conversations for authenticated user with pagination.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum conversations to return (default: 50, max: 100)
        offset: Pagination offset (default: 0)

    Returns:
        List of conversations with metadata
    """
    # Validate pagination parameters
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    try:
        # Get total count
        from sqlalchemy import func
        count_statement = select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user.id
        )
        count_result = await db.execute(count_statement)
        total = count_result.scalar() or 0

        # Get conversations
        statement = select(Conversation).where(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)

        result = await db.execute(statement)
        conversations = result.scalars().all()

        logger.info(
            f"Retrieved {len(conversations)} conversations for user {current_user.id} "
            f"(total: {total})"
        )

        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ],
            "total": total
        }

    except Exception as e:
        logger.error(f"Error listing conversations: {type(e).__name__}: {str(e)}", exc_info=True)
        raise BusinessException(
            message="Failed to retrieve conversations",
            error_code="CONVERSATION_LIST_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/conversations/{conversation_id}",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"}
    }
)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation with message history.

    Retrieve specific conversation and its messages.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Conversation with messages

    Raises:
        HTTPException: If conversation not found or access denied
    """
    try:
        # Get conversation
        statement = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await db.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Check ownership
        if conversation.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} attempted to access conversation {conversation_id} "
                f"belonging to user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Get messages
        messages_statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        messages_result = await db.execute(messages_statement)
        messages = messages_result.scalars().all()

        logger.info(
            f"Retrieved conversation {conversation_id} with {len(messages)} messages "
            f"for user {current_user.id}"
        )

        return {
            "conversation": {
                "id": str(conversation.id),
                "user_id": conversation.user_id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "meta": conversation.meta
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "conversation_id": str(msg.conversation_id),
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": msg.tool_calls,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving conversation {conversation_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise BusinessException(
            message="Failed to retrieve conversation",
            error_code="CONVERSATION_GET_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete(
    "/conversations/{conversation_id}",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Conversation not found"}
    }
)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete conversation.

    Delete conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If conversation not found or access denied
    """
    try:
        # Get conversation
        statement = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await db.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Check ownership
        if conversation.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} attempted to delete conversation {conversation_id} "
                f"belonging to user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Delete messages first (foreign key constraint)
        messages_statement = select(Message).where(
            Message.conversation_id == conversation_id
        )
        messages_result = await db.execute(messages_statement)
        messages = messages_result.scalars().all()

        for message in messages:
            await db.delete(message)

        # Delete conversation
        await db.delete(conversation)
        await db.commit()

        logger.info(
            f"Deleted conversation {conversation_id} with {len(messages)} messages "
            f"for user {current_user.id}"
        )

        return {
            "message": "Conversation deleted successfully"
        }

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error deleting conversation {conversation_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise BusinessException(
            message="Failed to delete conversation",
            error_code="CONVERSATION_DELETE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
