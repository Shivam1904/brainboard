"""
WebSearch routes for websearch management.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from db.dependency import get_db_session_dependency
from services.websearch_service import WebSearchService
from schemas.websearch import (
    UpdateActivityRequest, 
    UpdateWebSearchDetailsRequest,
    WebSearchDetailsAndActivityResponse,
    WebSearchDetailsResponse,
    WebSearchAISummaryResponse
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
# WEBSEARCH ENDPOINTS
# ============================================================================
@router.get("/getSummaryAndActivity/{widget_id}", response_model=WebSearchDetailsAndActivityResponse)
async def get_summary_and_activity(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get websearch summary and activity for a widget."""
    try:
        service = WebSearchService(db)
        result = await service.get_summary_and_activity(widget_id, user_id)
        
        if not result or not result.get("websearch_details"):
            raise raise_not_found("Websearch details not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get websearch summary and activity: {str(e)}")

@router.post("/updateActivity/{activity_id}")
async def update_activity(
    activity_id: str,
    update_data: UpdateActivityRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update websearch activity."""
    try:
        service = WebSearchService(db)
        result = await service.update_activity(activity_id, user_id, update_data.dict(exclude_unset=True))
        
        if not result or not result.get("success", True):
            raise raise_not_found("Websearch activity not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to update websearch activity: {str(e)}")

@router.get("/getWebsearchDetails/{widget_id}", response_model=WebSearchDetailsResponse)
async def get_websearch_details(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get websearch details for a specific widget."""
    try:
        service = WebSearchService(db)
        result = await service.get_websearch_details(widget_id, user_id)
        
        if not result:
            raise raise_not_found("Websearch details not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get websearch details: {str(e)}")

@router.post("/updateDetails/{websearch_details_id}")
async def update_websearch_details(
    websearch_details_id: str,
    update_data: UpdateWebSearchDetailsRequest,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Update websearch details."""
    try:
        service = WebSearchService(db)
        result = await service.update_websearch_details(websearch_details_id, user_id, update_data.dict(exclude_unset=True))
        
        if not result:
            raise raise_not_found("Websearch details not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to update websearch details: {str(e)}")

@router.get("/getaisummary/{widget_id}", response_model=WebSearchAISummaryResponse)
async def get_ai_summary(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: AsyncSession = Depends(get_db_session_dependency)
):
    """Get AI-generated summary for a specific websearch widget."""
    try:
        service = WebSearchService(db)
        result = await service.get_ai_summary(widget_id, user_id)
        
        if not result:
            raise raise_not_found("AI summary not found for this widget")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise raise_database_error(f"Failed to get AI summary: {str(e)}") 