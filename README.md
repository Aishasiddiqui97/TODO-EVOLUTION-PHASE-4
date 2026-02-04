# 🚀 TODO Evolution - Phase 4: Advanced AI Chatbot

## 📋 Overview
Phase 4 represents the culmination of our TODO application evolution, featuring an advanced AI-powered chatbot with comprehensive task management capabilities, real-time interactions, and intelligent automation.

## ✨ Features

### 🤖 AI Chatbot Integration
- **OpenAI GPT Integration**: Powered by advanced language models
- **Natural Language Processing**: Understand complex task requests
- **Context-Aware Responses**: Maintains conversation context
- **Multi-turn Conversations**: Supports extended dialogues

### 📋 Advanced Task Management
- **Smart Task Creation**: Create tasks through natural language
- **Intelligent Task Updates**: Modify tasks with conversational commands
- **Priority Management**: AI-assisted priority assignment
- **Due Date Intelligence**: Natural language date parsing

### 🔧 Technical Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.12
- **Database**: PostgreSQL with SQLModel ORM
- **AI**: OpenAI API integration
- **Authentication**: JWT-based secure authentication
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### 🔥 Automatic Setup
```bash
# Run the startup script
./start-phase4.bat
```

### 📋 Manual Setup

#### 1. Database Setup
```bash
docker-compose up -d db
```

#### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## 🔑 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=DeepSeek-R1-Distill-Llama-70B
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/todo_db
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   OpenAI API    │
                    │   (AI Models)   │
                    └─────────────────┘
```

## 🔧 Development

### Backend Development
```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## 🧪 Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Production Build
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License
This project is licensed under the MIT License.

## 🙏 Acknowledgments
- OpenAI for AI capabilities
- FastAPI for the robust backend framework
- Next.js for the modern frontend framework
- PostgreSQL for reliable data storage

---

**Phase 4** - The ultimate evolution of our TODO application with AI-powered intelligence! 🚀