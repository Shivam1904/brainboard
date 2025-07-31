#!/bin/bash

# ============================================================================
# CONSTANTS
# ============================================================================
CONDA_ENV_NAME="brainboard-ai"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
activate_conda_env() {
    echo "🚀 Activating conda environment: $CONDA_ENV_NAME"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV_NAME"
}

# ============================================================================
# COMMAND HANDLING
# ============================================================================
case "$1" in
    "server")
        activate_conda_env
        cd "$(dirname "$0")"
        echo "🚀 Starting server with $CONDA_ENV_NAME environment..."
        python run.py
        ;;
    "data")
        activate_conda_env
        cd "$(dirname "$0")"
        echo "🔧 Generating dummy data with $CONDA_ENV_NAME environment..."
        python generate_dummy_data.py
        ;;
    "setup")
        activate_conda_env
        cd "$(dirname "$0")"
        echo "🔧 Setting up database with $CONDA_ENV_NAME environment..."
        python init_db.py
        ;;
    *)
        echo "Usage: $0 {server|data|setup}"
        echo ""
        echo "Commands:"
        echo "  server  - Start the FastAPI server"
        echo "  data    - Generate dummy data"
        echo "  setup   - Initialize database tables"
        exit 1
        ;;
esac 