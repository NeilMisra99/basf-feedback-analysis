#!/bin/bash

# BASF App Development Server
# Installs dependencies and starts both frontend and backend in parallel

echo "🚀 Starting BASF App Development Environment..."

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill 0
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found!"
    echo "📝 Create .env.local with your API keys before running the app"
    echo "💡 See README.md for setup instructions"
    echo ""
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
if [ ! -d "backend/venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    (cd backend && python -m venv venv)
fi

echo "🔧 Activating virtual environment and installing dependencies..."
(cd backend && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt)

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
(cd frontend && npm install)

echo "✅ Dependencies installed successfully!"
echo ""

# Start backend in background
echo "📡 Starting backend server (Flask)..."
(cd backend && source venv/bin/activate && python application.py) &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend in background  
echo "🎨 Starting frontend server (React + Vite)..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5001"
echo "   Health:   http://localhost:5001/api/v1/health"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait