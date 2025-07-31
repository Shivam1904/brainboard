#!/bin/bash

# Script to run commands with the brainboard-ai conda environment

CONDA_ENV="brainboard-ai"
PYTHON_PATH="/opt/homebrew/Caskroom/miniconda/base/envs/brainboard-ai/bin/python"

# Function to show usage
show_usage() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Available commands:"
    echo "  server   - Start the server"
    echo "  init-db  - Initialize database"
    echo "  data     - Generate test data"
    echo "  python   - Run Python with conda environment"
    echo ""
    echo "Examples:"
    echo "  $0 server"
    echo "  $0 data"
    echo "  $0 python -c 'import fastapi; print(\"FastAPI version:\", fastapi.__version__)'"
}

# Check if command is provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND=$1
shift

case $COMMAND in
    "server")
        echo "🚀 Starting server with $CONDA_ENV environment..."
        cd "$(dirname "$0")"
        $PYTHON_PATH run.py
        ;;
    "init-db")
        echo "🔧 Initializing database with $CONDA_ENV environment..."
        $PYTHON_PATH init_db.py
        ;;
    "data")
        echo "📊 Generating test data with $CONDA_ENV environment..."
        $PYTHON_PATH generate_test_data.py
        ;;
    "python")
        echo "🐍 Running Python with $CONDA_ENV environment..."
        $PYTHON_PATH "$@"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac 