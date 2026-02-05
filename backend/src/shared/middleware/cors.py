"""
CORS configuration middleware for Chat API.

Provides flexible CORS configuration for different environments.
"""

from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import logging

logger = logging.getLogger(__name__)


def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.

    Returns:
        List of allowed origins
    """
    environment = os.getenv("ENVIRONMENT", "local")

    if environment == "production":
        # Production: Only allow specific domains
        origins = [
            "https://todo-chatbot.example.com",
            "https://www.todo-chatbot.example.com",
            "https://app.todo-chatbot.example.com"
        ]
    elif environment == "staging":
        # Staging: Allow staging domains
        origins = [
            "https://staging.todo-chatbot.example.com",
            "https://staging-app.todo-chatbot.example.com"
        ]
    else:
        # Local/Development: Allow localhost
        origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8000",
            "http://localhost:8001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ]

    # Allow additional origins from environment variable
    additional_origins = os.getenv("CORS_ORIGINS", "")
    if additional_origins:
        origins.extend(additional_origins.split(","))

    logger.info(f"CORS origins configured: {origins}")
    return origins


def configure_cors(app):
    """
    Configure CORS middleware for FastAPI application.

    Args:
        app: FastAPI application instance
    """
    origins = get_cors_origins()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-User-ID",
            "X-Request-ID",
            "X-Correlation-ID"
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-Request-ID"
        ],
        max_age=3600  # Cache preflight requests for 1 hour
    )

    logger.info("CORS middleware configured successfully")
