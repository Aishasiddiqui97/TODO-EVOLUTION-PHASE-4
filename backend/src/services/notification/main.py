"""
Notification Service Main Application.

Microservice that listens for reminder events and sends notifications
via email and in-app channels.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...shared.utils.logging import setup_logging
from ...shared.dapr_client.client import DaprClientWrapper

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Environment variables
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_GRPC_PORT = os.getenv("DAPR_GRPC_PORT", "50001")
APP_PORT = int(os.getenv("APP_PORT", "8003"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Notification Service", extra={
        "dapr_http_port": DAPR_HTTP_PORT,
        "dapr_grpc_port": DAPR_GRPC_PORT,
        "app_port": APP_PORT
    })

    # Verify Dapr connection
    try:
        dapr_client = DaprClientWrapper()
        logger.info("Dapr client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Dapr client: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Notification Service")


# Create FastAPI application
app = FastAPI(
    title="Event-Driven Todo Chatbot - Notification Service",
    description="Microservice for sending task reminders and notifications",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.
    """
    return {
        "status": "healthy",
        "service": "notification",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "notification",
        "version": "1.0.0",
        "description": "Notification Service for Event-Driven Todo Chatbot",
        "endpoints": {
            "health": "/health",
            "events": "/dapr/subscribe"
        }
    }


# Include routers
from .handlers.reminder_due import router as reminder_router
from .routes.health import router as health_router

app.include_router(reminder_router)
app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        log_level="info",
        reload=False
    )
