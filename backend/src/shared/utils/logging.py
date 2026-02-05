"""
Structured logging utility for Event-Driven Todo Chatbot.

Provides consistent JSON logging across all services.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """Structured JSON logger for consistent logging across services."""

    def __init__(self, service_name: str, level: int = logging.INFO):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(level)

        # Remove existing handlers
        self.logger.handlers = []

        # Add JSON handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(service_name))
        self.logger.addHandler(handler)

    def log_event(self, event_type: str, **kwargs) -> None:
        """
        Log an event with structured data.

        Args:
            event_type: Type of event (e.g., "task.created")
            **kwargs: Additional fields to include in log
        """
        self.logger.info(
            json.dumps({
                "eventType": event_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **kwargs
            })
        )

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in ["name", "msg", "args", "created", "filename", "funcName",
                               "levelname", "levelno", "lineno", "module", "msecs",
                               "message", "pathname", "process", "processName",
                               "relativeCreated", "thread", "threadName", "exc_info",
                               "exc_text", "stack_info"]:
                    log_data[key] = value

        return json.dumps(log_data)


def setup_logging(service_name: str = "chat-api", level: int = logging.INFO) -> None:
    """
    Setup structured logging for the application.

    Args:
        service_name: Name of the service
        level: Logging level
    """
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Create structured logger for the service
    logger = StructuredLogger(service_name, level)

    return logger
