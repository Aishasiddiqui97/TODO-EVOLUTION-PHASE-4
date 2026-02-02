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
    user_id: str,
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
    5. Execute MCP tools if needed (with shared DB session)
    6. Persist messages to database
    7. Return response

    Args:
        user_id: User ID from path parameter
        request: Chat request with message and optional conversation_id
        session: Async database session
        credentials: JWT credentials for authentication

    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    """
    logger.info(f"[CHAT] Request received from user {user_id}")
    logger.info(f"[CHAT] Message: {request.message[:100]}...")
    logger.info(f"[CHAT] Conversation ID: {request.conversation_id}")
    
    try:
        # Step 1: Validate user authentication
        logger.info("[CHAT] Step 1: Validating authentication")
        try:
            authenticated_user_id = await get_current_user_id(credentials)
            if str(authenticated_user_id) != user_id:
                logger.warning(f"[CHAT] Auth mismatch: {authenticated_user_id} != {user_id}")
                return ChatResponse(
                    conversation_id=request.conversation_id or "error",
                    response="❌ Authentication error: You don't have permission to access this chat.",
                    tool_calls=[]
                )
        except HTTPException as e:
            logger.error(f"[CHAT] Authentication failed: {e.detail}")
            return ChatResponse(
                conversation_id=request.conversation_id or "error",
                response=f"❌ Authentication failed: {e.detail}. Please login again.",
                tool_calls=[]
            )

        # Step 2: Validate message
        logger.info("[CHAT] Step 2: Validating message")
        if not request.message or not request.message.strip():
            logger.warning("[CHAT] Empty message received")
            return ChatResponse(
                conversation_id=request.conversation_id or "error",
                response="❌ Please provide a message.",
                tool_calls=[]
            )

        # Step 3: Initialize services (stateless - no state stored)
        logger.info("[CHAT] Step 3: Initializing services")
        conversation_service = ConversationService(session)
        message_service = MessageService(session)

        # Step 4: Get or create conversation
        logger.info("[CHAT] Step 4: Getting or creating conversation")
        conversation = None
        try:
            if request.conversation_id:
                logger.info(f"[CHAT] Fetching existing conversation: {request.conversation_id}")
                conversation = await conversation_service.get_conversation(
                    request.conversation_id,
                    user_id
                )
                if not conversation:
                    logger.warning(f"[CHAT] Conversation {request.conversation_id} not found")
                    return ChatResponse(
                        conversation_id=request.conversation_id,
                        response="❌ Conversation not found. Starting a new conversation.",
                        tool_calls=[]
                    )
            else:
                logger.info("[CHAT] Creating new conversation")
                conversation = await conversation_service.create_conversation(user_id)
                logger.info(f"[CHAT] Created conversation: {conversation.id}")
        except Exception as e:
            logger.error(f"[CHAT] Error in conversation handling: {str(e)}", exc_info=True)
            return ChatResponse(
                conversation_id=request.conversation_id or "error",
                response=f"❌ Database error: {str(e)}. Please try again.",
                tool_calls=[]
            )

        conversation_id = conversation.id

        # Step 5: Load conversation history from database (stateless)
        logger.info("[CHAT] Step 5: Loading conversation history")
        try:
            history = await message_service.get_conversation_history(
                conversation_id,
                limit=20  # Last 20 messages for context
            )
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in history
            ]
            logger.info(f"[CHAT] Loaded {len(conversation_history)} messages from history")
        except Exception as e:
            logger.error(f"[CHAT] Error loading history: {str(e)}", exc_info=True)
            conversation_history = []

        # Step 6: Get available MCP tools
        logger.info("[CHAT] Step 6: Getting MCP tool schemas")
        try:
            tool_schemas = mcp_server.get_all_tool_schemas()
            logger.info(f"[CHAT] Loaded {len(tool_schemas)} tool schemas")
        except Exception as e:
            logger.error(f"[CHAT] Error loading tool schemas: {str(e)}", exc_info=True)
            tool_schemas = []

        # Step 7: Process message through AI agent
        logger.info("[CHAT] Step 7: Processing message through AI agent")
        try:
            agent_response = await agent.process_message(
                user_message=request.message,
                conversation_history=conversation_history,
                available_tools=tool_schemas
            )
            logger.info(f"[CHAT] Agent response received, tool_calls: {len(agent_response.get('tool_calls', []))}")
        except Exception as e:
            logger.error(f"[CHAT] Agent processing failed: {str(e)}", exc_info=True)
            return ChatResponse(
                conversation_id=conversation_id,
                response=f"❌ AI agent error: {str(e)}. Please try rephrasing your message.",
                tool_calls=[]
            )

        # Step 8: Execute MCP tools if agent requested them
        logger.info("[CHAT] Step 8: Executing MCP tools")
        tool_results = []
        if agent_response.get("tool_calls"):
            for idx, tool_call in enumerate(agent_response["tool_calls"]):
                try:
                    tool_name = tool_call["tool"]
                    logger.info(f"[CHAT] Executing tool {idx+1}/{len(agent_response['tool_calls'])}: {tool_name}")
                    
                    # Parse arguments safely
                    try:
                        arguments = json.loads(tool_call["arguments"]) if isinstance(tool_call["arguments"], str) else tool_call["arguments"]
                    except json.JSONDecodeError as e:
                        logger.error(f"[CHAT] JSON parse error for tool {tool_name}: {str(e)}")
                        tool_results.append({
                            "tool": tool_name,
                            "arguments": {},
                            "result": {"success": False, "error": "invalid_arguments", "message": "Failed to parse tool arguments"}
                        })
                        continue

                    # CRITICAL: Inject user_id into tool arguments
                    arguments["user_id"] = user_id
                    logger.info(f"[CHAT] Tool arguments: {arguments}")

                    # Execute tool through MCP server with shared session
                    result = await mcp_server.execute_tool(
                        tool_name=tool_name,
                        session=session,  # Pass shared session
                        **arguments
                    )
                    logger.info(f"[CHAT] Tool {tool_name} result: {result.get('success', False)}")
                    
                    tool_results.append({
                        "tool": tool_name,
                        "arguments": arguments,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"[CHAT] Tool execution error for {tool_call.get('tool', 'unknown')}: {str(e)}", exc_info=True)
                    tool_results.append({
                        "tool": tool_call.get("tool", "unknown"),
                        "arguments": {},
                        "result": {"success": False, "error": "execution_failed", "message": str(e)}
                    })

        # Step 9: Generate final response with tool results
        logger.info("[CHAT] Step 9: Generating final response")
        try:
            if tool_results:
                final_response = await agent.generate_response_with_tool_results(
                    original_message=request.message,
                    tool_results=tool_results,
                    conversation_history=conversation_history
                )
            else:
                final_response = agent_response.get("response", "I'm here to help with your tasks!")
            logger.info(f"[CHAT] Final response generated: {final_response[:100]}...")
        except Exception as e:
            logger.error(f"[CHAT] Response generation failed: {str(e)}", exc_info=True)
            final_response = "I processed your request, but had trouble generating a response. Your action may have been completed."

        # Step 10: Persist messages to database
        logger.info("[CHAT] Step 10: Persisting messages to database")
        try:
            # Save user message
            await message_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=request.message
            )
            logger.info("[CHAT] User message saved")

            # Save assistant message with tool calls
            await message_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=final_response,
                tool_calls=tool_results if tool_results else None
            )
            logger.info("[CHAT] Assistant message saved")

            # Update conversation last_message_at
            await conversation_service.update_last_message_time(conversation_id)
            logger.info("[CHAT] Conversation timestamp updated")
        except Exception as e:
            logger.error(f"[CHAT] Error persisting messages: {str(e)}", exc_info=True)
            # Don't fail the request if message persistence fails
            # The user already got their response

        logger.info(f"[CHAT] Request completed successfully for conversation {conversation_id}")

        # Return response
        return ChatResponse(
            conversation_id=conversation_id,
            response=final_response,
            tool_calls=tool_results
        )

    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error(f"[CHAT] Unexpected error: {str(e)}", exc_info=True)
        return ChatResponse(
            conversation_id=request.conversation_id or "error",
            response=f"❌ An unexpected error occurred. Please try again. Error: {str(e)[:100]}",
            tool_calls=[]
        )

