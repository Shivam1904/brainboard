from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from models.database_models import DashboardWidget, User, TodoTask, WebSearchQuery, Alarm, Habit, Summary
from services.dashboard_ai_service import DashboardAIService
from services.widget_service import WidgetService
from services.summary_service import SummaryService

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for dashboard operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = DashboardAIService(db)
        self.widget_service = WidgetService(db)
        self.summary_service = SummaryService(db)
    
    async def get_today_dashboard(self, user_id: Optional[str] = None, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get today's AI-generated dashboard with all widget data
        
        Args:
            user_id: User ID (optional, uses default if not provided)
            target_date: Date for dashboard (defaults to today)
            
        Returns:
            Complete dashboard data with widgets and their content
        """
        if target_date is None:
            target_date = date.today()
        
        # Get or create user
        if user_id is None:
            user_id = self.ai_service.get_user_or_default()
        
        logger.info(f"Generating today's dashboard for user {user_id} on {target_date}")
        
        try:
            # Generate today's dashboard using AI service
            return await self.ai_service.get_today_dashboard(user_id, target_date)
            
        except Exception as e:
            logger.error(f"Error generating today's dashboard: {e}")
            raise
    
    def get_widget_complete_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete widget data including configuration and content
        
        Args:
            widget_id: Dashboard widget ID
            
        Returns:
            Complete widget data or None if not found
        """
        try:
            # Get widget configuration
            widget = self.db.query(DashboardWidget).filter_by(id=widget_id).first()
            if not widget:
                logger.warning(f"Widget {widget_id} not found")
                return None
            
            # Base widget info
            widget_data = {
                "id": widget.id,
                "title": widget.title,
                "type": widget.widget_type,
                "category": widget.category,
                "importance": widget.importance,
                "frequency": widget.frequency,
                "settings": widget.settings or {},
                "created_at": widget.created_at.isoformat(),
                "data": {}
            }
            
            # Get widget-specific data based on type
            if widget.widget_type == "todo":
                widget_data["data"] = self.get_todo_widget_data(widget_id)
            elif widget.widget_type == "websearch":
                widget_data["data"] = self.get_websearch_widget_data(widget_id)
            elif widget.widget_type == "alarm":
                widget_data["data"] = self.get_alarm_widget_data(widget_id)
            elif widget.widget_type == "habittracker":
                widget_data["data"] = self.get_habit_widget_data(widget_id)
            else:
                # For unknown widget types, just return empty data
                widget_data["data"] = {}
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Error getting widget data for {widget_id}: {e}")
            return None
    
    def get_todo_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for todo widget with enhanced frequency logic"""
        try:
            from datetime import date
            
            # Get all tasks for this widget
            all_tasks = self.db.query(TodoTask).filter_by(dashboard_widget_id=widget_id).all()
            
            # Filter tasks that should appear today using same logic as todo router
            today = date.today()
            today_tasks = []
            
            for task in all_tasks:
                should_show = self._should_show_task_today(task, today)
                if should_show:
                    today_tasks.append(task)
            
            # Sort by priority, due date, creation time
            today_tasks.sort(key=lambda t: (
                -(t.priority or 3),  # Higher priority first
                t.due_date or date.max,  # Earlier due dates first
                t.created_at
            ))
            
            total_tasks = len(today_tasks)
            completed_tasks = sum(1 for task in today_tasks if task.is_done)
            pending_tasks = total_tasks - completed_tasks
            
            # Group by priority and category
            tasks_by_priority = {}
            tasks_by_category = {}
            
            for task in today_tasks:
                # Priority grouping
                priority = str(task.priority or 3)
                tasks_by_priority[priority] = tasks_by_priority.get(priority, 0) + 1
                
                # Category grouping
                category = task.category or "uncategorized"
                tasks_by_category[category] = tasks_by_category.get(category, 0) + 1
            
            return {
                "tasks": [
                    {
                        "id": task.id,
                        "content": task.content,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "frequency": task.frequency,
                        "priority": task.priority,
                        "category": task.category,
                        "is_done": task.is_done,
                        "is_recurring": task.is_recurring,
                        "last_completed_date": task.last_completed_date.isoformat() if task.last_completed_date else None,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in today_tasks[:10]  # Limit to 10 tasks for dashboard
                ],
                "stats": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "pending_tasks": pending_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    "tasks_by_priority": tasks_by_priority,
                    "tasks_by_category": tasks_by_category
                }
            }
        except Exception as e:
            logger.error(f"Error getting todo widget data: {e}")
            return {
                "tasks": [], 
                "stats": {
                    "total_tasks": 0, 
                    "completed_tasks": 0, 
                    "pending_tasks": 0,
                    "completion_rate": 0,
                    "tasks_by_priority": {},
                    "tasks_by_category": {}
                }
            }
    
    def _should_show_task_today(self, task, target_date):
        """
        Helper method to determine if task should show today
        (Mirrors the logic from todo router)
        """
        # For one-time tasks
        if task.frequency == "once":
            if not task.is_done:
                if task.due_date is None:
                    return True
                return task.due_date <= target_date
            return False
        
        # For recurring tasks
        if not task.is_recurring:
            return not task.is_done
        
        # Daily tasks always show (unless completed today)
        if task.frequency == "daily":
            if task.last_completed_date == target_date:
                return False  # Already completed today
            return True
        
        # Weekly tasks - show every 7 days
        if task.frequency == "weekly":
            days_since_creation = (target_date - task.created_at.date()).days
            if task.last_completed_date:
                days_since_completion = (target_date - task.last_completed_date).days
                return days_since_completion >= 7
            return days_since_creation % 7 == 0
        
        # Monthly tasks - show every 30 days  
        if task.frequency == "monthly":
            days_since_creation = (target_date - task.created_at.date()).days
            if task.last_completed_date:
                days_since_completion = (target_date - task.last_completed_date).days
                return days_since_completion >= 30
            return days_since_creation % 30 == 0
        
        return True
    
    def get_websearch_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for websearch widget"""
        try:
            # Get search queries
            queries = self.db.query(WebSearchQuery).filter_by(dashboard_widget_id=widget_id).all()
            
            # Get recent summaries for this widget
            summaries = self.db.query(Summary).filter_by(dashboard_widget_id=widget_id).order_by(Summary.created_at.desc()).limit(5).all()
            
            if not queries and not summaries:
                return {
                    "message": "No search queries configured",
                    "searches": []
                }
            
            return {
                "searches": [
                    {
                        "id": query.id,
                        "search_term": query.search_term,
                        "created_at": query.created_at.isoformat()
                    }
                    for query in queries
                ],
                "recent_summaries": [
                    {
                        "id": summary.summary_id,
                        "query": summary.query,
                        "summary": summary.summary_text,
                        "sources": summary.sources_json or [],
                        "created_at": summary.created_at.isoformat()
                    }
                    for summary in summaries
                ],
                "stats": {
                    "total_queries": len(queries),
                    "total_summaries": len(summaries)
                }
            }
        except Exception as e:
            logger.error(f"Error getting websearch widget data: {e}")
            return {
                "message": "No search queries configured", 
                "searches": []
            }
    
    def get_alarm_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for alarm widget"""
        try:
            alarms = self.db.query(Alarm).filter_by(dashboard_widget_id=widget_id).all()
            active_alarms = [alarm for alarm in alarms if alarm.next_trigger_time and not alarm.is_snoozed]
            next_alarm = min((alarm.next_trigger_time for alarm in active_alarms), default=None)
            
            return {
                "alarms": [
                    {
                        "id": alarm.id,
                        "next_trigger_time": alarm.next_trigger_time.isoformat() if alarm.next_trigger_time else None,
                        "is_snoozed": alarm.is_snoozed,
                        "created_at": alarm.created_at.isoformat()
                    }
                    for alarm in alarms
                ],
                "stats": {
                    "total_alarms": len(alarms),
                    "active_alarms": len(active_alarms),
                    "next_alarm": next_alarm.isoformat() if next_alarm else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting alarm widget data: {e}")
            return {
                "alarms": [], 
                "stats": {
                    "total_alarms": 0, 
                    "active_alarms": 0,
                    "next_alarm": None
                }
            }
    
    def get_habit_widget_data(self, widget_id: str) -> Dict[str, Any]:
        """Get data for habit tracker widget"""
        try:
            habits = self.db.query(Habit).filter_by(dashboard_widget_id=widget_id).all()
            
            return {
                "habits": [
                    {
                        "id": habit.id,
                        "streak": habit.streak,
                        "created_at": habit.created_at.isoformat()
                    }
                    for habit in habits
                ],
                "total_habits": len(habits),
                "stats": {
                    "average_streak": sum(habit.streak for habit in habits) / len(habits) if habits else 0
                }
            }
        except Exception as e:
            logger.error(f"Error getting habit widget data: {e}")
            return {
                "habits": [], 
                "total_habits": 0,
                "stats": {
                    "average_streak": 0
                }
            }
    
    def get_user_widgets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all widgets for a user"""
        try:
            widgets = self.db.query(DashboardWidget).filter_by(user_id=user_id).all()
            
            # Generate widgets with full schema including data
            result = []
            for widget in widgets:
                # Get widget data from appropriate service
                widget_data = self._get_widget_data(widget.widget_type, widget.id)
                
                result.append({
                    "id": widget.id,
                    "type": widget.widget_type,  # Use 'type' instead of 'widget_type' for consistency
                    "title": widget.title,
                    "size": "medium",  # Default size, could be stored in widget settings
                    "frequency": widget.frequency,
                    "data": widget_data,
                    "category": widget.category,
                    "importance": widget.importance,
                    "settings": widget.settings or {},
                    "is_active": widget.is_active,
                    "last_shown_date": widget.last_shown_date.isoformat() if widget.last_shown_date else None,
                    "created_at": widget.created_at.isoformat()
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting user widgets: {e}")
            return []
    
    def _get_widget_data(self, widget_type: str, widget_id: str) -> Dict[str, Any]:
        """Get data for a specific widget type using the existing detailed methods"""
        try:
            if widget_type == "todo":
                return self.get_todo_widget_data(widget_id)
            elif widget_type == "alarm":
                return self.get_alarm_widget_data(widget_id)
            elif widget_type == "websearch":
                return self.get_websearch_widget_data(widget_id)
            elif widget_type == "habittracker":
                return self.get_habit_widget_data(widget_id)
            else:
                return {"message": f"Widget type {widget_type} not implemented yet"}
        except Exception as e:
            logger.error(f"Error getting widget data for {widget_type}: {e}")
            return {"error": str(e)}
    
    def create_dashboard_widget(self, user_id: str, widget_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new dashboard widget"""
        try:
            widget = DashboardWidget(
                user_id=user_id,
                title=widget_data["title"],
                widget_type=widget_data["widget_type"],
                frequency=widget_data["frequency"],
                category=widget_data.get("category"),
                importance=widget_data.get("importance"),
                settings=widget_data.get("settings")
            )
            
            self.db.add(widget)
            self.db.commit()
            
            return {
                "id": widget.id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "frequency": widget.frequency,
                "category": widget.category,
                "importance": widget.importance,
                "is_active": widget.is_active,
                "created_at": widget.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating dashboard widget: {e}")
            self.db.rollback()
            return None

    def update_dashboard_widget(self, widget_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing dashboard widget"""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
            
            if not widget:
                return None
            
            # Update only provided fields
            for field, value in update_data.items():
                if hasattr(widget, field) and value is not None:
                    setattr(widget, field, value)
            
            # Update timestamp
            widget.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "id": widget.id,
                "title": widget.title,
                "widget_type": widget.widget_type,
                "frequency": widget.frequency,
                "category": widget.category,
                "importance": widget.importance,
                "is_active": widget.is_active,
                "updated_at": widget.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating dashboard widget {widget_id}: {e}")
            self.db.rollback()
            return None
