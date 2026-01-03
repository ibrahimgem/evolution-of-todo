---
name: openai-agents-sdk
description: Integrate OpenAI Agents SDK for building conversational AI agents with tool calling capabilities. Use when implementing AI agents, managing conversation state, processing natural language with tools, or building chatbot backends. Covers agent initialization, tool registration, conversation management, streaming responses, and error handling.
---

# OpenAI Agents SDK

## Overview

Build intelligent conversational AI agents using OpenAI Agents SDK in Python FastAPI applications. This skill covers agent initialization, tool registration, conversation state management, streaming responses, and integration with MCP tools.

## Quick Start

### Installation

```bash
pip install openai
```

### Basic Agent Setup

```python
# backend/src/agent.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def create_agent_response(message: str, conversation_history: list):
    """Create agent response with conversation context"""

    # Append user message to history
    messages = conversation_history + [
        {"role": "user", "content": message}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
```

## Agent Configuration

### System Prompt Design

```python
# backend/src/agent.py
SYSTEM_PROMPT = """You are an AI assistant that helps users manage their todo tasks through natural conversation.

You have access to the following tools:
- add_task: Create new tasks
- list_tasks: View tasks with optional filtering
- complete_task: Mark tasks as done
- delete_task: Remove tasks
- update_task: Modify task details

Guidelines:
1. Parse user intent from natural language
2. Extract task details (title, description, due dates)
3. Call appropriate tools to complete operations
4. Provide clear, friendly responses
5. Confirm actions and show results

Examples:
User: "Add a task to buy groceries tomorrow"
You: Call add_task(title="Buy groceries", due_date="2025-01-02")

User: "Show me my incomplete tasks"
You: Call list_tasks(status="incomplete")
"""

def get_system_message():
    """Get system prompt for agent"""
    return {"role": "system", "content": SYSTEM_PROMPT}
```

### Agent with Tools

```python
# backend/src/agent.py
from .mcp_server import get_mcp_tools

# Convert MCP tools to OpenAI format
def convert_mcp_to_openai_tools(mcp_tools):
    """Convert MCP tools to OpenAI function calling format"""
    return [
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

# Get tools
mcp_tools = get_mcp_tools()
openai_tools = convert_mcp_to_openai_tools(mcp_tools)

async def create_agent_with_tools(message: str, conversation_history: list, user_id: int):
    """Create agent response with tool execution"""

    # Build messages with system prompt
    messages = [get_system_message()] + conversation_history + [
        {"role": "user", "content": message}
    ]

    # Call agent with tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        tool_results = await execute_tool_calls(
            assistant_message.tool_calls,
            user_id
        )

        # Add assistant message with tool calls to history
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [tc.dict() for tc in assistant_message.tool_calls]
        })

        # Add tool results to history
        for tool_result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call_id"],
                "content": json.dumps(tool_result["result"])
            })

        # Get final response with tool results
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        return {
            "content": final_response.choices[0].message.content,
            "tool_calls": tool_results
        }

    return {
        "content": assistant_message.content,
        "tool_calls": []
    }
```

## Tool Execution

### Execute Tool Calls

```python
# backend/src/agent.py
from .mcp_server import execute_mcp_tool
import json

async def execute_tool_calls(tool_calls, user_id: int):
    """Execute all tool calls from agent"""
    results = []

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Execute MCP tool with user context
        result = await execute_mcp_tool(
            tool_name=function_name,
            tool_input=function_args,
            context={"user_id": user_id}
        )

        results.append({
            "tool_call_id": tool_call.id,
            "tool_name": function_name,
            "result": result
        })

    return results
```

## Conversation Management

### Load Conversation History

```python
# backend/src/agent.py
from sqlmodel import select
from .models import Message

async def load_conversation_history(conversation_id: str, limit: int = 20):
    """Load recent messages from database"""
    async with AsyncSession(async_engine) as session:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        results = await session.execute(statement)
        messages = results.scalars().all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        # Convert to OpenAI format
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {})
            }
            for msg in messages
        ]
```

### Save Messages

