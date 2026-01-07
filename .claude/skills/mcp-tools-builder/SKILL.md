---
name: mcp-tools-builder
description: Build Model Context Protocol (MCP) tools for AI agents using the official MCP SDK in Python. Use when implementing MCP server tools, defining tool schemas, handling tool execution, or integrating tools with OpenAI Agents SDK. Covers tool registration, input validation, error handling, and async patterns.
---

# MCP Tools Builder

## Overview

Implement standardized Model Context Protocol (MCP) tools that enable AI agents to interact with your application. This skill covers MCP server setup, tool schema definition, input validation, execution patterns, and integration with OpenAI Agents SDK.

## Quick Start

### Installation

```bash
pip install mcp
```

### Basic MCP Tool

```python
# backend/src/mcp_tools/add_task.py
from mcp import Tool
from pydantic import BaseModel, Field
from typing import Optional

class AddTaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    due_date: Optional[str] = Field(None, description="Due date in ISO8601 format")

@Tool.register(
    name="add_task",
    description="Create a new task for the user",
    input_schema=AddTaskInput
)
async def add_task(input: AddTaskInput, context: dict) -> dict:
    """Create a new task in the database"""
    user_id = context.get("user_id")

    # Validate due_date if provided
    if input.due_date:
        try:
            due_date_obj = datetime.fromisoformat(input.due_date)
            if due_date_obj < datetime.now(timezone.utc):
                raise ValueError("Due date must be in the future")
        except ValueError as e:
            return {"error": str(e), "success": False}

    # Create task in database
    task = await create_task_in_db(
        user_id=user_id,
        title=input.title,
        description=input.description,
        due_date=input.due_date
    )

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "created_at": task.created_at.isoformat()
        }
    }
```

## MCP Server Setup

### Initialize MCP Server

```python
# backend/src/mcp_server.py
from mcp import MCPServer
from .mcp_tools import add_task, list_tasks, complete_task, delete_task, update_task

# Initialize MCP server
mcp_server = MCPServer(
    name="todo-mcp-server",
    version="1.0.0"
)

# Register all tools
mcp_server.register_tool(add_task)
mcp_server.register_tool(list_tasks)
mcp_server.register_tool(complete_task)
mcp_server.register_tool(delete_task)
mcp_server.register_tool(update_task)

# Export for agent integration
def get_mcp_tools():
    """Get all registered MCP tools for agent"""
    return mcp_server.get_tools()
```

## Core Tool Patterns

### 1. List/Query Tool

```python
# backend/src/mcp_tools/list_tasks.py
from enum import Enum

class TaskStatus(str, Enum):
    ALL = "all"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"

class ListTasksInput(BaseModel):
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by completion status")
    limit: int = Field(50, ge=1, le=100, description="Maximum tasks to return")
    offset: int = Field(0, ge=0, description="Pagination offset")

@Tool.register(
    name="list_tasks",
    description="Retrieve user's tasks with optional filtering and pagination",
    input_schema=ListTasksInput
)
async def list_tasks(input: ListTasksInput, context: dict) -> dict:
    """Query tasks from database with filtering"""
    user_id = context.get("user_id")

    tasks = await query_tasks_from_db(
        user_id=user_id,
        status=input.status,
        limit=input.limit,
        offset=input.offset
    )

    return {
        "success": True,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ],
        "total": len(tasks),
        "offset": input.offset,
        "limit": input.limit
    }
```

### 2. Update Tool

```python
# backend/src/mcp_tools/complete_task.py
class CompleteTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to update")
    completed: bool = Field(..., description="Completion status")

@Tool.register(
    name="complete_task",
    description="Mark a task as complete or incomplete",
    input_schema=CompleteTaskInput
)
async def complete_task(input: CompleteTaskInput, context: dict) -> dict:
    """Update task completion status"""
    user_id = context.get("user_id")

    # Verify task exists and belongs to user
    task = await get_task_from_db(input.task_id, user_id)
    if not task:
        return {
            "success": False,
            "error": f"Task {input.task_id} not found or access denied"
        }

    # Update task
    updated_task = await update_task_status_in_db(
        task_id=input.task_id,
        completed=input.completed
    )

    return {
        "success": True,
        "task": {
            "id": updated_task.id,
            "title": updated_task.title,
            "completed": updated_task.completed,
            "updated_at": updated_task.updated_at.isoformat()
        }
    }
```

