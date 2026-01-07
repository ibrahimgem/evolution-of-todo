"""
E2E tests for task filtering flow.

Tests the complete user journey for listing and filtering tasks through
natural language chat interface with various filter combinations.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from src.models import Task


@pytest.mark.e2e
@pytest.mark.asyncio
class TestTaskFilteringFlowE2E:
    """End-to-end tests for task listing and filtering via natural language."""

    async def test_full_list_all_tasks_flow(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test complete flow: message -> agent -> list_tasks -> database query -> response."""
        from src.models import Conversation, Message
        from sqlmodel import select

        # Setup: Create tasks for the user
        completed_task = Task(
            user_id=test_user.id,
            title="Completed Task",
            description="This task is done",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task = Task(
            user_id=test_user.id,
            title="Incomplete Task",
            description="This task is pending",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(completed_task)
        async_session.add(incomplete_task)
        await async_session.commit()
        await async_session.refresh(completed_task)
        await async_session.refresh(incomplete_task)

        # User sends natural language message
        message = "Show me all my tasks"

        mock_agent_result = {
            "response": "You have 2 tasks: 'Completed Task' (done) and 'Incomplete Task' (pending).",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all", "limit": 50, "offset": 0},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": incomplete_task.id,
                                "title": "Incomplete Task",
                                "description": "This task is pending",
                                "completed": False,
                                "due_date": None,
                                "created_at": incomplete_task.created_at.isoformat(),
                                "updated_at": incomplete_task.updated_at.isoformat()
                            },
                            {
                                "id": completed_task.id,
                                "title": "Completed Task",
                                "description": "This task is done",
                                "completed": True,
                                "due_date": None,
                                "created_at": completed_task.created_at.isoformat(),
                                "updated_at": completed_task.updated_at.isoformat()
                            }
                        ],
                        "total": 2,
                        "offset": 0,
                        "limit": 50
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
        assert data["tool_calls"][0]["tool_name"] == "list_tasks"
        assert data["tool_calls"][0]["result"]["success"] is True
        assert data["tool_calls"][0]["result"]["total"] == 2
        assert len(data["tool_calls"][0]["result"]["tasks"]) == 2

        conversation_id = data["conversation_id"]

        # 3. Verify conversation created
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await async_session.execute(stmt)
        conversation = result.scalar_one_or_none()

        assert conversation is not None
        assert conversation.user_id == test_user.id

        # 4. Verify messages persisted
        stmt = select(Message).where(Message.conversation_id == conversation_id)
        result = await async_session.execute(stmt)
        messages = result.scalars().all()

        assert len(messages) == 2  # User + Assistant
        assert messages[0].role == "user"
        assert messages[0].content == message
        assert messages[1].role == "assistant"
        assert messages[1].tool_calls is not None

    async def test_filter_by_status_incomplete(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test filtering for incomplete tasks only."""
        # Setup: Create mixed completed/incomplete tasks
        completed_task = Task(
            user_id=test_user.id,
            title="Finished work",
            completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task1 = Task(
            user_id=test_user.id,
            title="Buy groceries",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        incomplete_task2 = Task(
            user_id=test_user.id,
            title="Call dentist",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add_all([completed_task, incomplete_task1, incomplete_task2])
        await async_session.commit()

        message = "What tasks do I still need to complete?"

        mock_agent_result = {
            "response": "You have 2 incomplete tasks: 'Buy groceries' and 'Call dentist'.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "incomplete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {"id": incomplete_task1.id, "title": "Buy groceries", "completed": False},
                            {"id": incomplete_task2.id, "title": "Call dentist", "completed": False}
                        ],
                        "total": 2,
                        "offset": 0,
                        "limit": 50
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
        assert data["tool_calls"][0]["result"]["total"] == 2
        # Verify all returned tasks are incomplete
        for task in data["tool_calls"][0]["result"]["tasks"]:
            assert task["completed"] is False

    async def test_filter_by_status_complete(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test filtering for completed tasks only."""
        # Setup: Create mixed tasks
        completed_task1 = Task(
            user_id=test_user.id,
            title="Finished report",
            completed=True,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        completed_task2 = Task(
            user_id=test_user.id,
            title="Paid bills",
            completed=True,
            created_at=datetime.now(timezone.utc) - timedelta(hours=1),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        incomplete_task = Task(
            user_id=test_user.id,
            title="Upcoming meeting",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add_all([completed_task1, completed_task2, incomplete_task])
        await async_session.commit()

        message = "What have I completed recently?"

        mock_agent_result = {
            "response": "You've completed 2 tasks: 'Finished report' and 'Paid bills'.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "complete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {"id": completed_task2.id, "title": "Paid bills", "completed": True},
                            {"id": completed_task1.id, "title": "Finished report", "completed": True}
                        ],
                        "total": 2,
                        "offset": 0,
                        "limit": 50
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
        assert data["tool_calls"][0]["result"]["total"] == 2
        # Verify all returned tasks are completed
        for task in data["tool_calls"][0]["result"]["tasks"]:
            assert task["completed"] is True

    async def test_filter_with_due_date_information(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test listing tasks includes due date information for filtering/sorting."""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        next_week = datetime.now(timezone.utc) + timedelta(days=7)

        task_due_tomorrow = Task(
            user_id=test_user.id,
            title="Meeting prep",
            due_date=tomorrow,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        task_due_next_week = Task(
            user_id=test_user.id,
            title="Project review",
            due_date=next_week,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        task_no_due_date = Task(
            user_id=test_user.id,
            title="Someday task",
            due_date=None,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add_all([task_due_tomorrow, task_due_next_week, task_no_due_date])
        await async_session.commit()

        message = "What tasks are coming up?"

        mock_agent_result = {
            "response": "You have 3 upcoming tasks. 'Meeting prep' is due tomorrow.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "incomplete"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": task_due_tomorrow.id,
                                "title": "Meeting prep",
                                "due_date": tomorrow.isoformat(),
                                "completed": False
                            },
                            {
                                "id": task_due_next_week.id,
                                "title": "Project review",
                                "due_date": next_week.isoformat(),
                                "completed": False
                            },
                            {
                                "id": task_no_due_date.id,
                                "title": "Someday task",
                                "due_date": None,
                                "completed": False
                            }
                        ],
                        "total": 3,
                        "offset": 0,
                        "limit": 50
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
        tasks = data["tool_calls"][0]["result"]["tasks"]

        # Verify due date information is present
        assert tasks[0]["due_date"] is not None
        assert tasks[1]["due_date"] is not None
        assert tasks[2]["due_date"] is None

    async def test_pagination_first_page(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test pagination - requesting first page of results."""
        # Create 25 tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"Task {i:02d}",
                completed=False,
                created_at=datetime.now(timezone.utc) + timedelta(seconds=i),
                updated_at=datetime.now(timezone.utc) + timedelta(seconds=i)
            )
            for i in range(1, 26)
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        message = "Show me my first 10 tasks"

        mock_agent_result = {
            "response": "Here are your first 10 tasks...",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all", "limit": 10, "offset": 0},
                    "result": {
                        "success": True,
                        "tasks": [{"id": i, "title": f"Task {i:02d}"} for i in range(1, 11)],
                        "total": 25,
                        "offset": 0,
                        "limit": 10
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
        result = data["tool_calls"][0]["result"]
        assert result["total"] == 25
        assert result["limit"] == 10
        assert result["offset"] == 0
        assert len(result["tasks"]) == 10

    async def test_pagination_second_page(
        self, async_client, auth_headers, test_user, async_session, test_conversation
    ):
        """Test pagination - requesting second page in same conversation."""
        # Create 25 tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"Task {i:02d}",
                completed=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            for i in range(1, 26)
        ]
        for task in tasks:
            async_session.add(task)
        await async_session.commit()

        message = "Show me the next 10 tasks"

        mock_agent_result = {
            "response": "Here are tasks 11-20...",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all", "limit": 10, "offset": 10},
                    "result": {
                        "success": True,
                        "tasks": [{"id": i, "title": f"Task {i:02d}"} for i in range(11, 21)],
                        "total": 25,
                        "offset": 10,
                        "limit": 10
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
        result = data["tool_calls"][0]["result"]
        assert result["total"] == 25
        assert result["limit"] == 10
        assert result["offset"] == 10

    async def test_empty_result_set(
        self, async_client, auth_headers, test_user
    ):
        """Test filtering returns empty result when no tasks match."""
        message = "Show me my completed tasks"

        mock_agent_result = {
            "response": "You haven't completed any tasks yet.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "complete"},
                    "result": {
                        "success": True,
                        "tasks": [],
                        "total": 0,
                        "offset": 0,
                        "limit": 50
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
        result = data["tool_calls"][0]["result"]
        assert result["success"] is True
        assert result["total"] == 0
        assert result["tasks"] == []

    async def test_user_isolation_in_listing(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test users can only see their own tasks when listing."""
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
            title="My task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        other_user_task = Task(
            user_id=other_user.id,
            title="Other's task",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(test_user_task)
        async_session.add(other_user_task)
        await async_session.commit()

        message = "Show me all my tasks"

        mock_agent_result = {
            "response": "You have 1 task: 'My task'.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {"id": test_user_task.id, "title": "My task", "completed": False}
                        ],
                        "total": 1,
                        "offset": 0,
                        "limit": 50
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
        result = data["tool_calls"][0]["result"]
        # Should only see test_user's task
        assert result["total"] == 1
        assert result["tasks"][0]["title"] == "My task"

    async def test_combined_add_and_list_workflow(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test complete workflow: add task, then list to verify."""
        # Step 1: Add a task
        add_message = "Add a task to write documentation"

        mock_add_result = {
            "response": "I've added 'Write documentation' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "Write documentation", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_add_result):
            add_response = await async_client.post(
                "/api/chat",
                json={"message": add_message},
                headers=auth_headers
            )

        assert add_response.status_code == 200
        conversation_id = add_response.json()["conversation_id"]

        # Create the task in DB for listing
        task = Task(
            user_id=test_user.id,
            title="Write documentation",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        # Step 2: List tasks to verify
        list_message = "Show me my tasks"

        mock_list_result = {
            "response": "You have 1 task: 'Write documentation'.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": task.id,
                                "title": "Write documentation",
                                "completed": False,
                                "created_at": task.created_at.isoformat(),
                                "updated_at": task.updated_at.isoformat()
                            }
                        ],
                        "total": 1,
                        "offset": 0,
                        "limit": 50
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_list_result):
            list_response = await async_client.post(
                "/api/chat",
                json={
                    "message": list_message,
                    "conversation_id": conversation_id
                },
                headers=auth_headers
            )

        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["conversation_id"] == conversation_id
        result = list_data["tool_calls"][0]["result"]
        assert result["total"] == 1
        assert result["tasks"][0]["title"] == "Write documentation"

    async def test_list_tasks_with_all_task_fields(
        self, async_client, auth_headers, test_user, async_session
    ):
        """Test list_tasks returns all required task fields."""
        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        task = Task(
            user_id=test_user.id,
            title="Complete task",
            description="Full task details",
            due_date=future_date,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        message = "Show me my tasks with full details"

        mock_agent_result = {
            "response": "Here's your task with all details.",
            "tool_calls": [
                {
                    "tool_name": "list_tasks",
                    "arguments": {"status": "all"},
                    "result": {
                        "success": True,
                        "tasks": [
                            {
                                "id": task.id,
                                "title": "Complete task",
                                "description": "Full task details",
                                "due_date": future_date.isoformat(),
                                "completed": False,
                                "created_at": task.created_at.isoformat(),
                                "updated_at": task.updated_at.isoformat()
                            }
                        ],
                        "total": 1,
                        "offset": 0,
                        "limit": 50
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
        task_result = data["tool_calls"][0]["result"]["tasks"][0]

        # Verify all required fields are present
        assert "id" in task_result
        assert "title" in task_result
        assert "description" in task_result
        assert "due_date" in task_result
        assert "completed" in task_result
        assert "created_at" in task_result
        assert "updated_at" in task_result
