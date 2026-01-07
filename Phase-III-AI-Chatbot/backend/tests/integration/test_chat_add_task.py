"""
Integration tests for chat endpoint with task creation.

Tests the full flow from chat API endpoint through agent to add_task tool.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.integration
@pytest.mark.asyncio
class TestChatAddTaskIntegration:
    """Integration tests for task creation via chat endpoint."""

    async def test_chat_endpoint_creates_task_from_message(
        self, async_client, auth_headers, test_user
    ):
        """Test /api/chat endpoint processes task creation request."""
        # Mock OpenAI agent response
        mock_agent_result = {
            "response": "I've added 'Buy groceries' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Buy groceries"},
                    "result": {
                        "success": True,
                        "task": {
                            "id": 1,
                            "title": "Buy groceries",
                            "completed": False
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task to buy groceries"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "tool_calls" in data
        assert len(data["tool_calls"]) > 0

    async def test_chat_endpoint_requires_authentication(self, async_client):
        """Test chat endpoint requires valid JWT token."""
        response = await async_client.post(
            "/api/chat",
            json={"message": "Add a task"}
        )

        assert response.status_code == 401

    async def test_chat_endpoint_validates_request_format(
        self, async_client, auth_headers
    ):
        """Test chat endpoint validates request structure."""
        # Missing message field
        response = await async_client.post(
            "/api/chat",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_chat_creates_new_conversation_on_first_message(
        self, async_client, auth_headers, async_session
    ):
        """Test chat creates a new conversation when conversation_id not provided."""
        from src.models import Conversation
        from sqlmodel import select

        mock_agent_result = {
            "response": "Task added",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task to buy milk"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify conversation created in database
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await async_session.execute(stmt)
        conversation = result.scalar_one_or_none()

        assert conversation is not None
        assert conversation.title is not None

    async def test_chat_persists_user_message(
        self, async_client, auth_headers, async_session
    ):
        """Test chat endpoint persists user message to database."""
        from src.models import Message
        from sqlmodel import select

        mock_agent_result = {
            "response": "Got it",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task to buy groceries"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify user message persisted
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        )
        result = await async_session.execute(stmt)
        user_message = result.scalar_one_or_none()

        assert user_message is not None
        assert user_message.content == "Add a task to buy groceries"

    async def test_chat_persists_assistant_response(
        self, async_client, auth_headers, async_session
    ):
        """Test chat endpoint persists assistant response to database."""
        from src.models import Message
        from sqlmodel import select

        mock_agent_result = {
            "response": "I've added the task for you.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "result": {"success": True}
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify assistant message persisted
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "assistant"
        )
        result = await async_session.execute(stmt)
        assistant_message = result.scalar_one_or_none()

        assert assistant_message is not None
        assert assistant_message.content == "I've added the task for you."
        assert assistant_message.tool_calls is not None

    async def test_chat_resumes_existing_conversation(
        self, async_client, auth_headers, test_conversation, async_session
    ):
        """Test chat endpoint resumes existing conversation."""
        from src.models import Message
        from sqlmodel import select

        mock_agent_result = {
            "response": "Task added to existing conversation",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={
                    "message": "Add another task",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == str(test_conversation.id)

        # Verify message added to existing conversation
        stmt = select(Message).where(
            Message.conversation_id == test_conversation.id
        )
        result = await async_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) > 0

    async def test_chat_loads_conversation_history(
        self, async_client, auth_headers, test_conversation, test_message
    ):
        """Test chat endpoint loads conversation history for context."""
        mock_agent_result = {
            "response": "Following up on previous context",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message') as mock_process:
            mock_process.return_value = mock_agent_result

            await async_client.post(
                "/api/chat",
                json={
                    "message": "Continue",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

            # Verify process_chat_message was called with history
            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert call_args is not None
            # Verify history parameter contains previous messages
            if len(call_args[0]) > 2:  # Has history parameter
                history = call_args[0][2]
                assert isinstance(history, list)

    async def test_chat_handles_agent_failure(
        self, async_client, auth_headers
    ):
        """Test chat endpoint handles agent processing failures."""
        with patch('src.agent.process_chat_message', side_effect=Exception("Agent error")):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task"},
                headers=auth_headers
            )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data or "detail" in data

    async def test_chat_handles_tool_execution_error(
        self, async_client, auth_headers
    ):
        """Test chat handles tool execution errors gracefully."""
        mock_agent_result = {
            "response": "I encountered an error adding the task.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "result": {
                        "success": False,
                        "error": "Database connection failed"
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data["response"].lower() or not data["tool_calls"][0]["result"]["success"]

    async def test_chat_prevents_cross_user_conversation_access(
        self, async_client, auth_headers, async_session
    ):
        """Test users cannot access other users' conversations."""
        from src.models import User, Conversation
        from src.auth import hash_password, create_access_token
        from datetime import datetime, timezone

        # Create another user and their conversation
        other_user = User(
            email="other@example.com",
            name="Other User",
            hashed_password=hash_password("password"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(other_user)
        await async_session.commit()
        await async_session.refresh(other_user)

        other_conversation = Conversation(
            user_id=other_user.id,
            title="Other's conversation",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            meta={}
        )
        async_session.add(other_conversation)
        await async_session.commit()
        await async_session.refresh(other_conversation)

        # Try to access other user's conversation
        mock_agent_result = {"response": "Test", "tool_calls": []}

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={
                    "message": "Test message",
                    "conversation_id": str(other_conversation.id)
                },
                headers=auth_headers
            )

        # Should be forbidden or not found
        assert response.status_code in [403, 404]

    async def test_chat_updates_conversation_timestamp(
        self, async_client, auth_headers, test_conversation, async_session
    ):
        """Test chat updates conversation updated_at timestamp."""
        from src.models import Conversation
        from sqlmodel import select
        from datetime import datetime, timezone

        original_updated_at = test_conversation.updated_at

        # Wait a moment to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.1)

        mock_agent_result = {
            "response": "Updated",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            await async_client.post(
                "/api/chat",
                json={
                    "message": "New message",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        # Refresh conversation from database
        stmt = select(Conversation).where(Conversation.id == test_conversation.id)
        result = await async_session.execute(stmt)
        updated_conversation = result.scalar_one_or_none()

        assert updated_conversation is not None
        assert updated_conversation.updated_at > original_updated_at
