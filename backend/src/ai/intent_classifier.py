"""
Intent classification system for Phase III.
Classifies user intent from natural language input.

This module provides intent detection to help the AI agent
understand what operation the user wants to perform.
"""
from enum import Enum
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """
    User intent types for task management operations.
    """
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    SEARCH_TASKS = "search_tasks"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Rule-based intent classifier with keyword matching.

    This provides a fallback classification system in addition to
    the AI agent's natural language understanding.
    """

    def __init__(self):
        """Initialize the intent classifier with keyword patterns"""
        self.patterns = {
            Intent.CREATE_TASK: [
                r'\b(add|create|new|make|remind|remember)\b.*\b(task|todo|item)\b',
                r'\b(add|create)\b',
                r'\bremind me\b',
                r'\bdon\'t forget\b',
            ],
            Intent.LIST_TASKS: [
                r'\b(show|list|display|view|what|get)\b.*\b(task|todo|list)\b',
                r'\bwhat\'s on my\b',
                r'\bshow me\b',
                r'\bwhat do i need\b',
            ],
            Intent.COMPLETE_TASK: [
                r'\b(complete|done|finish|mark|check)\b.*\b(task|todo|item)\b',
                r'\bmark.*as (done|complete)\b',
                r'\bi (finished|completed|did)\b',
            ],
            Intent.UPDATE_TASK: [
                r'\b(update|change|modify|edit|move)\b.*\b(task|todo|item)\b',
                r'\bchange.*to\b',
                r'\bmove.*to\b',
            ],
            Intent.DELETE_TASK: [
                r'\b(delete|remove|cancel|drop)\b.*\b(task|todo|item)\b',
                r'\bget rid of\b',
                r'\bremove.*from\b',
            ],
            Intent.SEARCH_TASKS: [
                r'\b(find|search|filter|show me)\b.*\b(task|todo)\b',
                r'\bhigh priority\b',
                r'\bwork related\b',
            ],
        }

    def classify(self, text: str) -> Intent:
        """
        Classify user intent from text using keyword matching.

        Args:
            text: User's message text

        Returns:
            Classified intent
        """
        text_lower = text.lower()

        # Check each intent pattern
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    logger.info(f"Classified intent: {intent} from text: {text[:50]}...")
                    return intent

        logger.info(f"Could not classify intent from text: {text[:50]}...")
        return Intent.UNKNOWN

    def get_confidence(self, text: str, intent: Intent) -> float:
        """
        Get confidence score for a classified intent.

        Args:
            text: User's message text
            intent: Classified intent

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if intent == Intent.UNKNOWN:
            return 0.0

        text_lower = text.lower()
        patterns = self.patterns.get(intent, [])

        # Count matching patterns
        matches = sum(1 for pattern in patterns if re.search(pattern, text_lower))

        # Calculate confidence based on number of matches
        confidence = min(matches / len(patterns), 1.0) if patterns else 0.0

        return confidence


# Global classifier instance
classifier = IntentClassifier()


def classify_intent(text: str) -> Intent:
    """
    Classify user intent from text.

    Args:
        text: User's message text

    Returns:
        Classified intent
    """
    return classifier.classify(text)


def get_intent_confidence(text: str, intent: Intent) -> float:
    """
    Get confidence score for a classified intent.

    Args:
        text: User's message text
        intent: Classified intent

    Returns:
        Confidence score (0.0 to 1.0)
    """
    return classifier.get_confidence(text, intent)
