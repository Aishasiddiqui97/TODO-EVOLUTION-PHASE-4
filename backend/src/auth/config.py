"""
Authentication configuration for Phase III.
Extends Phase II auth with session management for stateless chat.
"""
import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY = os.getenv("AUTH_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS Configuration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# Session Configuration
SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = timedelta(days=7)

# Better Auth Configuration (for future enhancement)
BETTER_AUTH_ENABLED = os.getenv("BETTER_AUTH_ENABLED", "false").lower() == "true"
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "")
