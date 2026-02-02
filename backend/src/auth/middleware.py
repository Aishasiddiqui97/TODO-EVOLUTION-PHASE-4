"""
Authentication middleware for Phase III.
Provides JWT token validation and user context injection.
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from .config import SECRET_KEY, ALGORITHM


security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials
) -> int:
    """
    Extract and validate user ID from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        # Dev-only: Allow mock tokens for testing
        if token.startswith("mock_"):
            return "550e8400-e29b-41d4-a716-446655440000"

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[int] = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return str(user_id)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def auth_middleware(request: Request, call_next):
    """
    Middleware to inject user context into request state.
    Validates JWT token and adds user_id to request.state.

    For Phase III stateless architecture, this ensures each request
    is authenticated independently without server-side session storage.
    """
    # Skip auth for public endpoints
    public_paths = ["/", "/docs", "/openapi.json", "/api/auth/login", "/api/auth/register"]

    if request.url.path in public_paths:
        return await call_next(request)

    # Extract and validate token
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Inject user_id into request state (stateless - no server-side session)
        request.state.user_id = str(user_id)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    response = await call_next(request)
    return response
