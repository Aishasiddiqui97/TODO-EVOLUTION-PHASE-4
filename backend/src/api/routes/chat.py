"""
Chat API Routes for Event-Driven Todo Chatbot.

Provides conversational interface using OpenAI Agents SDK with MCP tools.
"""

import os
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ...mcp.tools.create_task import create_task, CreateTaskInput
from ...mcp.tools.update_task import update_task, UpdateTaskInput
from ...mcp.tools.complete_task import complete_task, CompleteTaskInput
from ...mcp.tools.delete_task import delete_task, DeleteTaskInput
from ...mcp.tools.list_tasks import list_tasks, ListTasksInput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# Temporary: Hardcoded user ID for MVP
TEMP_USER_ID = "user-001"


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000)
    conversationId: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    conversationId: str
    toolCalls: Optional[List[dict]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat message and return AI response.

    This endpoint uses OpenAI Agents SDK to process natural language
    and execute task management operations through MCP tools.

    Args:
        request: Chat request with user message

    Returns:
        AI response with conversation ID
    """
    try:
        # TODO: Implement OpenAI Agents SDK integration in T046
        # For now, return a simple echo response

        logger.info(f"Received chat message: {request.message[:100]}")

        # Simple keyword-based routing for MVP demonstration
        message_lower = request.message.lower()

        response_message = "I'm your AI task assistant. I can help you create, update, list, complete, and delete tasks. What would you like to do?"
        tool_calls = []

        # Basic intent detection (will be replaced by OpenAI Agents SDK)
        if any(word in message_lower for word in ["create", "add", "new task"]):
            response_message = "I can help you create a task. Please provide the task title and any additional details like priority, due date, or tags."

        elif any(word in message_lower for word in ["list", "show", "what tasks", "my tasks"]):
            # Demonstrate list_tasks tool
            try:
                result = await list_tasks(ListTasksInput(
                    userId=TEMP_USER_ID,
                    limit=10
                ))

                if result.success and result.count > 0:
                    task_list = "\n".join([f"- {task['title']} (Priority: {task['priority']}, Status: {task['status']})"
                                          for task in result.tasks[:5]])
                    response_message = f"Here are your tasks:\n{task_list}"
                    if result.count > 5:
                        response_message += f"\n\n...and {result.count - 5} more tasks."
                else:
                    response_message = "You don't have any tasks yet. Would you like to create one?"

                tool_calls.append({
                    "tool": "list_tasks",
                    "result": "success"
                })
            except Exception as e:
                logger.error(f"Error listing tasks: {e}", exc_info=True)
                response_message = "I encountered an error while listing your tasks. Please try again."

        elif any(word in message_lower for word in ["complete", "done", "finish"]):
            response_message = "I can help you mark a task as complete. Which task would you like to complete? Please provide the task title or ID."

        elif any(word in message_lower for word in ["delete", "remove"]):
            response_message = "I can help you delete a task. Which task would you like to delete? Please provide the task title or ID."

        elif any(word in message_lower for word in ["update", "change", "modify"]):
            response_message = "I can help you update a task. Which task would you like to update, and what changes would you like to make?"

        # Generate or use conversation ID
        conversation_id = request.conversationId or f"conv-{TEMP_USER_ID}-{os.urandom(4).hex()}"

        return ChatResponse(
            message=response_message,
            conversationId=conversation_id,
            toolCalls=tool_calls if tool_calls else None
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Retrieve conversation history.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation history
    """
    # TODO: Implement conversation history retrieval from Dapr State API
    return {
        "conversationId": conversation_id,
        "messages": [],
        "message": "Conversation history not yet implemented"
    }


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    """
    Delete conversation history.

    Args:
        conversation_id: Conversation ID

    Returns:
        No content
    """
    # TODO: Implement conversation deletion from Dapr State API
    return None
