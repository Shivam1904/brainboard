"""
API Version 1 - New API Structure
This module contains all v1 API endpoints for the restructured backend.
"""

from fastapi import APIRouter
from . import dashboard, ai, health, todo, alarm, single_item_tracker, websearch

# Create v1 router
v1_router = APIRouter()

# Include all v1 API modules
v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
v1_router.include_router(ai.router, prefix="/ai", tags=["ai"])
v1_router.include_router(health.router, prefix="", tags=["health"])

# Include widget-specific routers
v1_router.include_router(todo.router, prefix="/widgets/todo", tags=["todo"])
v1_router.include_router(alarm.router, prefix="/widgets/alarm", tags=["alarm"])
v1_router.include_router(single_item_tracker.router, prefix="/widgets/single-item-tracker", tags=["single-item-tracker"])
v1_router.include_router(websearch.router, prefix="/widgets/websearch", tags=["websearch"]) 