#!/bin/bash
# Start Chat API Server - Phase V MVP
# Run this script to start the FastAPI server locally

echo ""
echo "========================================"
echo "  Event-Driven Todo Chatbot - Chat API"
echo "========================================"
echo ""

cd "$(dirname "$0")/backend"

echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found. Please install Python 3.11+"
    exit 1
fi

echo ""
echo "Checking environment configuration..."
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Creating from template..."
    cp .env.example .env
    echo ""
    echo "Please edit backend/.env and add your OPENAI_API_KEY"
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "Starting Chat API server..."
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8001"
echo "  - Docs: http://localhost:8001/docs"
echo "  - Health: http://localhost:8001/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
