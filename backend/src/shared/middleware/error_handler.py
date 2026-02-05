"""
Error handling middleware for all services.

Provides consistent error handling and logging across services.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.

    Catches all exceptions and returns consistent error responses.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request with error handling.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response
        """
        # Generate request ID for tracing
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        except HTTPException as exc:
            # FastAPI HTTP exceptions - pass through with request ID
            logger.warning(
                f"HTTP exception: {exc.status_code} - {exc.detail}",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )

        except ValueError as exc:
            # Validation errors
            logger.error(
                f"Validation error: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation error",
                    "message": str(exc),
                    "status_code": 400,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )

        except Exception as exc:
            # Unexpected errors
            error_trace = traceback.format_exc()
            logger.error(
                f"Unhandled exception: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": error_trace
                },
                exc_info=True
            )

            # Don't expose internal errors in production
            error_message = "Internal server error"
            error_details = None

            # Include details in development
            import os
            if os.getenv("ENVIRONMENT") != "production":
                error_message = str(exc)
                error_details = error_trace

            return JSONResponse(
                status_code=500,
                content={
                    "error": error_message,
                    "details": error_details,
                    "status_code": 500,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )


def configure_error_handling(app):
    """
    Configure error handling for FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)

    # Custom exception handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "message": f"The requested resource was not found: {request.url.path}",
                "status_code": 404,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method not allowed",
                "message": f"Method {request.method} not allowed for {request.url.path}",
                "status_code": 405,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )

    logger.info("Error handling configured successfully")
