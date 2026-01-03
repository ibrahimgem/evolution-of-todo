"""Unit tests for MCP tool registry."""
import pytest
from src.mcp.mcp_server import MCPToolRegistry


@pytest.mark.unit
def test_mcp_registry_initialization():
    """Test MCP registry initializes correctly."""
    registry = MCPToolRegistry()
    assert registry.tool_count() == 0
    assert registry.list_tool_names() == []


@pytest.mark.unit
def test_register_tool():
    """Test registering a tool with the registry."""
    registry = MCPToolRegistry()

    async def dummy_handler(args, context):
        return {"success": True}

    registry.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {}},
        handler=dummy_handler
    )

    assert registry.tool_count() == 1
    assert "test_tool" in registry.list_tool_names()


@pytest.mark.unit
def test_get_tool():
    """Test retrieving a registered tool."""
    registry = MCPToolRegistry()

    async def dummy_handler(args, context):
        return {"success": True}

    registry.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {}},
        handler=dummy_handler
    )

    tool = registry.get_tool("test_tool")
    assert tool is not None
    assert tool["name"] == "test_tool"
    assert tool["description"] == "A test tool"


@pytest.mark.unit
def test_get_nonexistent_tool():
    """Test retrieving a tool that doesn't exist."""
    registry = MCPToolRegistry()
    tool = registry.get_tool("nonexistent")
    assert tool is None


@pytest.mark.unit
def test_get_all_tools_openai_format():
    """Test getting all tools in OpenAI function calling format."""
    registry = MCPToolRegistry()

    async def dummy_handler(args, context):
        return {"success": True}

    registry.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={
            "type": "object",
            "properties": {
                "arg1": {"type": "string"}
            }
        },
        handler=dummy_handler
    )

    tools = registry.get_all_tools()
    assert len(tools) == 1
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "test_tool"
    assert tools[0]["function"]["description"] == "A test tool"
    assert "parameters" in tools[0]["function"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_tool_success():
    """Test successful tool execution."""
    registry = MCPToolRegistry()

    async def dummy_handler(args, context):
        return {"success": True, "result": args.get("input")}

    registry.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object", "properties": {}},
        handler=dummy_handler
    )

    context = {"user_id": 1, "request_id": "test"}
    result = await registry.execute_tool("test_tool", {"input": "hello"}, context)

    assert result["success"] is True
    assert result["result"] == "hello"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_nonexistent_tool():
    """Test executing a tool that doesn't exist."""
    registry = MCPToolRegistry()
    context = {"user_id": 1, "request_id": "test"}
    result = await registry.execute_tool("nonexistent", {}, context)

    assert result["success"] is False
    assert "not found" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_tool_with_error():
    """Test tool execution with handler error."""
    registry = MCPToolRegistry()

    async def failing_handler(args, context):
        raise ValueError("Test error")

    registry.register_tool(
        name="failing_tool",
        description="A failing tool",
        input_schema={"type": "object", "properties": {}},
        handler=failing_handler
    )

    context = {"user_id": 1, "request_id": "test"}
    result = await registry.execute_tool("failing_tool", {}, context)

    assert result["success"] is False
    assert "Test error" in result["error"]
