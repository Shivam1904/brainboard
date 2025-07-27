from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routers import reminders, summaries, auth
from core.config import settings
from core.database import init_db

app = FastAPI(
    title="Brainboard API",
    description="AI-Powered Dashboard Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(summaries.router, prefix="/api/summaries", tags=["summaries"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Brainboard API is running", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "brainboard-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
