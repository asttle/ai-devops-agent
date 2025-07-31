#!/bin/bash

# Development startup script for AI DevOps Agent
# Uses uv for fast Python dependency management

echo "🚀 Starting AI DevOps Agent Development Environment"
echo "=================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
    echo "🔄 Please restart your terminal and run this script again"
    exit 1
fi

# Check if required environment variables are set
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys and credentials"
    echo "   Required: GOOGLE_GEMINI_API_KEY (free), AZURE credentials"
    exit 1
fi

# Install Python dependencies with uv
echo "📦 Installing Python dependencies with uv..."
uv sync

# Start backend server
echo "🔧 Starting FastAPI backend on http://localhost:8000"
uv run python backend/main.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

# Start Hono frontend server
echo "🌐 Starting Hono frontend on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development environment started!"
echo ""
echo "🌐 Frontend (Hono):     http://localhost:3000"
echo "🔧 Backend (FastAPI):   http://localhost:8000"
echo "📚 API Docs:            http://localhost:8000/docs"
echo "💊 Health Check:        http://localhost:8000/health"
echo ""
echo "🤖 Features enabled:"
echo "   • ⚡ uv for fast dependency management"
echo "   • 🧠 Context7 MCP for real-time documentation"
echo "   • ☁️  Multi-cloud support (AWS, Azure, GCP)"
echo "   • 🤖 LiteLLM gateway with free Gemini"
echo "   • 🔍 Web search for current best practices"
echo ""
echo "📝 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup INT TERM

# Keep script running
wait