# Evolution of Todo - Phase III

A supercharged full-stack web application for managing tasks, now featuring an **AI-powered Chatbot** for natural language task management.

## Features

- **AI Chatbot**: Manage your tasks through natural conversation using the integrated AI assistant.
- **MCP Integration**: Uses Model Context Protocol (MCP) to bridge the AI agent with the task database securely.
- **User Authentication**: Secure sign up and sign in with JWT tokens.
- **Todo Management**: Create, read, update, delete, and toggle completion of tasks via UI or Chat.
- **User Isolation**: Users can only access their own tasks and conversation history.
- **Persistent Storage**: All tasks and chat messages are stored in a PostgreSQL database.

## Tech Stack

- **Backend**: Python, FastAPI, SQLModel, PostgreSQL
- **AI Agent**: OpenAI Agents SDK, OpenRouter (Gemini 2.0 Flash)
- **Protocol**: Model Context Protocol (MCP) for tool execution
- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Authentication**: JWT-based authentication
- **Database**: PostgreSQL (Docker-based local setup)

## Prerequisites

- Python 3.13+
- Node.js 18+
- Docker (for PostgreSQL)
- OpenRouter API Key (for Chat features)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `backend/.env`:
```bash
OPENAI_API_KEY=your_openrouter_key
OPENAI_MODEL=google/gemini-2.0-flash-001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db
```

5. Start the database and seed the demo user:
```bash
docker-compose up -d
python src/seed.py
```

6. Run the backend server:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The application will be accessible at `http://localhost:3000`.

## API Endpoints

- `POST /api/chat` - Interact with the AI Chatbot
- `GET /api/tasks` - Manage tasks via standard REST
- `POST /api/auth/login` - Secure user authentication

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── ai/          # AI Agent and logic
│   │   ├── mcp/         # Model Context Protocol tools
│   │   ├── api/         # FastAPI routes
│   │   ├── models/      # Database models (Task, User, Conversation)
│   │   └── services/    # Business logic layer
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/chat/    # Phase III Chat Interface
│   │   ├── components/  # ChatKit and UI components
│   │   └── lib/         # API and Auth utilities
├── docker-compose.yml   # Database orchestration
└── README.md
```

## License

This project is licensed under the MIT License.
