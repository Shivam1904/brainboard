#!/bin/bash

# Brainboard Backend Runner
# Usage: 
#   ./run_backend.sh         - Normal run (just activate and start)
#   ./run_backend.sh --setup - Setup mode (create/update conda environment)

SETUP_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --setup|-s)
            SETUP_MODE=true
            shift
            ;;
        --help|-h)
            echo "Brainboard Backend Runner"
            echo "Usage:"
            echo "  ./run_backend.sh         - Normal run (just activate and start)"
            echo "  ./run_backend.sh --setup - Setup mode (create/update conda environment)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🔪 Killing any process on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process found on port 8000"

# Initialize conda for this shell session
eval "$(conda shell.bash hook)"

# Navigate to backend directory
cd /Users/shivam/Documents/github/brainboard/apps/backend

if [ "$SETUP_MODE" = true ]; then
    echo "⚙️ Setting up conda environment..."
    
    # Check if brainboard environment exists, create if not
    if ! conda info --envs | grep -q "brainboard"; then
        echo "📦 Creating conda environment 'brainboard'..."
        conda env create -f environment.yml
    else
        echo "🔄 Updating conda environment 'brainboard'..."
        conda env update -f environment.yml --prune
    fi
else
    echo "🚀 Quick start mode - using existing conda environment..."
    
    # Check if environment exists
    if ! conda info --envs | grep -q "brainboard"; then
        echo "❌ Environment 'brainboard' not found!"
        echo "💡 Run with --setup flag to create it: ./run_backend.sh --setup"
        exit 1
    fi
fi

echo "🚀 Starting Brainboard backend server..."

# Activate environment and run server from the correct directory
conda activate brainboard
/opt/homebrew/Caskroom/miniconda/base/envs/brainboard/bin/python main.py
