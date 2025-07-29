"""
Single Item Tracker Router - API endpoints for tracker operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from core.database import get_db
from services.single_item_tracker_service import SingleItemTrackerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["single-item-tracker"])

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
# SINGLE ITEM TRACKER ENDPOINTS
# ============================================================================

@router.get("/getTrackerDetailsAndActivity/{widget_id}")
async def get_tracker_details_and_activity(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get tracker details and activity for a specific widget
    """
    try:
        service = SingleItemTrackerService(db)
        result = service.get_tracker_details_and_activity(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracker details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tracker details and activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tracker details and activity: {str(e)}"
        )

@router.post("/updateActivity/{activity_id}")
async def update_tracker_activity(
    activity_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update tracker activity value and time
    """
    try:
        service = SingleItemTrackerService(db)
        result = service.update_activity(activity_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracker activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tracker activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tracker activity: {str(e)}"
        )

@router.get("/getTrackerDetails/{widget_id}")
async def get_tracker_details(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get tracker details for a specific widget
    """
    try:
        service = SingleItemTrackerService(db)
        result = service.get_tracker_details(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracker details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tracker details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tracker details: {str(e)}"
        )

@router.post("/updateDetails/{tracker_details_id}")
async def update_tracker_details(
    tracker_details_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update tracker details
    """
    try:
        service = SingleItemTrackerService(db)
        result = service.update_tracker_details(tracker_details_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracker details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tracker details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tracker details: {str(e)}"
        ) 