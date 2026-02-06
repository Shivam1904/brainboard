"""
AI Tools - Implementation of creation, editing, and fetching tools
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime

from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widget import DailyWidget
from services.dashboard_widget_service import DashboardWidgetService

logger = logging.getLogger(__name__)

class CreationTool:
    """Tool for creating new widgets and tasks."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.dashboard_widget_service = DashboardWidgetService(db_session)
    
    async def create_widget(self, widget_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new widget based on AI response."""
        try:
            # Extract required fields
            title = widget_data.get("title")
            category = widget_data.get("category")
            frequency_text = widget_data.get("frequency_text")
            
            if not all([title, category, frequency_text]):
                raise ValueError("Missing required fields: title, category, frequency_text")
            
            # Create widget configuration
            widget_config = self._build_widget_config(widget_data)
            
            # Determine widget type
            widget_type = 'todo-task'
            
            # Use dashboard widget service to create the widget
            config_data = {
                'title': title,
                'category': category,
                'frequency': frequency_text,
                'importance': 0.7,  # Default importance
                'is_permanent': False,
                'widget_config': widget_config,
                'created_by': user_id
            }
            
            dashboard_widget = await self.dashboard_widget_service.create_widget(widget_type, config_data)
            
            logger.info(f"Created widget: {title} for user {user_id}")
            
            return {
                "success": True,
                "widget_id": dashboard_widget.id,
                "message": f"Successfully created widget '{title}'",
                "widget_data": widget_data
            }
            
        except Exception as e:
            logger.error(f"Failed to create widget: {e}")
            await self.db_session.rollback()
            return {
                "success": False,
                "message": f"Failed to create widget: {str(e)}",
                "error": str(e)
            }
    
    def _build_widget_config(self, widget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build widget configuration from AI response data."""
        config = {}
        
        # Handle different widget types
        if widget_data.get("alarm_times"):
            config["alarm_times"] = widget_data["alarm_times"]
        
        if widget_data.get("tracking_value_type"):
            config["tracking_value_type"] = widget_data["tracking_value_type"]
            config["tracking_value_unit"] = widget_data.get("tracking_value_unit", "")
            config["tracking_target_value"] = widget_data.get("tracking_target_value", "")
        
        if widget_data.get("streak_type") and widget_data["streak_type"] != "none":
            config["streak_type"] = widget_data["streak_type"]
            config["streak_count"] = widget_data.get("streak_count", 1)
        
        if widget_data.get("milestones"):
            config["milestones"] = widget_data["milestones"]
        
        if widget_data.get("search_query_detailed"):
            config["search_query"] = widget_data["search_query_detailed"]
        
        return config
    
    def _determine_widget_type(self, widget_data: Dict[str, Any]) -> str:
        """Determine widget type based on AI response data."""
        if widget_data.get("alarm_times"):
            return "alarm"
        elif widget_data.get("tracking_value_type"):
            return "single_item_tracker"
        elif widget_data.get("search_query_detailed"):
            return "websearch"
        else:
            return "todo"  # Default to todo

class EditingTool:
    """Tool for editing existing widgets and tasks."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def edit_widget(self, edit_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Edit an existing widget based on AI response."""
        try:
            picked_title = edit_data.get("picked_title")
            if not picked_title:
                raise ValueError("Missing picked_title")
            
            # Find the widget by title
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.title == picked_title,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                return {
                    "success": False,
                    "message": f"Widget '{picked_title}' not found",
                    "error": "widget_not_found"
                }
            
            # Update widget if needed
            updated = await self._update_widget(widget, edit_data)
            
            # Create or update daily widget for today
            daily_widget = await self._update_daily_widget(widget, edit_data, user_id)
            
            await self.db_session.commit()
            
            return {
                "success": True,
                "message": f"Successfully updated '{picked_title}'",
                "widget_id": widget.id,
                "daily_widget_id": daily_widget.id if daily_widget else None,
                "updated_fields": list(edit_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to edit widget: {e}")
            await self.db_session.rollback()
            return {
                "success": False,
                "message": f"Failed to edit widget: {str(e)}",
                "error": str(e)
            }
    
    async def _update_widget(self, widget: DashboardWidgetDetails, edit_data: Dict[str, Any]) -> bool:
        """Update widget configuration if needed."""
        updated = False
        
        # Update widget config if new fields are provided
        if edit_data.get("status") or edit_data.get("progress"):
            if not widget.widget_config:
                widget.widget_config = {}
            
            if edit_data.get("status"):
                widget.widget_config["status"] = edit_data["status"]
                updated = True
            
            if edit_data.get("progress"):
                widget.widget_config["progress"] = edit_data["progress"]
                updated = True
        
        return updated
    
    async def _update_daily_widget(self, widget: DashboardWidgetDetails, edit_data: Dict[str, Any], user_id: str) -> Optional[DailyWidget]:
        """Create or update daily widget for today."""
        today = date.today()
        
        # Check if daily widget exists for today
        stmt = select(DailyWidget).where(
            and_(
                DailyWidget.widget_id == widget.id,
                DailyWidget.date == today
            )
        )
        result = await self.db_session.execute(stmt)
        daily_widget = result.scalars().first()
        
        if not daily_widget:
            # Create new daily widget
            daily_widget = DailyWidget(
                widget_id=widget.id,
                priority="MEDIUM",
                reasoning="Created from AI edit request",
                date=today,
                activity_data={},
                created_by=user_id
            )
            self.db_session.add(daily_widget)
        
        # Update activity data
        if not daily_widget.activity_data:
            daily_widget.activity_data = {}
        
        # Update based on widget type
        if widget.widget_type == "todo":
            daily_widget.activity_data["todo_activity"] = {
                "status": edit_data.get("status", "pending"),
                "progress": edit_data.get("progress", 0),
                "notes": edit_data.get("notes", ""),
                "started_at": datetime.now() if edit_data.get("status") == "in_progress" else None
            }
        elif widget.widget_type == "single_item_tracker":
            daily_widget.activity_data["tracker_activity"] = {
                "value": str(edit_data.get("tracking_value", "0")),
                "time_added": datetime.now(),
                "notes": edit_data.get("notes", "")
            }
        elif widget.widget_type == "alarm" and edit_data.get("snooze"):
            daily_widget.activity_data["alarm_activity"] = {
                "snoozed_at": datetime.now(),
                "snooze_count": daily_widget.activity_data.get("alarm_activity", {}).get("snooze_count", 0) + 1
            }
        
        daily_widget.updated_at = datetime.now()
        return daily_widget

class FetchingTool:
    """Tool for fetching data needed by other tools."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def fetch_widget_data(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch comprehensive data for a specific widget."""
        try:
            # Get widget details
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.id == widget_id,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                return {"success": False, "message": "Widget not found"}
            
            # Get recent daily widgets
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.date >= date.today().replace(day=1)  # This month
                )
            ).order_by(DailyWidget.date.desc())
            
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            # Compile activity data
            activity_summary = self._compile_activity_summary(daily_widgets)
            
            return {
                "success": True,
                "widget": {
                    "id": widget.id,
                    "title": widget.title,
                    "type": widget.widget_type,
                    "category": widget.category,
                    "config": widget.widget_config
                },
                "activity_summary": activity_summary,
                "daily_widgets_count": len(daily_widgets)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch widget data: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch data: {str(e)}",
                "error": str(e)
            }
    
    def _compile_activity_summary(self, daily_widgets: List[DailyWidget]) -> Dict[str, Any]:
        """Compile summary of daily widget activities."""
        summary = {
            "total_days": len(daily_widgets),
            "completed_days": 0,
            "progress_trend": [],
            "last_activity": None
        }
        
        for dw in daily_widgets:
            if dw.activity_data:
                # Count completed days
                if dw.activity_data.get("todo_activity", {}).get("status") == "completed":
                    summary["completed_days"] += 1
                
                # Track progress
                progress = dw.activity_data.get("todo_activity", {}).get("progress", 0)
                if progress is not None:
                    summary["progress_trend"].append({
                        "date": dw.date.isoformat(),
                        "progress": progress
                    })
                
                # Track last activity
                if dw.updated_at and (not summary["last_activity"] or dw.updated_at > summary["last_activity"]):
                    summary["last_activity"] = dw.updated_at
        
        return summary 