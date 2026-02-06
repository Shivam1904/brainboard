#!/usr/bin/env python3
"""
Run script for the Brainboard backend.
"""
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8989,
        reload=True,
        log_level="info"
    ) 