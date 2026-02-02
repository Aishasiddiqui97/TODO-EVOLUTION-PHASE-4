"""
Base class for MCP tools in Phase III.
All tools must inherit from this base class and implement the execute method.

Constitutional Requirements:
- Tools MUST be stateless functions
- Tools MUST persist state changes to database immediately
- Tools MUST NOT store any state in memory
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MCPTool(ABC):
    """
    Abstract base class for MCP tools.

    Each tool represents a single operation that the AI agent can perform.
    Tools are stateless and interact with the database through services.
    """

    def __init__(self):
        """Initialize the tool"""
        self.name = self.get_name()
        self.description = self.get_description()
        self.parameters = self.get_parameters()

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the tool name (used for registration and calling).

        Returns:
            Tool name (e.g., "add_task", "list_tasks")
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get the tool description for the AI agent.

        Returns:
            Human-readable description of what the tool does
        """
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the tool parameters schema (OpenAI function format).

        Returns:
            Parameters schema as dictionary
        """
        pass

    @abstractmethod
    async def execute(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the tool with given parameters and database session.

        Args:
            session: Database session for stateless operations
            **kwargs: Tool-specific parameters

        Returns:
            Result dictionary with:
            - success: bool (True if operation succeeded)
            - data: Any (operation result data)
            - error: str (error code if failed)
            - message: str (human-readable message)
        """
        pass

    def get_openai_schema(self) -> Dict[str, Any]:
        """
        Get the OpenAI function calling schema for this tool.

        Returns:
            OpenAI function schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def _success_response(
        self,
        data: Any,
        message: str = "Operation completed successfully"
    ) -> Dict[str, Any]:
        """
        Create a success response.

        Args:
            data: Result data
            message: Success message

        Returns:
            Success response dictionary
        """
        return {
            "success": True,
            "data": data,
            "message": message
        }

    def _error_response(
        self,
        error: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Create an error response.

        Args:
            error: Error code
            message: Error message

        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "error": error,
            "message": message
        }
