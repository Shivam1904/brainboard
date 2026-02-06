"""
Main FastAPI application entry point.
"""

# ============================================================================
# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import dashboard_widgets, dashboard
from routes import tracker as tracker_routes
from routes import weather as weather_routes
from routes import ai as ai_routes

# ============================================================================
# CONSTANTS & SETTINGS
# ============================================================================
# API settings
API_PREFIX_DASHBOARD_WIDGETS = f"{settings.API_PREFIX}/dashboard-widgets"
API_PREFIX_DASHBOARD = f"{settings.API_PREFIX}/dashboard"
API_TAG_DASHBOARD_WIDGETS = "dashboard-widgets"
API_TAG_DASHBOARD = "dashboard"

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# ============================================================================
# MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

# ============================================================================
# ROUTERS
# ============================================================================
app.include_router(dashboard_widgets.router, prefix=API_PREFIX_DASHBOARD_WIDGETS, tags=[API_TAG_DASHBOARD_WIDGETS])
app.include_router(dashboard.router, prefix=API_PREFIX_DASHBOARD, tags=[API_TAG_DASHBOARD])
app.include_router(ai_routes.router, tags=["AI Operations"])
app.include_router(tracker_routes.router, prefix="/api/v1/tracker", tags=["tracker"]) 
app.include_router(weather_routes.router, prefix="/api/v1/weather", tags=["weather"])

# ============================================================================
# ADMIN INTERFACE
# ============================================================================
from sqladmin import Admin, ModelView
from db.engine import engine
from models.daily_widget import DailyWidget
from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widgets_ai_output import DailyWidgetsAIOutput
from models.websearch_summary_ai_output import WebSearchSummaryAIOutput

admin = Admin(app, engine)

class DailyWidgetAdmin(ModelView, model=DailyWidget):
    column_list = [DailyWidget.id, DailyWidget.widget_id, DailyWidget.date, DailyWidget.is_active]
    name = "Daily Widget"
    name_plural = "Daily Widgets"
    icon = "fa-solid fa-calendar-day"

class DashboardWidgetDetailsAdmin(ModelView, model=DashboardWidgetDetails):
    column_list = [DashboardWidgetDetails.id, DashboardWidgetDetails.title, DashboardWidgetDetails.widget_type]
    name = "Widget Detail"
    name_plural = "Widget Details"
    icon = "fa-solid fa-circle-info"

class DailyWidgetsAIOutputAdmin(ModelView, model=DailyWidgetsAIOutput):
    column_list = [DailyWidgetsAIOutput.id, DailyWidgetsAIOutput.date, DailyWidgetsAIOutput.priority]
    name = "AI Output"
    name_plural = "AI Outputs"
    icon = "fa-solid fa-robot"

class WebsearchSummaryAIOutputAdmin(ModelView, model=WebSearchSummaryAIOutput):
    column_list = [WebSearchSummaryAIOutput.id, WebSearchSummaryAIOutput.query, WebSearchSummaryAIOutput.created_at]
    name = "Websearch Summary"
    name_plural = "Websearch Summaries"
    icon = "fa-solid fa-search"

admin.add_view(DailyWidgetAdmin)
admin.add_view(DashboardWidgetDetailsAdmin)
admin.add_view(DailyWidgetsAIOutputAdmin)
admin.add_view(WebsearchSummaryAIOutputAdmin)

# ============================================================================
# ENDPOINTS
# ============================================================================
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": f"{settings.APP_TITLE} is running"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.APP_TITLE} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)