"""
Main FastAPI application entry point.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes import dashboard_widgets, chat, dashboard
# from routes import ai  # Temporarily commented out for testing

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONSTANTS
# ============================================================================
APP_TITLE = "Brainboard Backend"
APP_DESCRIPTION = "Modular backend for Brainboard application"
APP_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS = ["*"]  # Configure this properly for production
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# API settings
API_PREFIX_DASHBOARD_WIDGETS = "/api/v1/dashboard-widgets"
API_PREFIX_CHAT = "/api/v1/chat"
API_PREFIX_DASHBOARD = "/api/v1/dashboard"
API_TAG_DASHBOARD_WIDGETS = "dashboard-widgets"
API_TAG_CHAT = "chat"
API_TAG_DASHBOARD = "dashboard"

# Server settings
HOST = "0.0.0.0"
PORT = 8000

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# ============================================================================
# MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# ============================================================================
# ROUTERS
# ============================================================================
app.include_router(dashboard_widgets.router, prefix=API_PREFIX_DASHBOARD_WIDGETS, tags=[API_TAG_DASHBOARD_WIDGETS])
app.include_router(chat.router, prefix=API_PREFIX_CHAT, tags=[API_TAG_CHAT])
app.include_router(dashboard.router, prefix=API_PREFIX_DASHBOARD, tags=[API_TAG_DASHBOARD])
# app.include_router(ai.router, tags=["AI Operations"])  # Temporarily commented out for testing

# ============================================================================
# ENDPOINTS
# ============================================================================
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": f"{APP_TITLE} is running"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{APP_TITLE} API",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 