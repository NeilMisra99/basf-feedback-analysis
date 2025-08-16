#!/bin/bash

# BASF App Development Server
# Starts both frontend and backend in parallel

echo "🚀 Starting App Development Servers..."

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill 0
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT

# Start backend in background
echo "📡 Starting backend server..."
(cd backend && python application.py) &
BACKEND_PID=$!

# Start frontend in background  
echo "🎨 Starting frontend server..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

# Wait for both processes
wait