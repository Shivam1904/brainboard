"""
Alarm Router - API endpoints for alarm operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import logging

from db.dependency import get_db_session_dependency
from services.alarm_service import AlarmService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["alarm"])

def get_default_user_id(db: AsyncSession = Depends(get_db_session_dependency)) -> str:
    """Get default user ID for development"""
    # For now, return a default user ID
    return "default-user"

# ============================================================================
# ALARM ENDPOINTS
# ============================================================================

@router.get("/getAlarmDetailsAndActivity/{widget_id}")
async def get_alarm_details_and_activity(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Get alarm details and activity for a specific widget
    """
    try:
        service = AlarmService(db)
        result = await service.get_alarm_details_and_activity(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alarm details and activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alarm details and activity: {str(e)}"
        )

@router.post("/snoozeAlarm/{activity_id}")
async def snooze_alarm(
    activity_id: str,
    snooze_minutes: int = Query(default=2, description="Minutes to snooze"),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Snooze alarm for specified minutes
    """
    try:
        service = AlarmService(db)
        result = await service.snooze_alarm(activity_id, snooze_minutes)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error snoozing alarm: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to snooze alarm: {str(e)}"
        )

@router.post("/stopAlarm/{activity_id}")
async def stop_alarm(
    activity_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Stop alarm (mark as started)
    """
    try:
        service = AlarmService(db)
        result = await service.stop_alarm(activity_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping alarm: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop alarm: {str(e)}"
        )

@router.post("/updateActivity/{activity_id}")
async def update_alarm_activity(
    activity_id: str,
    update_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Update alarm activity (start/snooze)
    """
    try:
        service = AlarmService(db)
        result = await service.update_activity(activity_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alarm activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alarm activity: {str(e)}"
        )

@router.get("/getAlarmDetails/{widget_id}")
async def get_alarm_details(
    widget_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Get alarm details for a specific widget
    """
    try:
        service = AlarmService(db)
        result = await service.get_alarm_details(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alarm details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alarm details: {str(e)}"
        )

@router.post("/updateDetails/{alarm_details_id}")
async def update_alarm_details(
    alarm_details_id: str,
    update_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """
    Update alarm details
    """
    try:
        service = AlarmService(db)
        result = await service.update_alarm_details(alarm_details_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alarm details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alarm details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alarm details: {str(e)}"
        ) 