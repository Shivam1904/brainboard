"""
Widgets Router
General widget management (all user widgets from DashboardWidgets)

Endpoints:
- GET /widgets - Get all user widgets
- GET /widgets/{widget_id} - Get specific widget details
- POST /widgets/{widget_id} - Update widget details
- POST /widgets - Create new widget
- DELETE /widgets/{widget_id} - Delete widget
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

from core.database import get_db
from models.database_models import User, DashboardWidget
from models.schemas.dashboard_schemas import CreateDashboardWidgetRequest, UpdateDashboardWidgetRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["widgets"])

def get_default_user_id(db: Session = Depends(get_db)) -> str:
    """Get default user ID for development"""
    default_user = db.query(User).filter(User.email == "default@brainboard.com").first()
    if not default_user:
        # Create default user if not exists
        default_user = User(
            email="default@brainboard.com",
            name="Default User"
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user.id

# ============================================================================
# WIDGETS ENDPOINTS - User's Complete Widget Collection
# ============================================================================

@router.get("", response_model=List[Dict[str, Any]])
async def get_all_widgets(
    include_hidden: bool = Query(False, description="Include hidden widgets"),
    category: Optional[str] = Query(None, description="Filter by category"),
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all widgets user has created (not today's selection)
    
    This returns the complete collection of widgets from DashboardWidgets table.
    User can browse and select additional widgets to add to today's dashboard.
    """
    try:
        # Build query
        query = db.query(DashboardWidget).filter(
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_active == True
        )
        
        # Apply filters
        if not include_hidden:
            query = query.filter(DashboardWidget.is_visible == True)
        
        if category:
            query = query.filter(DashboardWidget.category == category)
            
        if widget_type:
            query = query.filter(DashboardWidget.widget_type == widget_type)
        
        # Order by importance and creation date
        widgets = query.order_by(
            DashboardWidget.importance.desc(),
            DashboardWidget.created_at.desc()
        ).all()
        
        # Format response
        widgets_data = []
        for widget in widgets:
            widget_data = {
                "id": widget.id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "category": widget.category,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "is_visible": widget.is_visible,
                "grid_size": widget.grid_size,
                "settings": widget.settings,
                "last_shown_date": widget.last_shown_date,
                "created_at": widget.created_at,
                "updated_at": widget.updated_at
            }
            widgets_data.append(widget_data)
        
        return widgets_data
        
    except Exception as e:
        logger.error(f"Failed to get widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widgets: {str(e)}"
        )

@router.get("/{widget_id}", response_model=Dict[str, Any])
async def get_widget(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get specific widget details
    
    Returns complete widget configuration and metadata.
    """
    try:
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_active == True
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        return {
            "id": widget.id,
            "title": widget.title,
            "widget_type": widget.widget_type,
            "category": widget.category,
            "importance": widget.importance,
            "frequency": widget.frequency,
            "is_visible": widget.is_visible,
            "grid_size": widget.grid_size,
            "settings": widget.settings,
            "last_shown_date": widget.last_shown_date,
            "created_at": widget.created_at,
            "updated_at": widget.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get widget {widget_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get widget: {str(e)}"
        )

@router.post("/{widget_id}", response_model=Dict[str, Any])
async def update_widget(
    widget_id: str,
    update_data: UpdateDashboardWidgetRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Update widget details
    
    Updates the main widget configuration (not display settings).
    Use dashboard router for display-related updates.
    """
    try:
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_active == True
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Widget {widget_id} not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(widget, field):
                setattr(widget, field, value)
        
        widget.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(widget)
        
        logger.info(f"Updated widget: {widget_id}")
        
        return {
            "id": widget.id,
            "title": widget.title,
            "widget_type": widget.widget_type,
            "category": widget.category,
            "importance": widget.importance,
            "frequency": widget.frequency,
            "settings": widget.settings,
            "updated_at": widget.updated_at,
            "message": "Widget updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update widget {widget_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
        )

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_widget(
    widget_data: CreateDashboardWidgetRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Create new widget
    
    Creates a new widget in the user's collection.
    """
    try:
        # Create widget
        widget = DashboardWidget(
            user_id=user_id,
            title=widget_data.title,
            widget_type=widget_data.widget_type,
            frequency=widget_data.frequency,
            category=widget_data.category,
            importance=widget_data.importance,
            settings=widget_data.settings,
            is_visible=True,
            grid_size=getattr(widget_data, 'grid_size', None)
        )
        
        db.add(widget)
        db.commit()
        db.refresh(widget)
        
        logger.info(f"Created widget: {widget.id} ({widget.title})")
        
        return {
            "id": widget.id,
            "title": widget.title,
            "widget_type": widget.widget_type,
            "category": widget.category,
            "importance": widget.importance,
            "frequency": widget.frequency,
            "created_at": widget.created_at,
            "message": "Widget created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create widget: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create widget: {str(e)}"
        )

@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: str,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete widget
    
    Permanently deletes widget and all associated data.
    """
    try:
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
        
        logger.info(f"Deleted widget: {widget_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete widget {widget_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete widget: {str(e)}"
        )
