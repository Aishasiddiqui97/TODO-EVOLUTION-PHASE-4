"""
Natural language date parser for Phase III.
Parses dates and times from natural language input.

Uses dateparser library for robust date parsing with support for
relative dates like "tomorrow", "next Friday", "in 2 hours", etc.
"""
from datetime import datetime, timedelta
from typing import Optional
import dateparser
import logging

logger = logging.getLogger(__name__)


class DateParser:
    """
    Natural language date parser for task due dates.

    Supports various date formats:
    - Absolute: "January 15", "2026-01-25", "Friday"
    - Relative: "tomorrow", "next week", "in 3 days"
    - Time: "at 3pm", "in 2 hours", "tonight"
    """

    def __init__(self):
        """Initialize the date parser with default settings"""
        self.settings = {
            'PREFER_DATES_FROM': 'future',  # Prefer future dates
            'RETURN_AS_TIMEZONE_AWARE': False,
            'RELATIVE_BASE': datetime.utcnow()
        }

    def parse(self, text: str) -> Optional[datetime]:
        """
        Parse a date/time from natural language text.

        Args:
            text: Natural language date/time string

        Returns:
            Parsed datetime object or None if parsing failed

        Examples:
            >>> parser.parse("tomorrow")
            datetime(2026, 1, 23, 0, 0, 0)
            >>> parser.parse("next Friday at 3pm")
            datetime(2026, 1, 24, 15, 0, 0)
            >>> parser.parse("in 2 hours")
            datetime(2026, 1, 22, 15, 0, 0)
        """
        try:
            parsed_date = dateparser.parse(text, settings=self.settings)

            if parsed_date:
                logger.info(f"Parsed date '{text}' -> {parsed_date}")
                return parsed_date
            else:
                logger.warning(f"Could not parse date from: {text}")
                return None

        except Exception as e:
            logger.error(f"Date parsing error for '{text}': {str(e)}")
            return None

    def parse_with_context(
        self,
        text: str,
        base_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Parse a date with a specific base date for relative parsing.

        Args:
            text: Natural language date/time string
            base_date: Base date for relative parsing (default: now)

        Returns:
            Parsed datetime object or None if parsing failed
        """
        settings = self.settings.copy()
        if base_date:
            settings['RELATIVE_BASE'] = base_date

        try:
            parsed_date = dateparser.parse(text, settings=settings)

            if parsed_date:
                logger.info(f"Parsed date '{text}' with base {base_date} -> {parsed_date}")
                return parsed_date
            else:
                logger.warning(f"Could not parse date from: {text}")
                return None

        except Exception as e:
            logger.error(f"Date parsing error for '{text}': {str(e)}")
            return None

    def extract_date_from_text(self, text: str) -> Optional[datetime]:
        """
        Extract a date from a longer text string.

        Args:
            text: Text that may contain a date reference

        Returns:
            Extracted datetime or None if no date found

        Examples:
            >>> parser.extract_date_from_text("Remind me to buy groceries tomorrow")
            datetime(2026, 1, 23, 0, 0, 0)
            >>> parser.extract_date_from_text("Call mom next Friday at 3pm")
            datetime(2026, 1, 24, 15, 0, 0)
        """
        # Common date-related keywords
        date_keywords = [
            'tomorrow', 'today', 'tonight', 'yesterday',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'next', 'this', 'last',
            'week', 'month', 'year',
            'at', 'by', 'on', 'in'
        ]

        # Check if text contains date keywords
        text_lower = text.lower()
        has_date_keyword = any(keyword in text_lower for keyword in date_keywords)

        if not has_date_keyword:
            return None

        # Try to parse the entire text
        return self.parse(text)

    def is_valid_future_date(self, date: datetime) -> bool:
        """
        Check if a date is in the future.

        Args:
            date: Datetime to check

        Returns:
            True if date is in the future
        """
        return date > datetime.utcnow()


# Global parser instance
date_parser = DateParser()


def parse_date(text: str) -> Optional[datetime]:
    """
    Parse a date from natural language text.

    Args:
        text: Natural language date/time string

    Returns:
        Parsed datetime object or None if parsing failed
    """
    return date_parser.parse(text)


def extract_date_from_text(text: str) -> Optional[datetime]:
    """
    Extract a date from a longer text string.

    Args:
        text: Text that may contain a date reference

    Returns:
        Extracted datetime or None if no date found
    """
    return date_parser.extract_date_from_text(text)