```python
# backend/src/agent.py
from .models import Message, Conversation

async def save_message(
    conversation_id: str,
    role: str,
    content: str,
    tool_calls: list = None
):
    """Save message to database"""
    async with AsyncSession(async_engine) as session:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        session.add(message)
        await session.commit()

async def save_conversation_turn(
    conversation_id: str,
    user_message: str,
    assistant_message: str,
    tool_calls: list = None
):
    """Save complete conversation turn"""
    # Save user message
    await save_message(conversation_id, "user", user_message)

    # Save assistant message with tool calls
    await save_message(
        conversation_id,
        "assistant",
        assistant_message,
        tool_calls
    )
```

## Streaming Responses

### Stream Agent Output

```python
# backend/src/agent.py
from typing import AsyncGenerator

async def stream_agent_response(
    message: str,
    conversation_history: list,
    user_id: int
) -> AsyncGenerator[str, None]:
    """Stream agent responses chunk by chunk"""

    messages = [get_system_message()] + conversation_history + [
        {"role": "user", "content": message}
    ]

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto",
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

        # Handle tool calls in streaming
        if chunk.choices[0].delta.tool_calls:
            # Collect tool calls
            tool_calls = chunk.choices[0].delta.tool_calls
            # Execute tools and stream results
            yield "\n\nExecuting tools...\n"
            results = await execute_tool_calls(tool_calls, user_id)
            for result in results:
                yield f"\n✓ {result['tool_name']}: {result['result']}\n"
```

### FastAPI Streaming Endpoint

```python
# backend/src/routes/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Stream chat responses"""

    # Load conversation history
    history = await load_conversation_history(request.conversation_id)

    # Create streaming response
    async def generate():
        async for chunk in stream_agent_response(
            request.message,
            history,
            current_user.id
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Error Handling

### Rate Limiting

```python
# backend/src/agent.py
from openai import RateLimitError
import asyncio

async def create_agent_with_retry(message: str, history: list, user_id: int, max_retries: int = 3):
    """Create agent response with retry logic"""

    for attempt in range(max_retries):
        try:
            return await create_agent_with_tools(message, history, user_id)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)

    raise Exception("Max retries exceeded")
```

### API Errors

```python
# backend/src/agent.py
from openai import OpenAIError

async def safe_agent_call(message: str, history: list, user_id: int):
    """Call agent with comprehensive error handling"""

    try:
        return await create_agent_with_retry(message, history, user_id)
    except RateLimitError:
        return {
            "error": "Rate limit exceeded. Please try again in a moment.",
            "type": "rate_limit"
        }
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "error": "AI service temporarily unavailable. Please try again.",
            "type": "api_error"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "error": "An unexpected error occurred.",
            "type": "internal_error"
        }
```

## Complete Integration

```python
# backend/src/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: list

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Main chat endpoint with agent"""

    # Create or load conversation
    if not request.conversation_id:
        conversation = await create_conversation(current_user.id)
        conversation_id = conversation.id
    else:
        conversation_id = request.conversation_id

    # Load conversation history
    history = await load_conversation_history(conversation_id)

    # Call agent with tools
    result = await safe_agent_call(
        request.message,
        history,
        current_user.id
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Save conversation turn
    await save_conversation_turn(
        conversation_id,
        request.message,
        result["content"],
        result.get("tool_calls")
    )

    return ChatResponse(
        response=result["content"],
        conversation_id=conversation_id,
        tool_calls=result.get("tool_calls", [])
    )
```

## Best Practices

1. **System Prompts**: Design clear, specific system prompts with examples
2. **Context Window**: Limit conversation history to last 20-30 messages
3. **Tool Descriptions**: Write clear, unambiguous tool descriptions
4. **Error Handling**: Implement retry logic with exponential backoff
5. **Streaming**: Use streaming for better UX on long responses
6. **State Management**: Always persist conversations to database
7. **Token Management**: Monitor token usage and implement limits
8. **Testing**: Test agent with various natural language inputs
9. **Logging**: Log all agent calls and tool executions
10. **Security**: Validate user permissions before tool execution

## Common Patterns

**Multi-turn Conversations**:
```python
# Keep last N messages
MAX_HISTORY = 20
history = history[-MAX_HISTORY:]
```

**Conversation Starters**:
```python
CONVERSATION_STARTERS = [
    "What tasks do you have for today?",
    "Add a new task",
    "Show my incomplete tasks"
]
```

**Intent Detection**:
```python
# Let agent determine intent from natural language
# Agent will call appropriate tools based on user message
```

**Fallback Responses**:
```python
if not response.choices[0].message.content:
    return "I'm not sure how to help with that. Can you rephrase?"
```
