"""
Dashboard routes for dashboard management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from datetime import date

from db.dependency import get_db_session_dependency
from services.daily_widget_service import DailyWidgetService
from schemas.dashboard import (
    TodayWidgetListResponse,
    AddWidgetToTodayResponse,
    RemoveWidgetFromTodayResponse
)
from utils.errors import raise_not_found, raise_database_error

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# ============================================================================
# DEPENDENCIES
# ============================================================================
def get_default_user_id(db: AsyncSession = Depends(get_db_session_dependency)) -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================
@router.get("/getTodayWidgetList", response_model=List[TodayWidgetListResponse])
async def get_today_widget_list(
    target_date: Optional[date] = Query(None, description="Date for widget list (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get today's widget list from table DailyWidget."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.get_today_widget_list(user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to get today's widget list: {str(e)}")

@router.post("/widget/addtotoday/{widget_id}", response_model=AddWidgetToTodayResponse)
async def add_widget_to_today(
    widget_id: str,
    target_date: Optional[date] = Query(None, description="Date to add widget to (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Add a widget to today's list."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.add_widget_to_today(widget_id, user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to add widget to today: {str(e)}")

@router.delete("/widget/removefromtoday/{widget_id}", response_model=RemoveWidgetFromTodayResponse)
async def remove_widget_from_today(
    widget_id: str,
    target_date: Optional[date] = Query(None, description="Date to remove widget from (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Remove a widget from today's list."""
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        return await service.remove_widget_from_today(widget_id, user_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to remove widget from today: {str(e)}") 