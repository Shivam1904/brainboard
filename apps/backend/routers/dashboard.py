"""
Clean Dashboard Router
Handles AI-generated daily dashboard management

Endpoints:
- GET /widgets/today - Get today's AI-curated widgets (from DailyWidgets)
- POST /widget/{widget_id} - Update widget grid/visibility settings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, List, Any
from datetime import date, datetime
import logging

from core.database import get_db
from models.database import User, DashboardWidget, DailyWidget
from models.schemas.dashboard_schemas import UpdateWidgetDisplayRequest

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboard"])

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
# DASHBOARD ENDPOINTS - Daily AI-Curated Widgets
# ============================================================================

@router.get("/widgets/today", response_model=Dict[str, Any])
async def get_today_widgets(
    target_date: Optional[date] = Query(None, description="Date for dashboard (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Get today's AI-curated dashboard widgets (read-only)
    Returns widgets already generated and saved for today.
    """
    try:
        if target_date is None:
            target_date = date.today()
        daily_widgets = db.query(DailyWidget).join(
            DashboardWidget
        ).filter(
            DailyWidget.user_id == user_id,
            DailyWidget.display_date == target_date,
            DashboardWidget.is_active == True,
            DashboardWidget.is_visible == True
        ).order_by(DailyWidget.position).all()
        widgets_data = []
        for daily_widget in daily_widgets:
            widget = daily_widget.dashboard_widget
            widget_data = {
                # "id": widget.id,
                "daily_widget_id": daily_widget.dashboard_widget_id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "category": widget.category,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "position": daily_widget.position,
                "grid_position": daily_widget.grid_position or widget.grid_size,
                "is_pinned": daily_widget.is_pinned,
                "ai_reasoning": daily_widget.ai_reasoning,
                "settings": widget.settings,
                "created_at": widget.created_at,
                "updated_at": widget.updated_at
            }
            widgets_data.append(widget_data)
        return {
            "date": target_date,
            "widgets": widgets_data,
            "total_widgets": len(widgets_data),
            "ai_generated": bool(widgets_data),
            "last_updated": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Failed to get today's widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get today's widgets: {str(e)}"
        )

@router.post("/widgets/today/ai_generate", response_model=Dict[str, Any])
async def generate_today_widgets(
    target_date: Optional[date] = Query(None, description="Date for dashboard (defaults to today)"),
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Ad-hoc trigger to run AI logic and generate today's widgets, saving them in DB.
    """
    try:
        if target_date is None:
            target_date = date.today()
        # Run AI generation and save
        daily_widgets = await _generate_daily_widgets(db, user_id, target_date)
        widgets_data = []
        for daily_widget in daily_widgets:
            widget = daily_widget.dashboard_widget
            widget_data = {
                # "id": widget.id,
                "daily_widget_id": daily_widget.dashboard_widget_id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "category": widget.category,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "position": daily_widget.position,
                "grid_position": daily_widget.grid_position or widget.grid_size,
                "is_pinned": daily_widget.is_pinned,
                "ai_reasoning": daily_widget.ai_reasoning,
                "settings": widget.settings,
                "created_at": widget.created_at,
                "updated_at": widget.updated_at
            }
            widgets_data.append(widget_data)
        return {
            "date": target_date,
            "widgets": widgets_data,
            "total_widgets": len(widgets_data),
            "ai_generated": True,
            "last_updated": datetime.utcnow(),
            "message": "Today's widgets generated and saved successfully."
        }
    except Exception as e:
        logger.error(f"Failed to generate today's widgets for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate today's widgets: {str(e)}"
        )

@router.post("/widget/{widget_id}", response_model=Dict[str, Any])
async def update_widget_display(
    widget_id: str,
    update_data: UpdateWidgetDisplayRequest,
    user_id: str = Depends(get_default_user_id),
    db: Session = Depends(get_db)
):
    """
    Update widget display settings (grid size, visibility)
    
    This endpoint updates the display properties of a widget:
    - Grid size and position
    - Visibility (show/hide)
    - Other display-related settings
    """
    try:
        # Get the widget
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.user_id == user_id
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
        
        logger.info(f"Updated widget display settings: {widget_id}")
        
        return {
            "id": widget.id,
            "title": widget.title,
            "widget_type": widget.widget_type,
            "is_visible": widget.is_visible,
            "grid_size": widget.grid_size,
            "updated_at": widget.updated_at,
            "message": "Widget display settings updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update widget display {widget_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget display: {str(e)}"
        )

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def _generate_daily_widgets(db: Session, user_id: str, target_date: date) -> List[DailyWidget]:
    """
    Generate today's daily widgets using AI logic
    
    This function implements the AI logic to select which widgets
    should be shown on today's dashboard based on:
    - Widget frequency and importance
    - User patterns and preferences  
    - Last shown dates
    - Category balancing
    """
    try:
        # Remove ALL existing daily widgets for this user (across all dates)
        db.query(DailyWidget).filter(
            DailyWidget.user_id == user_id
        ).delete()
        db.commit()

        # Get all active and visible user widgets
        available_widgets = db.query(DashboardWidget).filter(
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_active == True,
            DashboardWidget.is_visible == True
        ).order_by(
            desc(DashboardWidget.importance),
            DashboardWidget.frequency,
            DashboardWidget.created_at
        ).all()

        if not available_widgets:
            logger.warning(f"No available widgets for user {user_id}")
            return []

        # Simple AI logic for now - select top widgets based on criteria
        selected_widgets = []
        position = 0

        # Always include todo widget if exists (special case)
        todo_widget = next((w for w in available_widgets if w.widget_type == "todo"), None)
        if todo_widget:
            daily_widget = DailyWidget(
                user_id=user_id,
                dashboard_widget_id=todo_widget.id,
                display_date=target_date,
                position=position,
                ai_reasoning="Todo widget is essential for daily productivity",
                is_pinned=False
            )
            db.add(daily_widget)
            selected_widgets.append(daily_widget)
            position += 1

        # Select other high-importance widgets (max 5 total for today)
        max_widgets = 5
        for widget in available_widgets:
            if len(selected_widgets) >= max_widgets:
                break
            if widget.widget_type == "todo":
                continue  # Already added
            # Simple selection criteria
            should_include = (
                widget.importance >= 3 or
                widget.frequency == "daily" or
                (widget.frequency == "weekly" and target_date.weekday() in [0, 2, 4])  # Mon, Wed, Fri
            )
            if should_include:
                daily_widget = DailyWidget(
                    user_id=user_id,
                    dashboard_widget_id=widget.id,
                    display_date=target_date,
                    position=position,
                    ai_reasoning=f"Selected based on {widget.frequency} frequency and importance {widget.importance}",
                    is_pinned=False
                )
                db.add(daily_widget)
                selected_widgets.append(daily_widget)
                position += 1

        db.commit()

        # Refresh to get relationships
        for daily_widget in selected_widgets:
            db.refresh(daily_widget)

        logger.info(f"Generated {len(selected_widgets)} daily widgets for user {user_id} on {target_date}")
        return selected_widgets

    except Exception as e:
        logger.error(f"Failed to generate daily widgets: {e}")
        db.rollback()
        return []
