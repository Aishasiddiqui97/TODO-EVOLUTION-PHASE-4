# Quickstart Guide: AI-Powered Todo Chatbot (Phase III)

**Date**: 2026-01-22
**Feature**: 003-ai-chatbot-mcp
**Purpose**: Local development setup and testing guide

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **Git**: Latest version
- **PostgreSQL**: 15+ (or Neon account)

### Required Accounts
- **OpenAI**: API key for Agents SDK
- **Neon**: Database account (or local PostgreSQL)
- **Better Auth**: Configuration (or use local auth)

---

## Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/Aishasiddiqui97/TODO-EVOLUTION-PHASE-2.git
cd TODO-EVOLUTION-PHASE-2
git checkout 003-ai-chatbot-mcp
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required: DATABASE_URL, OPENAI_API_KEY, AUTH_SECRET
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# (Optional) Seed test data
python scripts/seed_data.py
```

### 4. Start Backend

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --port 8001

# Backend will be available at: http://localhost:8001
# API docs at: http://localhost:8001/docs
```

### 5. Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 6. Start Frontend

```bash
npm run dev

# Frontend will be available at: http://localhost:3000
```

### 7. Test the Chatbot

1. Open browser: http://localhost:3000
2. Register a new account
3. Navigate to chat interface
4. Try: "Add buy groceries to my list"
5. Try: "What's on my todo list?"

---

## Detailed Setup

### Backend Configuration

#### Environment Variables (.env)

```bash
# Database (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql://user:password@host/database

# OpenAI API
OPENAI_API_KEY=sk-...

# Authentication
AUTH_SECRET=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000

# MCP Configuration
MCP_SERVER_PORT=8002

# Optional: Logging
LOG_LEVEL=INFO
```

#### Database Connection

**Option 1: Neon Serverless (Recommended)**
```bash
# Sign up at https://neon.tech
# Create a new project
# Copy connection string to DATABASE_URL
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb
```

**Option 2: Local PostgreSQL**
```bash
# Install PostgreSQL
# Create database
createdb todo_chatbot

# Set connection string
DATABASE_URL=postgresql://localhost/todo_chatbot
```

#### Run Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

#### Seed Test Data (Optional)

```bash
# Create seed script: scripts/seed_data.py
python scripts/seed_data.py

# This creates:
# - Test user (email: test@example.com, password: password123)
# - Sample tasks
# - Sample conversation
```

---

### Frontend Configuration

#### Environment Variables (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001

# Better Auth (if using)
NEXT_PUBLIC_AUTH_URL=http://localhost:8001/api/auth

# Optional: Analytics
NEXT_PUBLIC_ANALYTICS_ID=
```

#### Install Dependencies

```bash
npm install

# Key dependencies:
# - next@16.1.3
# - react@19.2.3
# - @openai/chatkit (for chat UI)
# - axios (for API calls)
```

#### Development Server

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

---

## Testing the Application

### Manual Testing Scenarios

#### Scenario 1: Create Task
1. Open chat: http://localhost:3000/chat
2. Type: "Add buy groceries to my list"
3. Expected: Task created confirmation
4. Verify: Check database or ask "What's on my list?"

#### Scenario 2: View Tasks
1. Type: "What do I need to do today?"
2. Expected: List of tasks due today
3. Type: "Show me all my tasks"
4. Expected: Complete task list

#### Scenario 3: Complete Task
1. Type: "Mark 'buy groceries' as done"
2. Expected: Task marked complete confirmation
3. Verify: Ask "Show me pending tasks"

#### Scenario 4: Update Task
1. Type: "Change the groceries task to 'buy milk and eggs'"
2. Expected: Task updated confirmation
3. Verify: Ask "What's on my list?"

#### Scenario 5: Delete Task
1. Type: "Delete the milk task"
2. Expected: Task deleted confirmation
3. Verify: Task no longer in list

#### Scenario 6: Conversation Resume
1. Close browser
2. Reopen and login
3. Previous conversation should be available
4. Type: "What did we talk about?"
5. Expected: AI remembers previous context

---

### API Testing with curl

#### Test Chat Endpoint

```bash
# Login first
TOKEN=$(curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8001/api/123/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add buy groceries to my list"
  }' | jq

