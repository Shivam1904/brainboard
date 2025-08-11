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
    target_date: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Get today's widget list from table DailyWidget.
    
    This endpoint only reads data and doesn't require transaction management.
    """
    try:
        
        service = DailyWidgetService(db)
        return await service.get_today_widget_list(target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to get today's widget list: {str(e)}")

@router.post("/widget/addtotoday/{widget_id}", response_model=AddWidgetToTodayResponse)
async def add_widget_to_today(
    widget_id: str,
    target_date: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Add a widget to today's list.
    
    This endpoint manages the transaction lifecycle to prevent cursor reset issues.
    """
    try:
        
        service = DailyWidgetService(db)
        result = await service.add_widget_to_today(widget_id, target_date)
        
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
    target_date: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Remove a widget from today's list.
    
    This endpoint manages the transaction lifecycle to prevent cursor reset issues.
    """
    try:
        service = DailyWidgetService(db)
        result = await service.remove_widget_from_today(daily_widget_id, target_date)
        
        # Commit the transaction at the route level
        await db.commit()
        
        return result
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise raise_database_error(f"Failed to remove widget from today: {str(e)}")

# ============================================================================
# ACTIVITY ENDPOINTS
# ============================================================================

@router.put("/daily-widgets/{daily_widget_id}/updateactivity")
async def update_activity(
    daily_widget_id: str,
    activity_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update activity data for a daily widget."""
    try:
        service = DailyWidgetService(db)
        result = await service.update_activity(daily_widget_id, activity_data)
        
        # Commit the transaction at the route level
        await db.commit()
        
        return result
    except Exception as e:
        # Rollback on any exception
        await db.rollback()
        raise raise_database_error(f"Failed to update activity: {str(e)}")

@router.put("/daily-widgets/{widget_id}/updateTodayActivityByWidgetId")
async def update_activity_by_widget_id_and_date(
    widget_id: str,
    target_date: str,
    activity_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update activity data for a daily widget by widget_id and date."""
    try:
        service = DailyWidgetService(db)
        result = await service.update_activity_by_widget_id_and_date(widget_id, target_date, activity_data)
        return result
    except Exception as e:
        raise raise_database_error(f"Failed to update activity by widget_id and date: {str(e)}")
    

@router.get("/daily-widgets/{daily_widget_id}/getTodayWidget")
async def get_activity_data(
    daily_widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get activity data for a daily widget."""
    try:
        service = DailyWidgetService(db)
        return await service.get_today_widget(daily_widget_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get activity data: {str(e)}")

@router.get("/daily-widgets/{widget_id}/getTodayWidgetbyWidgetId")
async def get_activity_data(
    widget_id: str,
    target_date: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get activity data for a daily widget."""
    try:
        service = DailyWidgetService(db)
        return await service.get_today_widget_by_widget_id(widget_id, target_date)
    except Exception as e:
        raise raise_database_error(f"Failed to get activity data: {str(e)}")
