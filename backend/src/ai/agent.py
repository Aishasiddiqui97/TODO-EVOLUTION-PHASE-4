"""
OpenAI Agents SDK integration for Phase III.
Provides AI agent initialization and tool calling capabilities.

Constitutional Requirements:
- AI agent MUST NOT directly access database
- All database operations MUST go through MCP tools
- Agent is stateless (no conversation state in memory)
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class TodoChatbotAgent:
    """
    AI Agent for Todo Chatbot using OpenAI Agents SDK.

    The agent interprets natural language, classifies intent,
    and calls appropriate MCP tools to perform task operations.
    """

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the Todo Chatbot agent.

        Args:
            model: OpenAI model to use (default: gpt-4-turbo-preview)
        """
        self.model = model
        self.system_prompt = self._get_system_prompt()
        logger.info(f"TodoChatbotAgent initialized with model: {model}")

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines agent behavior.

        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant for managing todo tasks through natural conversation.

Your capabilities:
- Create tasks from natural language descriptions
- List and filter tasks (all, today, pending, completed)
- Mark tasks as complete
- Update task details (title, due date, priority)
- Delete tasks
- Search and filter tasks by various criteria

Guidelines:
- Be conversational and friendly
- Confirm actions clearly (e.g., "I've added 'buy groceries' to your list")
- Ask clarifying questions when user intent is ambiguous
- Parse dates naturally (e.g., "tomorrow", "next Friday", "in 2 hours")
- Provide helpful suggestions when appropriate
- Handle errors gracefully with clear, actionable messages

Remember:
- Always confirm task operations
- Be specific about what was done
- If a task isn't found, suggest alternatives
- Keep responses concise but informative
"""

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        available_tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            available_tools: List of available MCP tools (OpenAI function format)

        Returns:
            Dictionary containing:
            - response: AI assistant's response text
            - tool_calls: List of tool calls made (if any)
            - finish_reason: Reason for completion
        """
        try:
            # Build messages array with system prompt and history
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API with function calling
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=available_tools if available_tools else None,
                tool_choice="auto" if available_tools else None,
                temperature=0.7,
                max_tokens=500
            )

            # Extract response
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            result = {
                "response": message.content or "",
                "tool_calls": [],
                "finish_reason": finish_reason
            }

            # Extract tool calls if present
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "tool": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                    for tool_call in message.tool_calls
                ]

            logger.info(f"Agent processed message, tool_calls: {len(result['tool_calls'])}")
            return result

        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "finish_reason": "error",
                "error": str(e)
            }

    async def generate_response_with_tool_results(
        self,
        original_message: str,
        tool_results: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a final response after tool execution.

        Args:
            original_message: The original user message
            tool_results: Results from executed tools
            conversation_history: Previous conversation messages

        Returns:
            Final response text
        """
        try:
            # Build context with tool results
            tool_context = "\n".join([
                f"Tool: {result['tool']}, Result: {result['result']}"
                for result in tool_results
            ])

            messages = [
                {"role": "system", "content": self.system_prompt},
                *conversation_history,
                {"role": "user", "content": original_message},
                {"role": "assistant", "content": f"[Tool execution results: {tool_context}]"},
                {"role": "user", "content": "Based on the tool results, provide a friendly response to the user."}
            ]

            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            return response.choices[0].message.content or "Operation completed."

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "Operation completed, but I had trouble generating a response."


# Global agent instance
agent = TodoChatbotAgent()
