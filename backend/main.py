"""
Main FastAPI application entry point.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes import alarm, widgets, chat, dashboard, todo

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
API_PREFIX_ALARMS = "/api/v1/alarms"
API_PREFIX_WIDGETS = "/api/v1/widgets"
API_PREFIX_CHAT = "/api/v1/chat"
API_PREFIX_DASHBOARD = "/api/v1/dashboard"
API_PREFIX_TODO = "/api/v1/todo"
API_TAG_ALARMS = "alarm"
API_TAG_WIDGETS = "widgets"
API_TAG_CHAT = "chat"
API_TAG_DASHBOARD = "dashboard"
API_TAG_TODO = "todo"

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
app.include_router(alarm.router, prefix=API_PREFIX_ALARMS, tags=[API_TAG_ALARMS])
app.include_router(widgets.router, prefix=API_PREFIX_WIDGETS, tags=[API_TAG_WIDGETS])
app.include_router(chat.router, prefix=API_PREFIX_CHAT, tags=[API_TAG_CHAT])
app.include_router(dashboard.router, prefix=API_PREFIX_DASHBOARD, tags=[API_TAG_DASHBOARD])
app.include_router(todo.router, prefix=API_PREFIX_TODO, tags=[API_TAG_TODO])

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