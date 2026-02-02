from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from the correct location
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

from .api.routes.tasks import router as tasks_router
from .api.routes.auth import router as auth_router
from .api.routes.chat import router as chat_router

app = FastAPI(title="Evolution of Todo - Phase II API", version="1.0.0")

# Add CORS middleware to allow frontend to connect
# IMPORTANT: Cannot use allow_origins=["*"] with allow_credentials=True
# Must specify explicit origins for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Explicit origins, not "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the task routes
app.include_router(tasks_router, prefix="/api", tags=["tasks"])

# Include the auth routes
app.include_router(auth_router, prefix="/api", tags=["auth"])

# Include the chat routes (Phase III)
app.include_router(chat_router, tags=["chat"])


@app.on_event("startup")
async def startup_event():
    """Initialize MCP tools on application startup"""
    # Temporarily disabled to fix indentation issues
    # from .mcp.registry import initialize_tools
    # initialize_tools()
    pass


@app.get("/")
def read_root():
    return {"message": "Evolution of Todo - Phase III API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}