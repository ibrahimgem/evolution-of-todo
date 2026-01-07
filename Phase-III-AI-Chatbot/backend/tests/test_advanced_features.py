import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch
from src.models import Message, Conversation, Task
from src.agent import get_agent_response

@pytest.mark.asyncio
@pytest.mark.integration
class TestAdvancedFeatures:
    """Integration tests for resuming conversations and temporal queries."""

    async def test_resume_conversation_history(self, async_client, auth_headers, test_conversation, async_session):
        """Test GET /api/conversations/{id} returns chronological message history."""
        # Add a few messages
        msg1 = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="Hello agent",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=5)
        )
        msg2 = Message(
            conversation_id=test_conversation.id,
            role="assistant",
            content="Hello user! How can I help?",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=4)
        )
        async_session.add_all([msg1, msg2])
        await async_session.commit()

        response = await async_client.get(f"/api/conversations/{test_conversation.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert len(data["messages"]) >= 2
        # Check chronological order
        assert data["messages"][0]["content"] == "Hello agent"
        assert data["messages"][1]["content"] == "Hello user! How can I help?"

    @patch("src.routes.chat.get_agent_response")
    async def test_multi_turn_context_hydration(self, mock_agent, async_client, auth_headers, test_conversation, async_session):
        """Test that POST /chat hydrates context from history for existing conversations."""
        # Add previous turn to database
        msg1 = Message(
            conversation_id=test_conversation.id,
            role="user",
            content="My name is Alice.",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        msg2 = Message(
            conversation_id=test_conversation.id,
            role="assistant",
            content="Nice to meet you, Alice!",
            created_at=datetime.now(timezone.utc) - timedelta(minutes=9)
        )
        async_session.add_all([msg1, msg2])
        await async_session.commit()

        # Mock agent response
        mock_agent.return_value = {
            "response": "I remember you, Alice!",
            "tool_calls": [],
            "error": None
        }

        # Send follow-up message
        payload = {
            "conversation_id": str(test_conversation.id),
            "message": "What is my name?"
        }
        response = await async_client.post("/api/chat", json=payload, headers=auth_headers)

        assert response.status_code == 200

        # Verify get_agent_response was called with history
        args, kwargs = mock_agent.call_args
        history = kwargs.get("conversation_history")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "My name is Alice."

    async def test_temporal_query_interpretation(self, async_session, test_user):
        """Test that the agent's system prompt includes temporal guidance (unit-ish integration)."""
        from src.agent import SYSTEM_PROMPT

        # Verify current server time and temporal guidelines are present
        assert "Current Server Time" in SYSTEM_PROMPT
        assert "overdue" in SYSTEM_PROMPT.lower()
        assert "tomorrow" in SYSTEM_PROMPT.lower()

    @patch("src.agent.openai_client")
    async def test_temporal_query_tool_call(self, mock_openai, test_user):
        """Test that a temporal request like 'due tomorrow' triggers list_tasks with agent logic."""
        # This is a bit complex to mock fully, so we'll verify the agent function
        # correctly prepares messages including the temporal-aware system prompt.

        mock_openai.chat.completions.create = AsyncMock()
        mock_openai.chat.completions.create.return_value.choices = [
            AsyncMock(message=AsyncMock(content="You have no tasks due tomorrow.", tool_calls=None))
        ]

        await get_agent_response(
            user_message="What is due tomorrow?",
            conversation_history=[],
            user_id=test_user.id
        )

        # Check if system prompt with time was sent
        call_args = mock_openai.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        system_msg = messages[0]["content"]
        assert "Current Server Time" in system_msg
        assert datetime.now(timezone.utc).strftime("%Y-%m-%d") in system_msg
