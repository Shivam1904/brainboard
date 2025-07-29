"""
Dashboard Router
Main API endpoints for the AI-powered dashboard system
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import date
import logging

from core.database import get_db
from services.dashboard_service import DashboardService
from models.schemas import (
    CreateDashboardWidgetRequest,
    UpdateDashboardWidgetRequest
)
from models.database import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get dashboard service
def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """Create dashboard service with database session"""
    return DashboardService(db)

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    # For now, return default user. In production, this would come from authentication
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default user not found. Please ensure database is initialized."
        )
    return default_user.id

@router.get(
    "/today",
    response_model=Dict[str, Any],
    summary="Get today's AI-generated dashboard",
    description="Returns complete dashboard for today with AI-selected widgets and their data"
)
async def get_today_dashboard(
    target_date: Optional[date] = Query(None, description="Date for dashboard (defaults to today)"),
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get today's AI-generated dashboard with all widget data
    
    This is the main endpoint that the frontend calls to get the complete
    dashboard configuration and data for a specific date.
    """
    try:
        return await dashboard_service.get_today_dashboard(user_id, target_date)
    except Exception as e:
        logger.error(f"Failed to generate dashboard for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {str(e)}"
        )

@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Get dashboard statistics",
    description="Returns statistics about user's dashboard configuration"
)
async def get_dashboard_stats(
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get dashboard statistics for the user"""
    try:
        # TODO: Implement dashboard stats
        return {
            "message": "Dashboard stats endpoint - to be implemented",
            "user_id": user_id or "default"
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.post(
    "/widget",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dashboard widget",
    description="Create a new widget that will be considered for daily dashboard generation"
)
async def create_dashboard_widget(
    widget_request: CreateDashboardWidgetRequest,
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Create a new dashboard widget configuration"""
    try:
        if user_id is None:
            user_id = dashboard_service.ai_service.get_user_or_default()
            
        widget_data = widget_request.dict()
        widget = dashboard_service.create_dashboard_widget(user_id, widget_data)
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create widget"
            )
        
        return widget
    except Exception as e:
        logger.error(f"Failed to create widget for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget: {str(e)}"
        )

@router.get(
    "/widgets",
    response_model=List[Dict[str, Any]],
    summary="Get all dashboard widgets",
    description="Returns all dashboard widget configurations for the user"
)
async def get_all_dashboard_widgets(
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get all dashboard widgets for the user"""
    try:
        if user_id is None:
            user_id = dashboard_service.ai_service.get_user_or_default()
            
        widgets = dashboard_service.get_user_widgets(user_id)
        return widgets
    except Exception as e:
        logger.error(f"Failed to get widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widgets: {str(e)}"
        )

@router.put(
    "/widget/{widget_id}",
    response_model=Dict[str, Any],
    summary="Update a dashboard widget",
    description="Update an existing dashboard widget configuration"
)
async def update_dashboard_widget(
    widget_id: str,
    widget_update: UpdateDashboardWidgetRequest,
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Update a dashboard widget configuration"""
    try:
        updated_widget = dashboard_service.update_dashboard_widget(widget_id, widget_update.dict(exclude_unset=True))
        
        if not updated_widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        return updated_widget
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
        )

@router.delete(
    "/widget/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dashboard widget",
    description="Delete a dashboard widget and all its associated data"
)
async def delete_dashboard_widget(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """Delete a dashboard widget"""
    try:
        from models.database import DashboardWidget
        
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.user_id == user_id
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        db.delete(widget)
        db.commit()
        
        logger.info(f"Deleted widget {widget_id} for user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete widget {widget_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete widget: {str(e)}"
        )
