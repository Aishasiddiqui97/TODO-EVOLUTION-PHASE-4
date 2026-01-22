"""
Error handling framework for Phase III AI agent.
Provides AI-friendly error messages and graceful error handling.

Constitutional Requirements:
- Errors MUST be handled gracefully without exposing technical details
- Error messages MUST be clear, actionable, and user-friendly
- Common errors MUST have specific, helpful messages
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ErrorCode:
    """Error codes for common failure scenarios"""
    TASK_NOT_FOUND = "task_not_found"
    INVALID_INPUT = "invalid_input"
    TOOL_FAILURE = "tool_failure"
    DATABASE_ERROR = "database_error"
    AI_SERVICE_ERROR = "ai_service_error"
    AUTHENTICATION_ERROR = "authentication_error"
    UNKNOWN_ERROR = "unknown_error"


class AIErrorHandler:
    """
    Error handler that converts technical errors into AI-friendly messages.

    The AI agent uses these messages to provide helpful responses to users
    without exposing technical implementation details.
    """

    def __init__(self):
        """Initialize error handler with message templates"""
        self.error_messages = {
            ErrorCode.TASK_NOT_FOUND: {
                "message": "I couldn't find that task. Could you be more specific or try listing your tasks?",
                "suggestions": [
                    "Try: 'Show me all my tasks'",
                    "Try: 'What's on my list?'"
                ]
            },
            ErrorCode.INVALID_INPUT: {
                "message": "I didn't quite understand that. Could you rephrase your request?",
                "suggestions": [
                    "Try being more specific about what you want to do",
                    "Example: 'Add buy groceries to my list'"
                ]
            },
            ErrorCode.TOOL_FAILURE: {
                "message": "Something went wrong while processing your request. Please try again.",
                "suggestions": [
                    "Try rephrasing your request",
                    "If the problem persists, try a simpler operation"
                ]
            },
            ErrorCode.DATABASE_ERROR: {
                "message": "I'm having trouble accessing your tasks right now. Please try again in a moment.",
                "suggestions": [
                    "Wait a moment and try again",
                    "Check your internet connection"
                ]
            },
            ErrorCode.AI_SERVICE_ERROR: {
                "message": "I'm having trouble understanding right now. Please try again.",
                "suggestions": [
                    "Try rephrasing your request",
                    "Use simpler language"
                ]
            },
            ErrorCode.AUTHENTICATION_ERROR: {
                "message": "I need you to log in first before I can help with your tasks.",
                "suggestions": [
                    "Please log in to your account",
                    "Check if your session has expired"
                ]
            },
            ErrorCode.UNKNOWN_ERROR: {
                "message": "Something unexpected happened. Please try again.",
                "suggestions": [
                    "Try your request again",
                    "If the problem continues, contact support"
                ]
            }
        }

    def handle_error(
        self,
        error_code: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and return an AI-friendly response.

        Args:
            error_code: Error code from ErrorCode class
            context: Optional context information about the error

        Returns:
            Dictionary with:
            - error_code: The error code
            - message: User-friendly error message
            - suggestions: List of helpful suggestions
            - context: Optional context information
        """
        error_info = self.error_messages.get(
            error_code,
            self.error_messages[ErrorCode.UNKNOWN_ERROR]
        )

        response = {
            "error_code": error_code,
            "message": error_info["message"],
            "suggestions": error_info["suggestions"]
        }

        if context:
            response["context"] = context

        logger.info(f"Handled error: {error_code}, context: {context}")
        return response

    def handle_task_not_found(
        self,
        task_reference: str,
        available_tasks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Handle task not found error with specific context.

        Args:
            task_reference: What the user referenced
            available_tasks: List of available task titles (optional)

        Returns:
            Error response with suggestions
        """
        message = f"I couldn't find a task matching '{task_reference}'."

        suggestions = ["Try: 'Show me all my tasks'"]

        if available_tasks:
            suggestions.append(f"You have {len(available_tasks)} tasks. Try listing them first.")

        return {
            "error_code": ErrorCode.TASK_NOT_FOUND,
            "message": message,
            "suggestions": suggestions,
            "context": {
                "task_reference": task_reference,
                "available_count": len(available_tasks) if available_tasks else 0
            }
        }

    def handle_ambiguous_request(
        self,
        clarification_needed: str
    ) -> Dict[str, Any]:
        """
        Handle ambiguous user request that needs clarification.

        Args:
            clarification_needed: What needs to be clarified

        Returns:
            Response asking for clarification
        """
        return {
            "error_code": ErrorCode.INVALID_INPUT,
            "message": f"I need more information: {clarification_needed}",
            "suggestions": [
                "Please provide more details",
                "Be more specific about what you want"
            ]
        }

    def format_for_ai_response(self, error_response: Dict[str, Any]) -> str:
        """
        Format error response for AI agent to use in conversation.

        Args:
            error_response: Error response dictionary

        Returns:
            Formatted string for AI response
        """
        message = error_response["message"]
        suggestions = error_response.get("suggestions", [])

        if suggestions:
            formatted_suggestions = "\n".join(f"- {s}" for s in suggestions)
            return f"{message}\n\n{formatted_suggestions}"

        return message


# Global error handler instance
error_handler = AIErrorHandler()


def handle_error(
    error_code: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handle an error and return an AI-friendly response.

    Args:
        error_code: Error code from ErrorCode class
        context: Optional context information

    Returns:
        Error response dictionary
    """
    return error_handler.handle_error(error_code, context)


def handle_task_not_found(
    task_reference: str,
    available_tasks: Optional[list] = None
) -> Dict[str, Any]:
    """
    Handle task not found error.

    Args:
        task_reference: What the user referenced
        available_tasks: List of available tasks

    Returns:
        Error response dictionary
    """
    return error_handler.handle_task_not_found(task_reference, available_tasks)
