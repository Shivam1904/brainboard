"""
Daily Widget service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, inspect
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

from models.daily_widget import DailyWidget
from models.dashboard_widget_details import DashboardWidgetDetails

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# ============================================================================
# SERVICE CLASS
# ============================================================================
class DailyWidgetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_widget_list(self, user_id: str, target_date: date) -> List[Dict[str, Any]]:
        """Get today's widget list from table DailyWidget."""
        try:
            stmt = select(DailyWidget).where(
                DailyWidget.date == target_date,
                DailyWidget.is_active == True,
                DailyWidget.delete_flag == False
            ).order_by(DailyWidget.priority.desc())
            
            result = await self.db.execute(stmt)
            daily_widgets = result.scalars().all()
            
            widgets_data = []
            for daily_widget in daily_widgets:
                widgets_data.append({
                    "id": daily_widget.id,
                    "widget_ids": daily_widget.widget_ids,
                    "widget_type": daily_widget.widget_type,
                    "priority": daily_widget.priority,
                    "reasoning": daily_widget.reasoning,
                    "date": daily_widget.date.isoformat(),
                    "is_active": daily_widget.is_active
                })
            
            return widgets_data
            
        except Exception as e:
            logger.error(f"Error getting today's widget list: {e}")
            raise

    async def add_widget_to_today(self, widget_id: str, user_id: str, target_date: date) -> Dict[str, Any]:
        """Add a widget to today's list."""
        try:
            # First, check if the widget exists and belongs to the user
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.id == widget_id,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                return {
                    "success": False,
                    "message": "Widget not found or does not belong to user"
                }
            
            # Check if widget is already in today's list
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == target_date,
                    DailyWidget.is_active == True,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            existing_daily_widgets = result.scalars().all()
            
            # Check if widget is already in any existing daily widget
            for daily_widget in existing_daily_widgets:
                if widget_id in daily_widget.widget_ids:
                    return {
                        "success": False,
                        "message": "Widget is already in today's list"
                    }
            
            # Find existing daily widget of the same type, or create new one
            existing_daily_widget = None
            for daily_widget in existing_daily_widgets:
                if daily_widget.widget_type == widget.widget_type:
                    existing_daily_widget = daily_widget
                    break
            
            if existing_daily_widget:
                # Add widget to existing daily widget
                widget_ids = existing_daily_widget.widget_ids.copy()  # Create a copy
                widget_ids.append(widget_id)
                # Use direct SQL update to ensure JSON is properly updated
                stmt = update(DailyWidget).where(
                    DailyWidget.id == existing_daily_widget.id
                ).values(widget_ids=widget_ids)
                await self.db.execute(stmt)
                await self.db.commit()
                await self.db.refresh(existing_daily_widget)  # Refresh the object
                
                # Create alarm activity for today if it's an alarm widget
                if widget.widget_type == "alarm":
                    from services.alarm_service import AlarmService
                    alarm_service = AlarmService(self.db)
                    activity_result = await alarm_service.create_alarm_activity_for_today(existing_daily_widget.id, widget_id, user_id)
                    if not activity_result:
                        logger.warning(f"Failed to create alarm activity for widget {widget_id}")
                
                return {
                    "success": True,
                    "message": f"Widget added to existing {widget.widget_type} group",
                    "daily_widget_id": existing_daily_widget.id,
                    "widget_ids": widget_ids
                }
            else:
                # Create new daily widget
                new_daily_widget = DailyWidget(
                    widget_ids=[widget_id],
                    widget_type=widget.widget_type,
                    priority="MEDIUM",  # Default priority
                    reasoning=f"Manually added widget: {widget.title}",
                    date=target_date,
                    is_active=True
                )
                
                self.db.add(new_daily_widget)
                await self.db.commit()
                await self.db.refresh(new_daily_widget)
                
                # Create alarm activity for today if it's an alarm widget
                if widget.widget_type == "alarm":
                    from services.alarm_service import AlarmService
                    alarm_service = AlarmService(self.db)
                    activity_result = await alarm_service.create_alarm_activity_for_today(new_daily_widget.id, widget_id, user_id)
                    if not activity_result:
                        logger.warning(f"Failed to create alarm activity for widget {widget_id}")
                
                return {
                    "success": True,
                    "message": f"New {widget.widget_type} group created with widget",
                    "daily_widget_id": new_daily_widget.id,
                    "widget_ids": [widget_id]
                }
                
        except Exception as e:
            logger.error(f"Error adding widget to today: {e}")
            await self.db.rollback()
            raise

    async def remove_widget_from_today(self, widget_id: str, user_id: str, target_date: date) -> Dict[str, Any]:
        """Remove a widget from today's list."""
        try:
            # Find daily widgets containing this widget
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == target_date,
                    DailyWidget.is_active == True,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            daily_widgets = result.scalars().all()
            
            for daily_widget in daily_widgets:
                if widget_id in daily_widget.widget_ids:
                    widget_ids = daily_widget.widget_ids
                    widget_ids.remove(widget_id)
                    
                    if len(widget_ids) == 0:
                        # No widgets left, deactivate the daily widget
                        daily_widget.is_active = False
                    else:
                        # Update with remaining widgets
                        daily_widget.widget_ids = widget_ids
                    
                    await self.db.commit()
                    
                    return {
                        "success": True,
                        "message": "Widget removed from today's list",
                        "daily_widget_id": daily_widget.id,
                        "remaining_widgets": widget_ids
                    }
            
            return {
                "success": False,
                "message": "Widget not found in today's list"
            }
                
        except Exception as e:
            logger.error(f"Error removing widget from today: {e}")
            await self.db.rollback()
            raise 