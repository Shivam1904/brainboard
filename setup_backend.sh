#!/bin/bash

# Script to set up the Brainboard backend environment

echo "Setting up Brainboard backend environment..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    echo "Please install conda first: https://docs.conda.io/en/latest/"
    exit 1
fi

# Create or update the conda environment
echo "Creating/updating conda environment 'brainboard'..."
conda env update -f apps/backend/environment.yml

echo ""
echo "✅ Backend environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  conda activate brainboard"
echo ""
echo "To run the backend server, run:"
echo "  python run_backend.py"
echo "  or"
echo "  ./run_backend.sh" 