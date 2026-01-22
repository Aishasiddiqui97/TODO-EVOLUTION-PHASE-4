"""
MCP Tool Registry for Phase III.
Centralized registry for all MCP tools used by the AI agent.

This module initializes and registers all available tools with the MCP server.
"""
from .server import mcp_server
from .tools.base import MCPTool
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Tool registry that manages tool lifecycle and registration.

    Constitutional Requirements:
    - Registry is stateless (only holds tool references)
    - Tools are registered at startup
    - No runtime state is maintained
    """

    def __init__(self):
        """Initialize the tool registry"""
        self.registered_tools = []

    def register(self, tool: MCPTool) -> None:
        """
        Register a tool with the MCP server.

        Args:
            tool: MCPTool instance to register
        """
        mcp_server.register_tool(tool)
        self.registered_tools.append(tool.name)
        logger.info(f"Tool registered: {tool.name}")

    def register_all(self) -> None:
        """
        Register all available tools.

        This method will be called at application startup to register
        all Phase III tools with the MCP server.
        """
        # Import tools here to avoid circular imports
        # Tools will be implemented in Phase 3 (User Story 1)
        # from .tools.add_task import AddTaskTool
        # from .tools.list_tasks import ListTasksTool
        # from .tools.complete_task import CompleteTaskTool
        # from .tools.update_task import UpdateTaskTool
        # from .tools.delete_task import DeleteTaskTool

        # Register tools
        # self.register(AddTaskTool())
        # self.register(ListTasksTool())
        # self.register(CompleteTaskTool())
        # self.register(UpdateTaskTool())
        # self.register(DeleteTaskTool())

        logger.info(f"Registered {len(self.registered_tools)} tools")

    def get_registered_tools(self) -> list[str]:
        """
        Get list of registered tool names.

        Returns:
            List of tool names
        """
        return self.registered_tools


# Global registry instance
registry = ToolRegistry()


def initialize_tools() -> None:
    """
    Initialize and register all MCP tools.
    Called at application startup.
    """
    logger.info("Initializing MCP tools...")
    registry.register_all()
    logger.info("MCP tools initialized successfully")
