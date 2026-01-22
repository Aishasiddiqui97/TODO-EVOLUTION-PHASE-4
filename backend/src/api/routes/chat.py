"""
Stateless chat endpoint for Phase III AI Chatbot.
Handles user messages and returns AI responses.

Constitutional Requirements:
- Server MUST be stateless (no in-memory conversation state)
- Conversation history MUST be fetched from database each request
- Each request MUST be independent and self-contained
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json

from ...db import get_async_session
from ...ai.agent import agent
from ...mcp.server import mcp_server
from ...services.conversation_service import ConversationService
from ...services.message_service import MessageService
from ...auth.middleware import get_current_user_id
from ...auth.config import security

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    conversation_id: str
    response: str
    tool_calls: List[Dict[str, Any]] = []


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: int,
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_session),
    credentials = Depends(security)
):
    """
    Stateless chat endpoint for AI-powered todo management.

    Flow:
    1. Validate user authentication
    2. Fetch or create conversation from database
    3. Load conversation history from database
    4. Process message through AI agent
    5. Execute MCP tools if needed
    6. Persist messages to database
    7. Return response

    Args:
        user_id: User ID from path parameter
        request: Chat request with message and optional conversation_id
        session: Async database session
        credentials: JWT credentials for authentication

    Returns:
        ChatResponse with conversation_id, response, and tool_calls

    Raises:
        HTTPException: If authentication fails or processing error occurs
    """
    try:
        # Validate user authentication
        authenticated_user_id = await get_current_user_id(credentials)
        if authenticated_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's chat"
            )

        logger.info(f"Chat request from user {user_id}: {request.message[:50]}...")

        # Initialize services (stateless - no state stored)
        conversation_service = ConversationService(session)
        message_service = MessageService(session)

        # Step 1: Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.conversation_id,
                user_id
            )
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = await conversation_service.create_conversation(user_id)

        conversation_id = conversation.id

        # Step 2: Load conversation history from database (stateless)
        history = await message_service.get_conversation_history(
            conversation_id,
            limit=20  # Last 20 messages for context
        )

        # Convert to format expected by AI agent
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Step 3: Get available MCP tools
        tool_schemas = mcp_server.get_all_tool_schemas()

        # Step 4: Process message through AI agent
        agent_response = await agent.process_message(
            user_message=request.message,
            conversation_history=conversation_history,
            available_tools=tool_schemas
        )

        # Step 5: Execute MCP tools if agent requested them
        tool_results = []
        if agent_response.get("tool_calls"):
            for tool_call in agent_response["tool_calls"]:
                tool_name = tool_call["tool"]
                arguments = json.loads(tool_call["arguments"])

                # Execute tool through MCP server
                result = await mcp_server.execute_tool(tool_name, **arguments)
                tool_results.append({
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result
                })

        # Step 6: Generate final response with tool results
        if tool_results:
            final_response = await agent.generate_response_with_tool_results(
                original_message=request.message,
                tool_results=tool_results,
                conversation_history=conversation_history
            )
        else:
            final_response = agent_response["response"]

        # Step 7: Persist messages to database
        # Save user message
        await message_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Save assistant message with tool calls
        await message_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=final_response,
            tool_calls=tool_results if tool_results else None
        )

        # Update conversation last_message_at
        await conversation_service.update_last_message_time(conversation_id)

        logger.info(f"Chat response generated for user {user_id}, conversation {conversation_id}")

        # Return response
        return ChatResponse(
            conversation_id=conversation_id,
            response=final_response,
            tool_calls=tool_results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message. Please try again."
        )
