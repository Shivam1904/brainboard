#!/bin/bash

# Brainboard Development Script
# This script provides easy commands for development

# Function to ensure brainboard environment is active
ensure_environment() {
    if [[ "$CONDA_DEFAULT_ENV" != "brainboard" ]]; then
        echo "Activating brainboard environment..."
        conda activate brainboard
    fi
}

# Function to show help
show_help() {
    echo "🧠 Brainboard Development Script"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  frontend    - Start the frontend development server"
    echo "  backend     - Start the backend development server"
    echo "  setup       - Set up the development environment"
    echo "  install     - Install frontend dependencies"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh frontend  # Start frontend only"
    echo "  ./dev.sh backend   # Start backend only"
    echo "  ./dev.sh setup     # Set up environment"
}

# Main script logic
case "$1" in
    "frontend")
        echo "🚀 Starting frontend development server..."
        npm run dev
        ;;
    "backend")
        ensure_environment
        echo "🚀 Starting backend development server..."
        python run_backend.py
        ;;
    "setup")
        echo "🔧 Setting up development environment..."
        npm install
        ./setup_backend.sh
        ;;
    "install")
        echo "📦 Installing frontend dependencies..."
        npm install
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run './dev.sh help' for available commands"
        exit 1
        ;;
esac 