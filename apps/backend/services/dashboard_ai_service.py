"""
Dashboard AI Service
Orchestrates dashboard generation and widget data fetching
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.ai_dashboard import DashboardAI
from models.database_models import DashboardWidget, User, Summary, TodoTask, WebSearchQuery, Alarm, Habit, HabitLog
from services.web_search_service import WebSearchService

logger = logging.getLogger(__name__)

class DashboardAIService:
    """Service for AI-powered dashboard generation and management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_ai = DashboardAI(db)
        self.web_search_service = WebSearchService()
    
    def get_user_or_default(self) -> str:
        """Get default user ID for development"""
        from models.database_models import User
        default_user = self.db.query(User).filter(User.email == "default@brainboard.com").first()
        if not default_user:
            raise ValueError("Default user not found. Please ensure database is initialized.")
        return default_user.id
    
    async def get_today_dashboard(self, user_id: str, target_date: date = None) -> dict:
        """
        Generate and return complete dashboard for today with all widget data
        
        Args:
            user_id: User identifier
            target_date: Optional date (defaults to today)
            
        Returns:
            Complete dashboard response with widget configurations and data
        """
        if target_date is None:
            target_date = date.today()
            
        logger.info(f"Generating today's dashboard for user {user_id}")
        
        # Get AI-selected widgets for today
        selected_widgets = self.dashboard_ai.generate_daily_dashboard(user_id, target_date)
        
        # Fetch data for each selected widget
        widgets_with_data = []
        for widget in selected_widgets:
            try:
                widget_data = await self._get_widget_data(widget)
                widgets_with_data.append(widget_data)
            except Exception as e:
                logger.error(f"Failed to get data for widget {widget.id}: {e}")
                # Include widget even if data fetch fails, with error info
                widgets_with_data.append({
                    "id": widget.id,
                    "type": widget.widget_type,
                    "title": widget.title,
                    "size": self._get_widget_size(widget.widget_type),
                    "error": f"Failed to load data: {str(e)}",
                    "data": {}
                })
        
        return {
            "date": target_date.isoformat(),
            "widgets": widgets_with_data,
            "stats": {
                "total_widgets": len(selected_widgets),
                "daily_count": sum(1 for w in selected_widgets if w.frequency == "daily"),
                "weekly_count": sum(1 for w in selected_widgets if w.frequency == "weekly"),
                "monthly_count": sum(1 for w in selected_widgets if w.frequency == "monthly")
            }
        }
    
    async def _get_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """
        Fetch complete data for a specific widget type
        
        Args:
            widget: DashboardWidget instance
            
        Returns:
            Complete widget data structure
        """
        base_widget_info = {
            "id": widget.id,
            "type": widget.widget_type,
            "title": widget.title,
            "size": self._get_widget_size(widget.widget_type),
            "category": widget.category,
            "importance": widget.importance,
            "frequency": widget.frequency,
            "settings": widget.settings or {}
        }
        
        # Fetch widget-specific data based on type
        if widget.widget_type == "todo":
            data = await self._get_todo_widget_data(widget)
        elif widget.widget_type == "websearch":
            data = await self._get_websearch_widget_data(widget)
        elif widget.widget_type == "alarm":
            data = await self._get_alarm_widget_data(widget)
        elif widget.widget_type == "calendar":
            data = await self._get_calendar_widget_data(widget)
        elif widget.widget_type == "habittracker":
            data = await self._get_habittracker_widget_data(widget)
        else:
            # Unknown widget type
            data = {"message": f"Widget type '{widget.widget_type}' not implemented yet"}
        
        base_widget_info["data"] = data
        return base_widget_info
    
    async def _get_todo_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for todo widget"""
        try:
            tasks = self.db.query(TodoTask).filter(
                TodoTask.dashboard_widget_id == widget.id
            ).order_by(TodoTask.created_at.desc()).all()
            
            completed_tasks = [t for t in tasks if t.is_done]
            pending_tasks = [t for t in tasks if not t.is_done]
            
            return {
                "tasks": [
                    {
                        "id": task.id,
                        "content": task.content,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "is_done": task.is_done,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in tasks[:20]  # Limit to 20 most recent
                ],
                "stats": {
                    "total_tasks": len(tasks),
                    "completed_tasks": len(completed_tasks),
                    "pending_tasks": len(pending_tasks),
                    "completion_rate": len(completed_tasks) / len(tasks) * 100 if tasks else 0
                }
            }
        except Exception as e:
            logger.error(f"Error fetching todo data: {e}")
            return {"error": str(e), "tasks": [], "stats": {}}
    
    async def _get_websearch_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for web search widget"""
        try:
            # Get search queries for this widget
            queries = self.db.query(WebSearchQuery).filter(
                WebSearchQuery.dashboard_widget_id == widget.id
            ).order_by(WebSearchQuery.created_at.desc()).all()
            
            if not queries:
                return {"message": "No search queries configured", "searches": []}
            
            # Get recent summaries for these queries
            search_results = []
            for query in queries[:3]:  # Limit to 3 most recent queries
                # Get latest summary for this query
                latest_summary = self.db.query(Summary).filter(
                    Summary.dashboard_widget_id == widget.id,
                    Summary.query == query.search_term
                ).order_by(Summary.created_at.desc()).first()
                
                if latest_summary:
                    search_results.append({
                        "query": query.search_term,
                        "summary": latest_summary.summary_text,
                        "sources": latest_summary.sources_json or [],
                        "search_results": latest_summary.search_results_json or [],
                        "created_at": latest_summary.created_at.isoformat()
                    })
                else:
                    # No summary yet, create placeholder
                    search_results.append({
                        "query": query.search_term,
                        "summary": "Search pending...",
                        "sources": [],
                        "search_results": [],
                        "created_at": query.created_at.isoformat()
                    })
            
            return {
                "searches": search_results,
                "total_queries": len(queries)
            }
        except Exception as e:
            logger.error(f"Error fetching websearch data: {e}")
            return {"error": str(e), "searches": []}
    
    async def _get_alarm_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for alarm widget"""
        try:
            alarms = self.db.query(Alarm).filter(
                Alarm.dashboard_widget_id == widget.id
            ).order_by(Alarm.next_trigger_time.asc()).all()
            
            now = datetime.utcnow()
            active_alarms = [a for a in alarms if a.next_trigger_time and a.next_trigger_time > now]
            
            return {
                "alarms": [
                    {
                        "id": alarm.id,
                        "next_trigger_time": alarm.next_trigger_time.isoformat() if alarm.next_trigger_time else None,
                        "is_snoozed": alarm.is_snoozed,
                        "time_until_trigger": (alarm.next_trigger_time - now).total_seconds() if alarm.next_trigger_time else None,
                        "created_at": alarm.created_at.isoformat()
                    }
                    for alarm in alarms[:10]
                ],
                "stats": {
                    "total_alarms": len(alarms),
                    "active_alarms": len(active_alarms),
                    "next_alarm": active_alarms[0].next_trigger_time.isoformat() if active_alarms else None
                }
            }
        except Exception as e:
            logger.error(f"Error fetching alarm data: {e}")
            return {"error": str(e), "alarms": [], "stats": {}}
    
    async def _get_calendar_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for calendar widget (placeholder)"""
        return {
            "message": "Calendar widget not fully implemented",
            "events": [],
            "current_date": date.today().isoformat()
        }
    
    async def _get_habittracker_widget_data(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Get data for habit tracker widget"""
        try:
            habits = self.db.query(Habit).filter(
                Habit.dashboard_widget_id == widget.id
            ).all()
            
            habit_data = []
            for habit in habits:
                # Get recent logs for this habit
                recent_logs = self.db.query(HabitLog).filter(
                    HabitLog.habit_id == habit.id
                ).order_by(HabitLog.date.desc()).limit(30).all()
                
                habit_data.append({
                    "id": habit.id,
                    "streak": habit.streak,
                    "recent_logs": [
                        {
                            "date": log.date.isoformat(),
                            "status": log.status
                        }
                        for log in recent_logs
                    ],
                    "created_at": habit.created_at.isoformat()
                })
            
            return {
                "habits": habit_data,
                "total_habits": len(habits)
            }
        except Exception as e:
            logger.error(f"Error fetching habit tracker data: {e}")
            return {"error": str(e), "habits": []}
    
    def _get_widget_size(self, widget_type: str) -> str:
        """Determine widget size based on type"""
        # Size mapping based on widget functionality document
        small_widgets = ["reminder", "singletracker", "thishour"]
        medium_widgets = ["todo", "websearch", "alarm", "calendar", "habittracker", "notifications"]
        
        if widget_type in small_widgets:
            return "small"
        elif widget_type in medium_widgets:
            return "medium"
        else:
            return "medium"  # Default
    
    def get_dashboard_stats(self, user_id: str) -> dict:
        """Get dashboard statistics"""
        stats = self.dashboard_ai.get_dashboard_stats(user_id)
        return stats
    
    def create_dashboard_widget(self, user_id: str, widget_data: Dict[str, Any]) -> DashboardWidget:
        """Create a new dashboard widget"""
        try:
            widget = DashboardWidget(
                user_id=user_id,
                title=widget_data["title"],
                widget_type=widget_data["widget_type"],
                frequency=widget_data["frequency"],
                category=widget_data.get("category"),
                importance=widget_data.get("importance"),
                settings=widget_data.get("settings"),
                is_active=True
            )
            
            self.db.add(widget)
            self.db.commit()
            self.db.refresh(widget)
            
            logger.info(f"Created dashboard widget {widget.id} for user {user_id}")
            return widget
            
        except Exception as e:
            logger.error(f"Failed to create dashboard widget: {e}")
            self.db.rollback()
            raise