### 3. Delete Tool

```python
# backend/src/mcp_tools/delete_task.py
class DeleteTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to delete")

@Tool.register(
    name="delete_task",
    description="Permanently delete a task",
    input_schema=DeleteTaskInput
)
async def delete_task(input: DeleteTaskInput, context: dict) -> dict:
    """Delete task from database"""
    user_id = context.get("user_id")

    # Verify ownership before deletion
    task = await get_task_from_db(input.task_id, user_id)
    if not task:
        return {
            "success": False,
            "error": f"Task {input.task_id} not found or access denied"
        }

    await delete_task_from_db(input.task_id)

    return {
        "success": True,
        "message": f"Task {input.task_id} deleted successfully",
        "deleted_task_id": input.task_id
    }
```

### 4. Partial Update Tool

```python
# backend/src/mcp_tools/update_task.py
class UpdateTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[str] = Field(None, description="ISO8601 format")

@Tool.register(
    name="update_task",
    description="Update task fields (partial update supported)",
    input_schema=UpdateTaskInput
)
async def update_task(input: UpdateTaskInput, context: dict) -> dict:
    """Update task with partial field changes"""
    user_id = context.get("user_id")

    # Verify at least one field is provided
    if not any([input.title, input.description, input.due_date]):
        return {
            "success": False,
            "error": "At least one field (title, description, due_date) must be provided"
        }

    # Verify task exists and belongs to user
    task = await get_task_from_db(input.task_id, user_id)
    if not task:
        return {
            "success": False,
            "error": f"Task {input.task_id} not found or access denied"
        }

    # Validate due_date if provided
    if input.due_date:
        try:
            due_date_obj = datetime.fromisoformat(input.due_date)
            if due_date_obj < datetime.now(timezone.utc):
                return {"success": False, "error": "Due date must be in the future"}
        except ValueError:
            return {"success": False, "error": "Invalid due_date format"}

    # Update only provided fields
    update_data = {}
    if input.title is not None:
        update_data["title"] = input.title
    if input.description is not None:
        update_data["description"] = input.description
    if input.due_date is not None:
        update_data["due_date"] = input.due_date

    updated_task = await update_task_in_db(input.task_id, update_data)

    return {
        "success": True,
        "task": {
            "id": updated_task.id,
            "title": updated_task.title,
            "description": updated_task.description,
            "due_date": updated_task.due_date,
            "updated_at": updated_task.updated_at.isoformat()
        }
    }
```

## Integration with OpenAI Agents SDK

### Register Tools with Agent

```python
# backend/src/agent.py
from openai import OpenAI
from .mcp_server import get_mcp_tools

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get MCP tools
mcp_tools = get_mcp_tools()

# Convert to OpenAI tool format
openai_tools = [
    {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema.model_json_schema()
        }
    }
    for tool in mcp_tools
]

async def process_message(message: str, conversation_id: str, user_id: int):
    """Process message with agent and execute tools"""

    # Load conversation history
    messages = await load_conversation_history(conversation_id)
    messages.append({"role": "user", "content": message})

    # Call agent with tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )

    # Execute tool calls
    tool_results = []
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            result = await execute_mcp_tool(
                tool_name=tool_call.function.name,
                tool_input=json.loads(tool_call.function.arguments),
                context={"user_id": user_id}
            )
            tool_results.append({
                "tool_call_id": tool_call.id,
                "result": result
            })

    return {
        "response": response.choices[0].message.content,
        "tool_calls": tool_results
    }
```

### Tool Execution Handler

