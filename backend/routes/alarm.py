"""
Alarm routes for alarm management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from db.dependency import get_db_session_dependency
from services.alarm_service import AlarmService
from schemas.alarm import (
    UpdateActivityRequest, 
    UpdateAlarmDetailsRequest,
    AlarmDetailsAndActivityResponse,
    AlarmDetailsResponse
)
from utils.errors import raise_not_found, raise_database_error

# ============================================================================
# CONSTANTS
# ============================================================================
router = APIRouter()

# Default user for development
DEFAULT_USER_ID = "user_001"

# Default snooze minutes
DEFAULT_SNOOZE_MINUTES = 5

# ============================================================================
# DEPENDENCIES
# ============================================================================
def get_default_user_id(db: AsyncSession = Depends(get_db_session_dependency)) -> str:
    """Get default user ID for development."""
    return DEFAULT_USER_ID

# ============================================================================
# ALARM ENDPOINTS
# ============================================================================
@router.get("/getAlarmDetailsAndActivity/{widget_id}", response_model=AlarmDetailsAndActivityResponse)
async def get_alarm_details_and_activity(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get alarm details and activity for a widget."""
    try:
        service = AlarmService(db)
        return await service.get_alarm_details_and_activity(widget_id, user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get alarm details: {str(e)}")

@router.post("/snoozeAlarm/{activity_id}")
async def snooze_alarm(
    activity_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Snooze an alarm activity."""
    try:
        service = AlarmService(db)
        return await service.snooze_alarm(activity_id, user_id, DEFAULT_SNOOZE_MINUTES)
    except Exception as e:
        raise raise_database_error(f"Failed to snooze alarm: {str(e)}")

@router.post("/stopAlarm/{activity_id}")
async def stop_alarm(
    activity_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Stop an alarm activity."""
    try:
        service = AlarmService(db)
        return await service.stop_alarm(activity_id, user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to stop alarm: {str(e)}")

@router.post("/updateActivity/{activity_id}")
async def update_activity(
    activity_id: str,
    update_data: UpdateActivityRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update an alarm activity."""
    try:
        service = AlarmService(db)
        return await service.update_activity(activity_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update activity: {str(e)}")

@router.get("/getAlarmDetails/{widget_id}", response_model=AlarmDetailsResponse)
async def get_alarm_details(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get alarm details for a widget."""
    try:
        service = AlarmService(db)
        result = await service.get_alarm_details(widget_id, user_id)
        if not result:
            raise raise_not_found("Alarm details not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get alarm details: {str(e)}")

@router.post("/updateDetails/{alarm_details_id}")
async def update_alarm_details(
    alarm_details_id: str,
    update_data: UpdateAlarmDetailsRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update alarm details."""
    try:
        service = AlarmService(db)
        return await service.update_alarm_details(alarm_details_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update alarm details: {str(e)}") 