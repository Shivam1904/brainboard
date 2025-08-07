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
def get_default_user_id() -> str:
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
    """
    Get today's widget list from table DailyWidget.
    
    This endpoint only reads data and doesn't require transaction management.
    """
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
    """
    Add a widget to today's list.
    
    This endpoint manages the transaction lifecycle to prevent cursor reset issues.
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        result = await service.add_widget_to_today(widget_id, user_id, target_date)
        
        # Commit the transaction at the route level
        await db.commit()
        
        return result
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise raise_database_error(f"Failed to add widget to today: {str(e)}")

@router.post("/widget/removefromtoday/{daily_widget_id}", response_model=RemoveWidgetFromTodayResponse)
async def remove_widget_from_today(
    daily_widget_id: str,
    target_date: Optional[date] = Query(None, description="Date to remove widget from (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Remove a widget from today's list.
    
    This endpoint manages the transaction lifecycle to prevent cursor reset issues.
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        service = DailyWidgetService(db)
        result = await service.remove_widget_from_today(daily_widget_id, user_id, target_date)
        
        # Commit the transaction at the route level
        await db.commit()
        
        return result
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise raise_database_error(f"Failed to remove widget from today: {str(e)}")

@router.post("/widget/updateActive/{daily_widget_id}")
async def update_daily_widget_active(
    daily_widget_id: str,
    is_active: bool = Query(..., description="Whether the daily widget should be active"),
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Update the active status of a daily widget.
    
    This endpoint manages the transaction lifecycle to prevent cursor reset issues.
    """
    try:
        service = DailyWidgetService(db)
        result = await service.update_daily_widget_active(daily_widget_id, is_active)
        
        # Commit the transaction at the route level
        await db.commit()
        
        return result
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise raise_database_error(f"Failed to update daily widget active status: {str(e)}") 