"""OpenAI agent client for conversational AI with tool calling."""
from dotenv import load_dotenv
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from openai import AsyncOpenAI
from .mcp.mcp_server import get_mcp_registry

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM client (supports OpenAI, Groq, or Gemini)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

# Configure client based on available API keys (priority: Groq > OpenAI > Gemini)
if GROQ_API_KEY:
    # Groq (free tier) - OpenAI-compatible API with fast inference
    logger.info("Initializing Groq client (OpenAI-compatible mode)")
    openai_client = AsyncOpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    DEFAULT_MODEL = LLM_MODEL or "llama-3.3-70b-versatile"
elif OPENAI_API_KEY:
    # Standard OpenAI client
    logger.info("Initializing OpenAI client")
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    DEFAULT_MODEL = LLM_MODEL or "gpt-4o-mini"
elif GEMINI_API_KEY:
    # Google Gemini (requires native SDK - this won't work with OpenAI SDK)
    logger.warning("GEMINI_API_KEY detected but not supported. Please use GROQ_API_KEY or OPENAI_API_KEY instead.")
    openai_client = None
    DEFAULT_MODEL = "gpt-4o-mini"
else:
    logger.warning("No LLM API key set (GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY) - agent will not be able to make API calls")
    openai_client = None
    DEFAULT_MODEL = "gpt-4o-mini"

# System prompt for the AI agent
SYSTEM_PROMPT = """You are a helpful AI assistant that helps users manage their todo tasks through natural conversation.

**Your Capabilities:**
You have access to the following tools to manage tasks:
- add_task: Create a new task with title, optional description, and optional due date
- list_tasks: Retrieve tasks with optional filtering (all, complete, incomplete)
- complete_task: Mark a task as complete or incomplete
- delete_task: Permanently delete a task
- update_task: Update task fields (title, description, due_date)

**Guidelines:**
1. **Natural Language Processing**: Understand user intent from conversational language
   - "Buy groceries tomorrow" → extract title "Buy groceries" and due_date (tomorrow)
   - "Show my incomplete tasks" → use list_tasks with status="incomplete"
   - "Mark task 5 as done" → use complete_task with task_id=5 and completed=true

2. **Date Parsing**: Convert natural language dates to ISO8601 format
   - "tomorrow" → calculate next day and format as "YYYY-MM-DDTHH:MM:SSZ"
   - "next Monday" → find next Monday date
   - "in 3 days" → add 3 days to current date
   - Always use UTC timezone

3. **Task Identification**: Help users identify tasks when ambiguous
   - If user says "delete the grocery task" but there are multiple, ask for clarification
   - Use task titles from list_tasks results to help disambiguate

4. **Error Handling**: Provide friendly error messages
   - If tool fails, explain what went wrong in simple terms
   - Suggest alternatives when operations fail

5. **Confirmation**: Confirm actions with specifics
   - "I've added 'Buy groceries' to your tasks for tomorrow (Jan 2, 2026)"
   - "You have 5 incomplete tasks and 3 completed tasks"

6. **Tool Calling**: Always use tools for task operations
   - Never invent or make up task data
   - Always call the appropriate tool for user requests
   - Wait for tool results before responding

**Response Format:**
- Be concise and friendly
- Provide specific details (task IDs, dates, counts)
- Ask clarifying questions when needed
- Acknowledge successful operations clearly

Remember: You are stateless. All conversation history is provided in the messages array. All task data comes from tool calls - never make up information."""


async def get_agent_response(
    user_message: str,
    conversation_history: List[Dict[str, Any]],
    user_id: int,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get response from LLM agent with tool calling support.
    Supports both OpenAI and Google Gemini (via OpenAI-compatible API).

    Args:
        user_message: User's current message
        conversation_history: Previous messages in conversation
        user_id: Authenticated user ID for tool execution context
        model: LLM model to use (defaults to gemini-1.5-flash or gpt-4o-mini based on API key)

    Returns:
        Dictionary containing:
        - response: AI's text response
        - tool_calls: List of tool executions [{tool_name, result}]
        - error: Error message if request failed

    Raises:
        Exception: If OpenAI API call fails
    """
    if not openai_client:
        logger.error("LLM client not initialized - missing API key")
        return {
            "response": "I'm unable to process your request right now. Please try again later.",
            "tool_calls": [],
            "error": "LLM API key not configured"
        }

    # Use default model if not specified
    if model is None:
        model = DEFAULT_MODEL

    try:
        # Build message history with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (if any)
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Get available tools from MCP registry
        mcp_registry = get_mcp_registry()
        tools = mcp_registry.get_all_tools()

        logger.info(
            f"Sending request to LLM (model={model}) with {len(messages)} messages "
            f"and {len(tools)} tools for user {user_id}"
        )

        # Call LLM with function calling (OpenAI-compatible API)
        # Build API call parameters
        api_params = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Only add tools and tool_choice if tools are available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        response = await openai_client.chat.completions.create(**api_params)

        assistant_message = response.choices[0].message
        tool_calls_data = []

        # Execute tool calls if any
        if assistant_message.tool_calls:
            logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool call(s)")

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                # Parse tool arguments
                import json
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments: {e}")
                    arguments = {}

                # Execute tool with context
                context = {
                    "user_id": user_id,
                    "request_id": f"{user_id}_{datetime.now(timezone.utc).timestamp()}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                result = await mcp_registry.execute_tool(tool_name, arguments, context)

                tool_calls_data.append({
                    "tool_name": tool_name,
                    "result": result
                })

            # Get final response from agent after tool execution
            # Add tool results to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Add tool results
            for i, tool_call in enumerate(assistant_message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_calls_data[i]["result"])
                })

            # Get final response
            final_response = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            final_message = final_response.choices[0].message.content

        else:
            # No tool calls, use direct response
            final_message = assistant_message.content

        logger.info(f"Agent response generated successfully with {len(tool_calls_data)} tool call(s)")

        return {
            "response": final_message or "I'm here to help with your tasks!",
            "tool_calls": tool_calls_data,
            "error": None
        }

    except Exception as e:
        logger.error(f"OpenAI agent error: {type(e).__name__}: {str(e)}", exc_info=True)
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "tool_calls": [],
            "error": str(e)
        }


def get_openai_client() -> AsyncOpenAI:
    """
    Get the OpenAI client instance.

    Returns:
        AsyncOpenAI client

    Raises:
        RuntimeError: If client not initialized
    """
    if not openai_client:
        raise RuntimeError("OpenAI client not initialized - OPENAI_API_KEY not set")
    return openai_client
