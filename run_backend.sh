#!/bin/bash

# Script to run the Brainboard FastAPI backend server

# Change to backend directory
cd apps/backend

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000 