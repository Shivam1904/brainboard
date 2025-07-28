from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routers import websearch, health, dashboard, todo, single_item_tracker, alarm
from core.config import settings
from core.database import init_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brainboard API",
    description="AI-Powered Dashboard Backend with WebSearch Widgets",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - ALL prefixes defined here for consistency
app.include_router(websearch.router, prefix="/api/v1/widgets/websearch", tags=["websearch"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(health.router, prefix="/api", tags=["health"])  # Health uses /api for simplicity
app.include_router(todo.router, prefix="/api/v1/widgets/todo", tags=["todo"])  # Clean todo API - 4 endpoints only
app.include_router(single_item_tracker.router, prefix="/api/v1/widgets/single-item-tracker", tags=["single-item-tracker"])
app.include_router(alarm.router, prefix="/api/v1/widgets/alarm", tags=["alarm"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Brainboard API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