# Expected response:
# {
#   "conversation_id": "uuid",
#   "response": "I've added 'buy groceries' to your list.",
#   "tool_calls": [...]
# }
```

#### Test MCP Tools Directly

```bash
# Test add_task tool
curl -X POST http://localhost:8002/mcp/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "due_date": "2026-01-23"
  }' | jq
```

---

## Development Workflow

### 1. Start Development Environment

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Database (if local)
psql todo_chatbot
```

### 2. Make Changes

**Backend Changes**:
- Edit files in `backend/src/`
- FastAPI auto-reloads on save
- Check logs in Terminal 1

**Frontend Changes**:
- Edit files in `frontend/src/`
- Next.js auto-reloads on save
- Check browser console for errors

**Database Changes**:
- Create migration: `alembic revision --autogenerate -m "description"`
- Apply migration: `alembic upgrade head`
- Rollback: `alembic downgrade -1`

### 3. Test Changes

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:integration
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: description of changes"
git push origin 003-ai-chatbot-mcp
```

---

## Troubleshooting

### Backend Issues

#### Issue: Database connection fails
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check Neon dashboard for connection string
```

#### Issue: OpenAI API errors
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check quota and billing
```

#### Issue: MCP tools not working
```bash
# Check MCP server logs
tail -f logs/mcp.log

# Test tool directly
python -c "from src.mcp.tools.add_task import AddTaskTool; print(AddTaskTool())"

# Verify tool registry
python -c "from src.mcp.registry import registry; print(registry.tools)"
```

### Frontend Issues

#### Issue: API calls fail (CORS)
```bash
# Check backend CORS configuration
# In backend/src/main.py:
# allow_origins should include http://localhost:3000

# Check browser console for CORS errors
# Verify NEXT_PUBLIC_API_URL is correct
```

#### Issue: ChatKit not rendering
```bash
# Check ChatKit installation
npm list @openai/chatkit

# Reinstall if needed
npm install @openai/chatkit@latest

# Check browser console for errors
```

#### Issue: Authentication fails
```bash
# Check auth token in localStorage
# Open browser console:
localStorage.getItem('auth_token')

# Clear and re-login
localStorage.clear()

# Check backend auth logs
```

### Database Issues

#### Issue: Migrations fail
```bash
# Check current migration version
alembic current

# Check migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head

# If stuck, reset database (CAUTION: loses data)
alembic downgrade base
alembic upgrade head
```

#### Issue: Slow queries
```bash
# Check query performance
EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = 'uuid';

# Verify indexes exist
\d messages

# Add missing indexes
CREATE INDEX idx_name ON table(column);
```

---

## Useful Commands

### Backend

```bash
# Run specific test
pytest tests/test_chat.py::test_create_task

# Check code style
black src/
flake8 src/

# Generate API docs
python scripts/generate_docs.py

# View logs
tail -f logs/app.log
```

### Frontend

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format

# Build
npm run build

# Analyze bundle
npm run analyze
```

### Database

```bash
# Connect to database
psql $DATABASE_URL

# List tables
\dt

# Describe table
\d messages

# Count records
SELECT COUNT(*) FROM messages;

# Recent conversations
SELECT * FROM conversations ORDER BY last_message_at DESC LIMIT 10;
```

---

## Next Steps

1. **Implement MVP**: Focus on User Story 1 (Create Tasks) and User Story 2 (View Tasks)
2. **Test Thoroughly**: Verify all acceptance scenarios from spec.md
3. **Add Monitoring**: Set up logging and metrics
4. **Deploy**: Follow deployment guide in docs/deployment.md

---

## Resources

- **API Documentation**: http://localhost:8001/docs
- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Tasks**: [tasks.md](./tasks.md)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review specification and plan documents
3. Check GitHub issues
4. Contact development team

**Happy coding! 🚀**
