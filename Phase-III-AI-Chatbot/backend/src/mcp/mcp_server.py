"""MCP (Model Context Protocol) server for registering and managing tools."""
import logging
from typing import Dict, Callable, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry for MCP tools that can be called by the AI agent."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Dict[str, Any]] = {}
        logger.info("MCP Tool Registry initialized")

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: Callable,
    ) -> None:
        """
        Register a new tool with the MCP server.

        Args:
            name: Unique tool name (e.g., "add_task")
            description: Human-readable description for the AI
            input_schema: JSON schema defining tool inputs
            handler: Async function that executes the tool logic
        """
        if name in self._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")

        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "handler": handler,
        }
        logger.info(f"Registered MCP tool: {name}")

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool metadata by name.

        Args:
            name: Tool name

        Returns:
            Tool metadata dictionary or None if not found
        """
        return self._tools.get(name)

    def get_all_tools(self) -> list[Dict[str, Any]]:
        """
        Get all registered tools for OpenAI function calling.

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        tools = []
        for tool_name, tool_data in self._tools.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_data["name"],
                    "description": tool_data["description"],
                    "parameters": tool_data["input_schema"],
                }
            })
        return tools

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        context: dict
    ) -> dict:
        """
        Execute a registered tool with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Input arguments for the tool
            context: Execution context (user_id, request_id, timestamp)

        Returns:
            Tool execution result dictionary

        Raises:
            ValueError: If tool not found
        """
        tool = self.get_tool(tool_name)
        if not tool:
            logger.error(f"Tool '{tool_name}' not found in registry")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        try:
            logger.info(
                f"Executing tool '{tool_name}' for user {context.get('user_id')} "
                f"with args: {list(arguments.keys())}"
            )
            start_time = datetime.now(timezone.utc)

            # Execute the tool handler
            result = await tool["handler"](arguments, context)

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                f"Tool '{tool_name}' executed successfully in {execution_time:.3f}s "
                f"- success: {result.get('success', False)}"
            )

            return result

        except Exception as e:
            logger.error(
                f"Tool '{tool_name}' execution failed: {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }

    def list_tool_names(self) -> list[str]:
        """
        Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def tool_count(self) -> int:
        """
        Get total number of registered tools.

        Returns:
            Count of registered tools
        """
        return len(self._tools)


# Global MCP tool registry instance
mcp_registry = MCPToolRegistry()


def get_mcp_registry() -> MCPToolRegistry:
    """
    Get the global MCP tool registry instance.

    Returns:
        MCPToolRegistry instance
    """
    return mcp_registry
