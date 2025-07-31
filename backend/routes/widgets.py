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

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# MODELS
# ============================================================================
class WidgetType(BaseModel):
    """Widget type information."""
    id: str
    name: str
    description: str
    category: str
    icon: str
    count: int
    config_schema: dict

# ============================================================================
# WIDGET ENDPOINTS
# ============================================================================
@router.get("/")
async def get_user_widgets(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all widgets for the current user."""
    service = WidgetService(db)
    return await service.get_user_widgets(DEFAULT_USER_ID)

@router.get("/categories")
async def get_widget_categories(
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get list of widget categories."""
    service = WidgetService(db)
    return await service.get_widget_categories()

@router.get("/{widget_id}")
async def get_widget_details(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get specific widget details for the current user."""
    try:
        service = WidgetService(db)
        widgets = await service.get_user_widgets(DEFAULT_USER_ID)
        
        # Find the specific widget
        widget = next((w for w in widgets if w["id"] == widget_id), None)
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found for user"
            )
        
        return widget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget details: {str(e)}"
        ) 