"""
Alarm Router - API endpoints for alarm operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from core.database import get_db
from services.alarm_service import AlarmService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["alarm"])

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    from models.database import User
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        default_user = User(
            email="default@brainboard.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user.id

# ============================================================================
# ALARM ENDPOINTS
# ============================================================================

@router.get("/getAlarmDetailsAndActivity/{widget_id}")
async def get_alarm_details_and_activity(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get alarm details and activity for a specific widget
    """
    try:
        service = AlarmService(db)
        result = service.get_alarm_details_and_activity(widget_id)
        
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

@router.post("/updateActivity/{activity_id}")
async def update_alarm_activity(
    activity_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update alarm activity (start/snooze)
    """
    try:
        service = AlarmService(db)
        result = service.update_activity(activity_id, update_data)
        
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
    db: Session = Depends(get_db)
):
    """
    Get alarm details for a specific widget
    """
    try:
        service = AlarmService(db)
        result = service.get_alarm_details(widget_id)
        
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
    db: Session = Depends(get_db)
):
    """
    Update alarm details
    """
    try:
        service = AlarmService(db)
        result = service.update_alarm_details(alarm_details_id, update_data)
        
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