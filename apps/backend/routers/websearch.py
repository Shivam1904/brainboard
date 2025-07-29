"""
WebSearch Router - API endpoints for websearch operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from core.database import get_db
from services.websearch_service import WebSearchService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websearch"])

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
# WEBSEARCH ENDPOINTS
# ============================================================================

@router.get("/getSummaryAndActivity/{widget_id}")
async def get_summary_and_activity(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get websearch summary and activity for a specific widget
    """
    try:
        service = WebSearchService(db)
        result = service.get_summary_and_activity(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Websearch details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting websearch summary and activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get websearch summary and activity: {str(e)}"
        )

@router.post("/updateActivity/{activity_id}")
async def update_websearch_activity(
    activity_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update websearch activity (status, reaction, summary, sources)
    """
    try:
        service = WebSearchService(db)
        result = service.update_activity(activity_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Websearch activity not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating websearch activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update websearch activity: {str(e)}"
        )

@router.get("/getWebsearchDetails/{widget_id}")
async def get_websearch_details(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Get websearch details for a specific widget
    """
    try:
        service = WebSearchService(db)
        result = service.get_websearch_details(widget_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Websearch details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting websearch details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get websearch details: {str(e)}"
        )

@router.post("/updateDetails/{websearch_details_id}")
async def update_websearch_details(
    websearch_details_id: str,
    update_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update websearch details
    """
    try:
        service = WebSearchService(db)
        result = service.update_websearch_details(websearch_details_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Websearch details not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating websearch details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update websearch details: {str(e)}"
        ) 