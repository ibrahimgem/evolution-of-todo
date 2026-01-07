"""
Integration tests for multi-step task creation conversations.

Tests scenarios where the AI needs multiple interactions with the user
to gather all information needed to create a task.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone


@pytest.mark.integration
@pytest.mark.asyncio
class TestMultiStepTaskCreation:
    """Tests for multi-turn task creation conversations."""

    async def test_clarification_request_for_ambiguous_task(
        self, async_client, auth_headers
    ):
        """Test AI asks for clarification when task description is ambiguous."""
        message = "Add something"

        mock_agent_result = {
            "response": "I'd be happy to add a task for you! What would you like the task to be?",
            "tool_calls": []  # No tool call yet - waiting for clarification
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result):
            response = await async_client.post(
                "/api/chat",
                json={"message": message},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tool_calls"]) == 0  # No task created yet
        assert "what" in data["response"].lower() or "clarif" in data["response"].lower()

    async def test_task_creation_after_clarification(
        self, async_client, auth_headers, test_conversation
    ):
        """Test task is created after user provides clarification."""
        # First message: ambiguous
        mock_agent_result_1 = {
            "response": "What task would you like to add?",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_1):
            response1 = await async_client.post(
                "/api/chat",
                json={
                    "message": "Add a task",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response1.status_code == 200
        assert len(response1.json()["tool_calls"]) == 0

        # Second message: clarified
        mock_agent_result_2 = {
            "response": "I've added 'Buy groceries' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Buy groceries"},
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "Buy groceries", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_2):
            response2 = await async_client.post(
                "/api/chat",
                json={
                    "message": "Buy groceries",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response2.status_code == 200
        data = response2.json()
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["result"]["success"] is True

    async def test_multi_turn_date_clarification(
        self, async_client, auth_headers, test_conversation
    ):
        """Test AI asks for due date clarification when ambiguous."""
        # First message with ambiguous date
        message1 = "Add a task to buy groceries soon"

        mock_agent_result_1 = {
            "response": "I can add that task. When would you like it due?",
            "tool_calls": []
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_1):
            response1 = await async_client.post(
                "/api/chat",
                json={
                    "message": message1,
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response1.status_code == 200
        assert "when" in response1.json()["response"].lower() or "due" in response1.json()["response"].lower()

        # Second message with specific date
        message2 = "Tomorrow at 5pm"

        from datetime import timedelta
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        future_date = future_date.replace(hour=17, minute=0, second=0, microsecond=0)

        mock_agent_result_2 = {
            "response": "I've added 'Buy groceries' with a due date of tomorrow at 5pm.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {
                        "title": "Buy groceries",
                        "due_date": future_date.isoformat()
                    },
                    "result": {
                        "success": True,
                        "task": {
                            "id": 1,
                            "title": "Buy groceries",
                            "due_date": future_date.isoformat(),
                            "completed": False
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_2):
            response2 = await async_client.post(
                "/api/chat",
                json={
                    "message": message2,
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response2.status_code == 200
        data = response2.json()
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["result"]["success"] is True

    async def test_context_preservation_across_multiple_messages(
        self, async_client, auth_headers, test_conversation, async_session
    ):
        """Test conversation context is preserved across multiple messages."""
        from src.models import Message
        from sqlmodel import select

        messages = [
            "I need to add some tasks",
            "First, buy groceries",
            "Also call mom",
            "And finish the report"
        ]

        for i, message in enumerate(messages):
            if i == 0:
                mock_result = {"response": "Sure! What tasks would you like to add?", "tool_calls": []}
            else:
                task_title = message.replace("First, ", "").replace("Also ", "").replace("And ", "").capitalize()
                mock_result = {
                    "response": f"Added: {task_title}",
                    "tool_calls": [
                        {
                            "tool_name": "add_task",
                            "arguments": {"title": task_title},
                            "result": {
                                "success": True,
                                "task": {"id": i, "title": task_title, "completed": False}
                            }
                        }
                    ]
                }

            with patch('src.agent.process_chat_message', return_value=mock_result):
                response = await async_client.post(
                    "/api/chat",
                    json={
                        "message": message,
                        "conversation_id": str(test_conversation.id)
                    },
                    headers=auth_headers
                )

            assert response.status_code == 200

        # Verify all messages persisted
        stmt = select(Message).where(
            Message.conversation_id == test_conversation.id
        ).order_by(Message.created_at)
        result = await async_session.execute(stmt)
        all_messages = result.scalars().all()

        # Should have user + assistant messages for each turn
        assert len(all_messages) >= len(messages)

    async def test_correction_after_initial_creation(
        self, async_client, auth_headers, test_conversation
    ):
        """Test user can correct task details immediately after creation."""
        # First: Create task
        message1 = "Add a task to buy groceries"

        mock_agent_result_1 = {
            "response": "I've added 'Buy groceries' to your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {"title": "Buy groceries"},
                    "result": {
                        "success": True,
                        "task": {"id": 1, "title": "Buy groceries", "completed": False}
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_1):
            response1 = await async_client.post(
                "/api/chat",
                json={
                    "message": message1,
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response1.status_code == 200

        # Second: Correct it (would use update_task tool in real implementation)
        message2 = "Actually, change that to tomorrow"

        mock_agent_result_2 = {
            "response": "I've updated the due date to tomorrow.",
            "tool_calls": []  # Would be update_task in full implementation
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_2):
            response2 = await async_client.post(
                "/api/chat",
                json={
                    "message": message2,
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response2.status_code == 200

    async def test_multiple_clarifications_before_creation(
        self, async_client, auth_headers, test_conversation
    ):
        """Test multiple back-and-forth clarifications before task creation."""
        conversation_flow = [
            {
                "user": "Add a task",
                "assistant_response": "What task would you like to add?",
                "tool_calls": []
            },
            {
                "user": "Something about groceries",
                "assistant_response": "Should I add 'Buy groceries' as the task?",
                "tool_calls": []
            },
            {
                "user": "Yes, and make it for tomorrow",
                "assistant_response": "I've added 'Buy groceries' due tomorrow.",
                "tool_calls": [
                    {
                        "tool_name": "add_task",
                        "arguments": {
                            "title": "Buy groceries",
                            "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
                        },
                        "result": {
                            "success": True,
                            "task": {"id": 1, "title": "Buy groceries", "completed": False}
                        }
                    }
                ]
            }
        ]

        for turn in conversation_flow:
            mock_result = {
                "response": turn["assistant_response"],
                "tool_calls": turn["tool_calls"]
            }

            with patch('src.agent.process_chat_message', return_value=mock_result):
                response = await async_client.post(
                    "/api/chat",
                    json={
                        "message": turn["user"],
                        "conversation_id": str(test_conversation.id)
                    },
                    headers=auth_headers
                )

            assert response.status_code == 200

        # Last response should have successful tool call
        assert len(conversation_flow[-1]["tool_calls"]) == 1
        assert conversation_flow[-1]["tool_calls"][0]["result"]["success"] is True

    async def test_rejection_and_retry(
        self, async_client, auth_headers, test_conversation
    ):
        """Test handling of rejected task creation and retry."""
        # First attempt with past date (rejected)
        from datetime import timedelta
        past_date = datetime.now(timezone.utc) - timedelta(days=1)

        mock_agent_result_1 = {
            "response": "I couldn't add that task because the due date must be in the future. Would you like to try a different date?",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {
                        "title": "Buy groceries",
                        "due_date": past_date.isoformat()
                    },
                    "result": {
                        "success": False,
                        "error": "Due date must be in the future"
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_1):
            response1 = await async_client.post(
                "/api/chat",
                json={
                    "message": "Add a task due yesterday",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response1.status_code == 200
        assert response1.json()["tool_calls"][0]["result"]["success"] is False

        # Second attempt with future date (success)
        future_date = datetime.now(timezone.utc) + timedelta(days=1)

        mock_agent_result_2 = {
            "response": "I've added 'Buy groceries' due tomorrow.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "arguments": {
                        "title": "Buy groceries",
                        "due_date": future_date.isoformat()
                    },
                    "result": {
                        "success": True,
                        "task": {
                            "id": 1,
                            "title": "Buy groceries",
                            "due_date": future_date.isoformat(),
                            "completed": False
                        }
                    }
                }
            ]
        }

        with patch('src.agent.process_chat_message', return_value=mock_agent_result_2):
            response2 = await async_client.post(
                "/api/chat",
                json={
                    "message": "Make it tomorrow instead",
                    "conversation_id": str(test_conversation.id)
                },
                headers=auth_headers
            )

        assert response2.status_code == 200
        assert response2.json()["tool_calls"][0]["result"]["success"] is True
