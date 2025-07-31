"""
Widgets routes for user widget management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.dependency import get_db_session_dependency
from services.widget_service import WidgetService
from schemas.widget import WidgetResponse, WidgetTypeResponse, WidgetCategoryResponse, CreateWidgetRequest, CreateWidgetResponse, UpdateWidgetRequest
from utils.errors import raise_not_found, raise_database_error

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# WIDGET ENDPOINTS
# ============================================================================
@router.get("/getAllWidgetList", response_model=List[WidgetResponse])
async def get_user_widgets(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all widgets for the current user."""
    service = WidgetService(db)
    return await service.get_user_widgets(DEFAULT_USER_ID)



@router.get("/categories", response_model=List[WidgetCategoryResponse])
async def get_widget_categories(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get list of widget categories."""
    service = WidgetService(db)
    return await service.get_widget_categories()

@router.post("/create", response_model=CreateWidgetResponse)
async def create_widget(
    request: CreateWidgetRequest,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Create a new dashboard widget."""
    try:
        service = WidgetService(db)
        return await service.create_widget(request, DEFAULT_USER_ID)
    except Exception as e:
        raise raise_database_error(f"Failed to create widget: {str(e)}")

@router.get("/{widget_id}", response_model=WidgetResponse)
async def get_widget_details(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get specific widget details for the current user."""
    try:
        service = WidgetService(db)
        widgets = await service.get_user_widgets(DEFAULT_USER_ID)
        
        # Find the specific widget
        widget = next((w for w in widgets if w.id == widget_id), None)
        
        if not widget:
            raise raise_not_found(f"Widget {widget_id} not found for user")
        
        return widget
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get widget details: {str(e)}")

@router.post("/updateDetails/{widget_id}")
async def update_widget_details(
    widget_id: str,
    request: UpdateWidgetRequest,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update widget details."""
    try:
        service = WidgetService(db)
        return await service.update_widget(widget_id, request, DEFAULT_USER_ID)
    except Exception as e:
        raise raise_database_error(f"Failed to update widget: {str(e)}") 