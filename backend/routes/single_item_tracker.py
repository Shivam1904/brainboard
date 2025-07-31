"""
SingleItemTracker routes for tracker management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from db.dependency import get_db_session_dependency
from services.single_item_tracker_service import SingleItemTrackerService
from schemas.single_item_tracker import (
    UpdateActivityRequest, 
    UpdateTrackerDetailsRequest,
    UpdateOrCreateTrackerDetailsRequest,
    TrackerDetailsAndActivityResponse,
    TrackerDetailsResponse
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
# SINGLEITEMTRACKER ENDPOINTS
# ============================================================================
@router.get("/getTrackerDetailsAndActivity/{widget_id}", response_model=TrackerDetailsAndActivityResponse)
async def get_tracker_details_and_activity(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get tracker details and activity for a widget."""
    try:
        service = SingleItemTrackerService(db)
        return await service.get_tracker_details_and_activity(widget_id, user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get tracker details: {str(e)}")

@router.post("/updateActivity/{activity_id}")
async def update_activity(
    activity_id: str,
    update_data: UpdateActivityRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update a tracker activity."""
    try:
        service = SingleItemTrackerService(db)
        return await service.update_activity(activity_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update activity: {str(e)}")

@router.get("/getTrackerDetails/{widget_id}", response_model=TrackerDetailsResponse)
async def get_tracker_details(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get tracker details for a widget."""
    try:
        service = SingleItemTrackerService(db)
        result = await service.get_tracker_details(widget_id, user_id)
        if not result.get("tracker_details"):
            raise raise_not_found("Tracker details not found")
        return result["tracker_details"]
    except Exception as e:
        raise raise_database_error(f"Failed to get tracker details: {str(e)}")

@router.post("/updateDetails/{tracker_details_id}")
async def update_tracker_details(
    tracker_details_id: str,
    update_data: UpdateTrackerDetailsRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update tracker details."""
    try:
        service = SingleItemTrackerService(db)
        return await service.update_tracker_details(tracker_details_id, user_id, update_data.dict(exclude_unset=True))
    except Exception as e:
        raise raise_database_error(f"Failed to update tracker details: {str(e)}")

@router.post("/updateOrCreateDetails")
async def update_or_create_tracker_details(
    request: UpdateOrCreateTrackerDetailsRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update existing tracker details or create new ones if they don't exist."""
    try:
        service = SingleItemTrackerService(db)
        return await service.update_or_create_tracker_details(
            widget_id=request.widget_id,
            title=request.title,
            value_type=request.value_type,
            value_unit=request.value_unit,
            target_value=request.target_value,
            user_id=user_id
        )
    except Exception as e:
        raise raise_database_error(f"Failed to update or create tracker details: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_trackers(
    user_id: str,
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get all trackers for a user."""
    try:
        service = SingleItemTrackerService(db)
        return await service.get_user_trackers(user_id)
    except Exception as e:
        raise raise_database_error(f"Failed to get user trackers: {str(e)}") 