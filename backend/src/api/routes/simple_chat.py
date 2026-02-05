"""
Simple chat endpoint for Phase IV AI Chatbot without MCP dependencies.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import httpx

from ...db import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter()


class SimpleChatRequest(BaseModel):
    """Request model for simple chat endpoint"""
    message: str
    conversation_id: Optional[str] = None


class SimpleChatResponse(BaseModel):
    """Response model for simple chat endpoint"""
    response: str
    conversation_id: Optional[str] = None


@router.get("/api/debug-env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "NOT_SET"),
        "OPENAI_API_KEY": "***" if os.getenv("OPENAI_API_KEY") else "NOT_SET",
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "NOT_SET")
    }


@router.post("/api/simple-chat", response_model=SimpleChatResponse)
async def simple_chat(
    request: SimpleChatRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Simple chat endpoint that directly calls OpenRouter API
    """
    try:
        # Get OpenRouter configuration
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        model = "google/gemini-2.0-flash-001"  # Hardcoded to bypass env var issue
        
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenRouter API key not configured"
            )
        
        # Prepare the chat request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Todo Chatbot"
        }
        
        # Create a simple system prompt for task management
        system_prompt = """You are a helpful AI assistant for a Todo application. 
        You can help users manage their tasks, provide suggestions, and answer questions.
        Keep your responses concise and helpful."""
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        # Make request to OpenRouter
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"AI service error: {response.status_code}"
                )
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            return SimpleChatResponse(
                response=ai_response,
                conversation_id=request.conversation_id
            )
            
    except httpx.TimeoutException:
        logger.error("OpenRouter API timeout")
        raise HTTPException(
            status_code=500,
            detail="AI service timeout. Please try again."
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="I'm sorry, I encountered an error processing your request. Please try again."
        )