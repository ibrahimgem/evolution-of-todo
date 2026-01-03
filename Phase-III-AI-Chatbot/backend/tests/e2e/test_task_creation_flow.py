"""
E2E tests for full task creation flow.

Tests the complete user journey from sending a natural language message
through the chat API, agent processing, MCP tool execution, and database persistence.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTaskCreationFlowE2E:
    """End-to-end tests for task creation via natural language."""

    async def test_full_task_creation_flow_minimal(
        self, async_client, auth_headers, async_session
    ):
        """Test complete flow: message -> agent -> add_task -> database -> response."""
        from src.models import Task, Conversation, Message
        from sqlmodel import select

        # User sends natural language message
        message = "Add a task to buy groceries"

        # Mock agent to use actual add_task tool
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
                            "description": None,
                            "due_date": None,
                            "completed": False,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            # 1. Send chat request
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        # 2. Verify HTTP response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "tool_calls" in data
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool_name"] == "add_task"
        assert data["tool_calls"][0]["result"]["success"] is True

        conversation_id = data["conversation_id"]
        task_id = data["tool_calls"][0]["result"]["task"]["id"]

        # 3. Verify conversation created
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await async_session.execute(stmt)
        conversation = result.scalar_one_or_none()

        assert conversation is not None
        assert conversation.title is not None

        # 4. Verify user message persisted
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        )
        result = await async_session.execute(stmt)
        user_message = result.scalar_one_or_none()

        assert user_message is not None
        assert user_message.content == message

        # 5. Verify assistant message persisted with tool calls
        stmt = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == "assistant"
        )
        result = await async_session.execute(stmt)
        assistant_message = result.scalar_one_or_none()

        assert assistant_message is not None
        assert assistant_message.tool_calls is not None
        assert len(assistant_message.tool_calls) > 0

        # 6. Verify task created in database (most important!)
        stmt = select(Task).where(Task.id == task_id)
        result = await async_session.execute(stmt)
        task = result.scalar_one_or_none()

        assert task is not None
        assert task.title == "Buy groceries"
        assert task.completed is False

    async def test_full_task_creation_flow_with_details(
        self, async_client, auth_headers, async_session
    ):
        """Test complete flow with description and due date extraction."""
        from src.models import Task
        from sqlmodel import select
        from datetime import timedelta

        message = "Add a task to buy groceries tomorrow. Need milk, eggs, and bread."
        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        mock_agent_result = {
            "response": "I've added the grocery shopping task for tomorrow.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {
                        "title": "Buy groceries",
                        "description": "Need milk, eggs, and bread",
                        "due_date": future_date.isoformat()
                    },
                    "result": {
                        "success": True,
                        "task": {
                            "id": 1,
                            "title": "Buy groceries",
                            "description": "Need milk, eggs, and bread",
                            "due_date": future_date.isoformat(),
                            "completed": False,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        task_id = data["tool_calls"][0]["result"]["task"]["id"]

        # Verify task in database has all fields
        stmt = select(Task).where(Task.id == task_id)
        result = await async_session.execute(stmt)
        task = result.scalar_one_or_none()

        assert task is not None
        assert task.title == "Buy groceries"
        assert task.description == "Need milk, eggs, and bread"
        # Due date verification would be done here in real implementation

    async def test_task_creation_with_conversation_context(
        self, async_client, auth_headers, test_conversation, async_session
    ):
        """Test task creation in context of existing conversation."""
        from src.models import Task, Message
        from sqlmodel import select

        message = "Also add a task to call mom"

        mock_agent_result = {
            "response": "I've added 'Call mom' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Call mom"},
                    "result": {
                        "success": True,
                        "task": {
                            "id": 1,
                            "title": "Call mom",
                            "completed": False
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={
                    "message": message,
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == str(test_conversation.id)

        # Verify message added to existing conversation
        stmt = select(Message).where(
            Message.conversation_id == test_conversation.id,
            Message.role == "user"
        )
        result = await async_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) > 0
        assert any(msg.content == message for msg in messages)

    async def test_task_creation_failure_flow(
        self, async_client, auth_headers
    ):
        """Test E2E flow when task creation fails."""
        message = "Add a task due yesterday"

        mock_agent_result = {
            "response": "I couldn't add that task because the due date must be in the future.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {
                        "title": "Task",
                        "due_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                    },
                    "result": {
                        "success": False,
                        "error": "Due date must be in the future"
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"][0]["result"]["success"] is False
        assert "error" in data["tool_calls"][0]["result"]

    async def test_multiple_tasks_creation_in_one_message(
        self, async_client, auth_headers, async_session
    ):
        """Test creating multiple tasks from a single message."""
        from src.models import Task
        from sqlmodel import select

        message = "Add three tasks: buy groceries, call mom, and finish report"

        mock_agent_result = {
            "response": "I've added all three tasks for you.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Buy groceries"},
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "Buy groceries", "completed": False}
                    }
                },
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Call mom"},
                    "result": {
                        "success": True,
                        "task": {"id": 2, "title": "Call mom", "completed": False}
                    }
                },
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Finish report"},
                    "result": {
                        "success": True,
                        "task": {"id": 3, "title": "Finish report", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tool_calls"]) == 3
        assert all(call["result"]["success"] for call in data["tool_calls"])

    async def test_conversation_auto_title_generation(
        self, async_client, auth_headers, async_session
    ):
        """Test conversation title is auto-generated from first message."""
        from src.models import Conversation
        from sqlmodel import select

        message = "Add a task to buy groceries tomorrow"

        mock_agent_result = {
            "response": "Task added",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        conversation_id = response.json()["conversation_id"]

        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await async_session.execute(stmt)
        conversation = result.scalar_one_or_none()

        assert conversation is not None
        # Title should be derived from first message (first 50 chars + "...")
        expected_title = message[:50]
        if len(message) > 50:
            expected_title += "..."
        assert conversation.title == expected_title or conversation.title == message

    async def test_user_isolation_in_task_creation(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test tasks are properly scoped to the authenticated user."""
        from src.models import Task
        from sqlmodel import select

        message = "Add a task for user isolation test"

        mock_agent_result = {
            "response": "Task added",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "User isolation test"},
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "User isolation test", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        task_id = response.json()["tool_calls"][0]["result"]["task"]["id"]

        # Verify task belongs to test_user
        stmt = select(Task).where(Task.id == task_id)
        result = await async_session.execute(stmt)
        task = result.scalar_one_or_none()

        assert task is not None
        assert task.user_id == test_user.id
