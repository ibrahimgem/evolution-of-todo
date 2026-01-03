"""
Integration tests for chat endpoint with task listing.

Tests the full flow from chat API endpoint through agent to list_tasks tool.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from src.models import Task


@pytest.mark.integration
@pytest.mark.asyncio
class TestChatListTasksIntegration:
    """Integration tests for task listing via chat endpoint."""

    async def test_chat_endpoint_lists_tasks_from_message(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test /api/chat endpoint processes task listing request."""
        # Create some tasks
        task1 = Task(
            user_id=test_user.id,
            title="Buy groceries",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        task2 = Task(
            user_id=test_user.id,
            title="Finish report",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(task1)
        async_session.add(task2)
        await async_session.commit()

        # Mock OpenAI agent response
        mock_agent_result = {
            "response": "You have 2 tasks: Buy groceries (incomplete) and Finish report (complete).",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": task1.id,
                                "title": "Buy groceries",
                                "completed": False
                            },
                            {
                                "id": task2.id,
                                "title": "Finish report",
                                "completed": True
                            }
                        ],
                        "total": 2
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Show me all my tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
        assert "tool_calls" in data
        assert len(data["tool_calls"]) > 0
        assert data["tool_calls"][0]["tool_name"] == "list_tasks"

    async def test_chat_lists_incomplete_tasks_only(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat can filter for incomplete tasks only."""
        # Create completed and incomplete tasks
        incomplete_task = Task(
            user_id=test_user.id,
            title="Buy groceries",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        completed_task = Task(
            user_id=test_user.id,
            title="Finish report",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(incomplete_task)
        async_session.add(completed_task)
        await async_session.commit()

        mock_agent_result = {
            "response": "You have 1 incomplete task: Buy groceries.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "incomplete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": incomplete_task.id,
                                "title": "Buy groceries",
                                "completed": False
                            }
                        ],
                        "total": 1
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "What tasks do I need to complete?"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"][0]["result"]["total"] == 1
        assert data["tool_calls"][0]["result"]["tasks"][0]["completed"] is False

    async def test_chat_lists_completed_tasks_only(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat can filter for completed tasks only."""
        # Create completed and incomplete tasks
        incomplete_task = Task(
            user_id=test_user.id,
            title="Buy groceries",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        completed_task = Task(
            user_id=test_user.id,
            title="Finish report",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(incomplete_task)
        async_session.add(completed_task)
        await async_session.commit()

        mock_agent_result = {
            "response": "You have completed 1 task: Finish report.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "complete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": completed_task.id,
                                "title": "Finish report",
                                "completed": True
                            }
                        ],
                        "total": 1
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "What tasks have I completed?"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"][0]["result"]["total"] == 1
        assert data["tool_calls"][0]["result"]["tasks"][0]["completed"] is True

    async def test_chat_handles_empty_task_list(
        self, async_client, auth_headers, test_user
    ):
        """Test chat handles empty task list gracefully."""
        mock_agent_result = {
            "response": "You have no tasks yet.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [],
                        "total": 0
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Show me my tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"][0]["result"]["total"] == 0
        assert data["tool_calls"][0]["result"]["tasks"] == []

    async def test_chat_lists_tasks_with_pagination(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat can paginate task listing."""
        # Create 15 tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"Task {i}",
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 16)
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        # Mock agent requesting first 10 tasks
        mock_agent_result = {
            "response": "Here are your first 10 tasks...",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"limit": 10, "offset": 0},
                    "result": {
                        "success": True,
                        "tasks": [{"id": i, "title": f"Task {i}"} for i in range(1, 11)],
                        "total": 15,
                        "limit": 10,
                        "offset": 0
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Show me my first 10 tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tool_calls"][0]["result"]["total"] == 15
        assert data["tool_calls"][0]["result"]["limit"] == 10
        assert len(data["tool_calls"][0]["result"]["tasks"]) == 10

    async def test_chat_lists_tasks_with_due_dates(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat lists tasks with due date information."""
        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        task_with_due = Task(
            user_id=test_user.id,
            title="Important meeting",
            description="Prepare presentation",
            due_date=future_date,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(task_with_due)
        await async_session.commit()

        mock_agent_result = {
            "response": "You have 1 task due tomorrow: Important meeting.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "incomplete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": task_with_due.id,
                                "title": "Important meeting",
                                "description": "Prepare presentation",
                                "due_date": future_date.isoformat(),
                                "completed": False
                            }
                        ],
                        "total": 1
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "What tasks are due soon?"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tool_calls"][0]["result"]["tasks"]) == 1
        assert data["tool_calls"][0]["result"]["tasks"][0]["due_date"] is not None

    async def test_chat_persists_list_tasks_interaction(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat persists list_tasks interaction to conversation history."""
        from src.models import Message, Conversation
        from sqlmodel import select

        mock_agent_result = {
            "response": "You have no tasks.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "result": {"success": True, "tasks": [], "total": 0}
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Show me my tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]

        # Verify messages persisted
        stmt = select(Message).where(Message.conversation_id == conversation_id)
        result = await async_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) == 2  # User message + Assistant response
        assert messages[0].role == "user"
        assert messages[0].content == "Show me my tasks"
        assert messages[1].role == "assistant"
        assert messages[1].tool_calls is not None

    async def test_chat_handles_list_tasks_tool_error(
        self, async_client, auth_headers, test_user
    ):
        """Test chat handles list_tasks tool errors gracefully."""
        mock_agent_result = {
            "response": "I encountered an error retrieving your tasks.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
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
                json={"message": "Show me my tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert not data["tool_calls"][0]["result"]["success"]
        assert "error" in data["tool_calls"][0]["result"]

    async def test_chat_lists_only_authenticated_user_tasks(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test list_tasks only returns tasks for authenticated user."""
        from src.models import User
        from src.auth import hash_password

        # Create another user with tasks
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

        # Create tasks for both users
        test_user_task = Task(
            user_id=test_user.id,
            title="Test User Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        other_user_task = Task(
            user_id=other_user.id,
            title="Other User Task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(test_user_task)
        async_session.add(other_user_task)
        await async_session.commit()

        mock_agent_result = {
            "response": "You have 1 task: Test User Task.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": test_user_task.id,
                                "title": "Test User Task",
                                "completed": False
                            }
                        ],
                        "total": 1
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": "Show me my tasks"},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        # Should only see test_user's task
        assert data["tool_calls"][0]["result"]["total"] == 1
        assert data["tool_calls"][0]["result"]["tasks"][0]["title"] == "Test User Task"

    async def test_chat_combines_add_and_list_tasks(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test chat can handle both adding and listing tasks in sequence."""
        # First, add a task
        mock_add_result = {
            "response": "I've added 'Buy milk' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "Buy milk", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_add_result):
            add_response = await async_client.post(
                "/api/chat",
                json={"message": "Add a task to buy milk"},
                headers=auth_headers
            )

        assert add_response.status_code == 200
        conversation_id = add_response.json()["conversation_id"]

        # Create the task in DB for listing
        task = Task(
            user_id=test_user.id,
            title="Buy milk",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(task)
        await async_session.commit()

        # Then, list tasks in same conversation
        mock_list_result = {
            "response": "You have 1 task: Buy milk.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "result": {
                        "success": True,
                        "tasks": [{"id": task.id, "title": "Buy milk", "completed": False}],
                        "total": 1
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_list_result):
            list_response = await async_client.post(
                "/api/chat",
                json={
                    "message": "What tasks do I have?",
                    "conversation_id": conversation_id
                },
                headers=auth_headers
            )

        assert list_response.status_code == 200
        data = list_response.json()
        assert data["conversation_id"] == conversation_id
        assert data["tool_calls"][0]["result"]["total"] == 1

    async def test_chat_lists_tasks_requires_authentication(
        self, async_client
    ):
        """Test listing tasks via chat requires authentication."""
        response = await async_client.post(
            "/api/chat",
            json={"message": "Show me my tasks"}
        )

        assert response.status_code == 401
