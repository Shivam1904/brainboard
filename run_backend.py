#!/usr/bin/env python3
"""
Script to run the Brainboard FastAPI backend server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Run the FastAPI server"""
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 