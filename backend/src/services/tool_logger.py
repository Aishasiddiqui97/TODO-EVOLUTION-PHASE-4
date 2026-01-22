"""
Tool call logging service for Phase III.
Logs all MCP tool executions for debugging and monitoring.

Constitutional Requirements:
- Logging is stateless (writes to log files/database)
- All tool calls are logged for observability
- Logs include tool name, arguments, results, and timing
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ToolLogger:
    """
    Service for logging MCP tool calls.

    Provides observability into tool execution for debugging,
    monitoring, and analytics.
    """

    def __init__(self):
        """Initialize tool logger"""
        self.logger = logging.getLogger("mcp.tools")

    async def log_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        user_id: int,
        conversation_id: str,
        execution_time_ms: Optional[float] = None
    ) -> None:
        """
        Log a tool call with its arguments and result.

        Args:
            tool_name: Name of the tool that was called
            arguments: Arguments passed to the tool
            result: Result returned by the tool
            user_id: User who triggered the tool call
            conversation_id: Conversation context
            execution_time_ms: Tool execution time in milliseconds
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "execution_time_ms": execution_time_ms,
            "success": result.get("success", False)
        }

        # Log at appropriate level based on success
        if result.get("success"):
            self.logger.info(
                f"Tool call: {tool_name} | User: {user_id} | "
                f"Success: True | Time: {execution_time_ms}ms"
            )
        else:
            self.logger.error(
                f"Tool call: {tool_name} | User: {user_id} | "
                f"Success: False | Error: {result.get('error')}"
            )

        # Log full details at debug level
        self.logger.debug(f"Tool call details: {json.dumps(log_entry, indent=2)}")

    async def log_tool_error(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        error: Exception,
        user_id: int,
        conversation_id: str
    ) -> None:
        """
        Log a tool execution error.

        Args:
            tool_name: Name of the tool that failed
            arguments: Arguments passed to the tool
            error: Exception that occurred
            user_id: User who triggered the tool call
            conversation_id: Conversation context
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "arguments": arguments,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "conversation_id": conversation_id
        }

        self.logger.error(
            f"Tool error: {tool_name} | User: {user_id} | "
            f"Error: {type(error).__name__}: {str(error)}"
        )
        self.logger.debug(f"Tool error details: {json.dumps(log_entry, indent=2)}")

    async def log_tool_metrics(
        self,
        tool_name: str,
        execution_count: int,
        success_count: int,
        failure_count: int,
        avg_execution_time_ms: float
    ) -> None:
        """
        Log aggregated tool metrics.

        Args:
            tool_name: Name of the tool
            execution_count: Total number of executions
            success_count: Number of successful executions
            failure_count: Number of failed executions
            avg_execution_time_ms: Average execution time
        """
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "execution_count": execution_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / execution_count if execution_count > 0 else 0,
            "avg_execution_time_ms": avg_execution_time_ms
        }

        self.logger.info(
            f"Tool metrics: {tool_name} | "
            f"Executions: {execution_count} | "
            f"Success rate: {metrics['success_rate']:.2%} | "
            f"Avg time: {avg_execution_time_ms:.2f}ms"
        )
        self.logger.debug(f"Tool metrics details: {json.dumps(metrics, indent=2)}")


# Global tool logger instance
tool_logger = ToolLogger()


async def log_tool_call(
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
    user_id: int,
    conversation_id: str,
    execution_time_ms: Optional[float] = None
) -> None:
    """
    Log a tool call.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments
        result: Tool result
        user_id: User ID
        conversation_id: Conversation ID
        execution_time_ms: Execution time in milliseconds
    """
    await tool_logger.log_tool_call(
        tool_name,
        arguments,
        result,
        user_id,
        conversation_id,
        execution_time_ms
    )


async def log_tool_error(
    tool_name: str,
    arguments: Dict[str, Any],
    error: Exception,
    user_id: int,
    conversation_id: str
) -> None:
    """
    Log a tool error.

    Args:
        tool_name: Name of the tool
        arguments: Tool arguments
        error: Exception that occurred
        user_id: User ID
        conversation_id: Conversation ID
    """
    await tool_logger.log_tool_error(
        tool_name,
        arguments,
        error,
        user_id,
        conversation_id
    )