```python
# backend/src/mcp_server.py
async def execute_mcp_tool(tool_name: str, tool_input: dict, context: dict) -> dict:
    """Execute MCP tool by name with input and context"""
    tool = mcp_server.get_tool(tool_name)
    if not tool:
        return {"success": False, "error": f"Tool {tool_name} not found"}

    try:
        # Validate input against schema
        validated_input = tool.input_schema(**tool_input)

        # Execute tool
        result = await tool.execute(validated_input, context)
        return result
    except ValidationError as e:
        return {"success": False, "error": f"Input validation failed: {e}"}
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return {"success": False, "error": "Tool execution failed"}
```

## Error Handling Patterns

### Input Validation Errors

```python
from pydantic import BaseModel, validator

class AddTaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[str] = None

    @validator('due_date')
    def validate_due_date(cls, v):
        if v:
            try:
                date_obj = datetime.fromisoformat(v)
                if date_obj < datetime.now(timezone.utc):
                    raise ValueError("Due date must be in the future")
            except ValueError as e:
                raise ValueError(f"Invalid due_date: {e}")
        return v
```

### Database Errors

```python
@Tool.register(name="add_task", ...)
async def add_task(input: AddTaskInput, context: dict) -> dict:
    try:
        task = await create_task_in_db(...)
        return {"success": True, "task": task}
    except IntegrityError:
        return {"success": False, "error": "Task already exists"}
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return {"success": False, "error": "Database operation failed"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {"success": False, "error": "An unexpected error occurred"}
```

### Permission Errors

```python
async def verify_task_ownership(task_id: int, user_id: int) -> Optional[Task]:
    """Verify task belongs to user"""
    task = await get_task_from_db(task_id)
    if not task or task.user_id != user_id:
        return None
    return task

@Tool.register(name="delete_task", ...)
async def delete_task(input: DeleteTaskInput, context: dict) -> dict:
    user_id = context.get("user_id")
    task = await verify_task_ownership(input.task_id, user_id)

    if not task:
        return {
            "success": False,
            "error": "Task not found or access denied"
        }

    await delete_task_from_db(input.task_id)
    return {"success": True}
```

## Testing MCP Tools

```python
# tests/test_mcp_tools.py
import pytest
from src.mcp_tools.add_task import add_task, AddTaskInput

@pytest.mark.asyncio
async def test_add_task_success():
    input_data = AddTaskInput(
        title="Test task",
        description="Test description"
    )
    context = {"user_id": 1}

    result = await add_task(input_data, context)

    assert result["success"] is True
    assert result["task"]["title"] == "Test task"
    assert "id" in result["task"]

@pytest.mark.asyncio
async def test_add_task_invalid_due_date():
    input_data = AddTaskInput(
        title="Test task",
        due_date="2020-01-01T00:00:00Z"  # Past date
    )
    context = {"user_id": 1}

    result = await add_task(input_data, context)

    assert result["success"] is False
    assert "due date" in result["error"].lower()
```

## Best Practices

1. **Input Validation**: Use Pydantic models with validators for all inputs
2. **Error Responses**: Always return structured error responses with `success` field
3. **Context Passing**: Include user_id and other auth context in tool execution
4. **Async Patterns**: Use async/await for all database operations
5. **Logging**: Log tool executions and errors for debugging
6. **Idempotency**: Design tools to be idempotent where possible
7. **Transaction Support**: Wrap database operations in transactions
8. **Testing**: Write unit tests for each tool with various input scenarios
9. **Documentation**: Include clear descriptions for tools and parameters
10. **Security**: Always validate user permissions before executing operations

## Common Patterns

**Date Parsing**:
```python
from datetime import datetime, timezone

def parse_iso_date(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")
```

**Pagination**:
```python
class PaginationInput(BaseModel):
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
```

**Filtering**:
```python
class FilterInput(BaseModel):
    status: Optional[str] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
```

## Tool Schema Best Practices

- Use clear, descriptive names (verbs for actions)
- Include comprehensive descriptions
- Set appropriate constraints (min/max lengths, ranges)
- Use Optional[] for non-required fields
- Provide default values where sensible
- Add Field descriptions for all parameters
- Use enums for fixed choices
