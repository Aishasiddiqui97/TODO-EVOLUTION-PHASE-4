"""
MCP (Model Context Protocol) Server for Phase III.
Provides a registry and execution framework for MCP tools.

The MCP server is stateless and provides tools that the AI agent can call
to perform task operations. All tools persist changes to the database immediately.
"""
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server that manages tool registration and execution.

    Constitutional Requirements:
    - Server is stateless (no in-memory state)
    - Tools are stateless functions
    - All state changes persist to database immediately
    """

    def __init__(self):
        """Initialize MCP server with empty tool registry"""
        self.tools: Dict[str, "MCPTool"] = {}
        logger.info("MCP Server initialized")

    def register_tool(self, tool: "MCPTool") -> None:
        """
        Register a tool with the MCP server.

        Args:
            tool: MCPTool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    async def execute_tool(
        self,
        tool_name: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute a registered tool by name.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool

        Returns:
            Tool execution result as dictionary

        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {
                "success": False,
                "error": "tool_not_found",
                "message": f"Tool '{tool_name}' is not registered"
            }

        tool = self.tools[tool_name]

        try:
            logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
            result = await tool.execute(**kwargs)
            logger.info(f"Tool {tool_name} executed successfully")
            return result

        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {str(e)}")
            return {
                "success": False,
                "error": "tool_execution_failed",
                "message": str(e)
            }

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the OpenAI function schema for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            OpenAI function schema or None if tool not found
        """
        if tool_name not in self.tools:
            return None

        return self.tools[tool_name].get_openai_schema()

    def get_all_tool_schemas(self) -> list[Dict[str, Any]]:
        """
        Get OpenAI function schemas for all registered tools.

        Returns:
            List of OpenAI function schemas
        """
        return [tool.get_openai_schema() for tool in self.tools.values()]


# Global MCP server instance (stateless - only holds tool registry)
mcp_server = MCPServer()
