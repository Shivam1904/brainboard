"""
AI Tool Preprocessing - Data fetching and preparation for tools
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, datetime, timedelta

from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widget import DailyWidget

logger = logging.getLogger(__name__)

class CreationPreprocessing:
    """Preprocessing for widget creation operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def fetch_user_context(self, user_id: str) -> Dict[str, Any]:
        """Fetch user context needed for widget creation."""
        try:
            # Get existing widgets to avoid duplicates
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            existing_widgets = result.scalars().all()
            
            # Get user's widget categories and types
            categories = list(set([w.category for w in existing_widgets if w.category]))
            widget_types = list(set([w.widget_type for w in existing_widgets if w.widget_type]))
            
            # Get recent activity patterns
            recent_activity = await self._get_recent_activity(user_id)
            
            return {
                "success": True,
                "existing_widgets": [w.title for w in existing_widgets],
                "categories": categories,
                "widget_types": widget_types,
                "recent_activity": recent_activity,
                "widget_count": len(existing_widgets)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch user context: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch context: {str(e)}",
                "error": str(e)
            }
    
    async def _get_recent_activity(self, user_id: str) -> Dict[str, Any]:
        """Get recent user activity patterns."""
        try:
            # Get daily widgets from last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            
            stmt = select(DailyWidget).join(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DailyWidget.date >= thirty_days_ago,
                    DailyWidget.date <= date.today()
                )
            )
            
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            # Analyze activity patterns
            activity_summary = {
                "total_activities": len(daily_widgets),
                "completed_tasks": 0,
                "active_categories": {},
                "completion_rate": 0.0
            }
            
            for dw in daily_widgets:
                if dw.activity_data:
                    # Count completed tasks
                    if dw.activity_data.get("todo_activity", {}).get("status") == "completed":
                        activity_summary["completed_tasks"] += 1
                    
                    # Track category activity
                    if hasattr(dw, 'widget') and dw.widget:
                        category = dw.widget.category
                        if category:
                            activity_summary["active_categories"][category] = activity_summary["active_categories"].get(category, 0) + 1
            
            if activity_summary["total_activities"] > 0:
                activity_summary["completion_rate"] = activity_summary["completed_tasks"] / activity_summary["total_activities"]
            
            return activity_summary
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return {}

class EditingPreprocessing:
    """Preprocessing for widget editing operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def fetch_editing_context(self, picked_title: str, user_id: str) -> Dict[str, Any]:
        """Fetch context needed for editing a specific widget."""
        try:
            # Find the widget
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
            
            # Get recent daily widgets for this widget
            recent_daily_widgets = await self._get_recent_daily_widgets(widget.id)
            
            # Get widget history and patterns
            widget_history = await self._get_widget_history(widget.id)
            
            return {
                "success": True,
                "widget": {
                    "id": widget.id,
                    "title": widget.title,
                    "type": widget.widget_type,
                    "category": widget.category,
                    "config": widget.widget_config
                },
                "recent_daily_widgets": recent_daily_widgets,
                "widget_history": widget_history,
                "today_status": await self._get_today_status(widget.id)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch editing context: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch editing context: {str(e)}",
                "error": str(e)
            }
    
    async def _get_recent_daily_widgets(self, widget_id: str) -> List[Dict[str, Any]]:
        """Get recent daily widgets for a specific widget."""
        try:
            # Get last 7 days of daily widgets
            seven_days_ago = date.today() - timedelta(days=7)
            
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.date >= seven_days_ago
                )
            ).order_by(DailyWidget.date.desc())
            
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            return [
                {
                    "date": dw.date.isoformat(),
                    "activity_data": dw.activity_data,
                    "priority": dw.priority,
                    "reasoning": dw.reasoning
                }
                for dw in daily_widgets
            ]
            
        except Exception as e:
            logger.error(f"Failed to get recent daily widgets: {e}")
            return []
    
    async def _get_widget_history(self, widget_id: str) -> Dict[str, Any]:
        """Get widget performance history."""
        try:
            # Get monthly statistics for the last 3 months
            three_months_ago = date.today() - timedelta(days=90)
            
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.date >= three_months_ago
                )
            )
            
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            # Compile monthly stats
            monthly_stats = {}
            for dw in daily_widgets:
                month_key = dw.date.strftime("%Y-%m")
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = {
                        "total_days": 0,
                        "completed_days": 0,
                        "avg_progress": 0.0
                    }
                
                monthly_stats[month_key]["total_days"] += 1
                
                if dw.activity_data:
                    if dw.activity_data.get("todo_activity", {}).get("status") == "completed":
                        monthly_stats[month_key]["completed_days"] += 1
                    
                    progress = dw.activity_data.get("todo_activity", {}).get("progress", 0)
                    if progress is not None:
                        current_avg = monthly_stats[month_key]["avg_progress"]
                        total_days = monthly_stats[month_key]["total_days"]
                        monthly_stats[month_key]["avg_progress"] = (current_avg * (total_days - 1) + progress) / total_days
            
            return {
                "monthly_stats": monthly_stats,
                "total_activity_days": len(daily_widgets),
                "overall_completion_rate": sum(stats["completed_days"] for stats in monthly_stats.values()) / max(sum(stats["total_days"] for stats in monthly_stats.values()), 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get widget history: {e}")
            return {}
    
    async def _get_today_status(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get today's status for the widget."""
        try:
            today = date.today()
            
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.date == today
                )
            )
            
            result = await self.db_session.execute(stmt)
            daily_widget = result.scalars().first()
            
            if daily_widget and daily_widget.activity_data:
                return {
                    "exists": True,
                    "activity_data": daily_widget.activity_data,
                    "priority": daily_widget.priority,
                    "reasoning": daily_widget.reasoning
                }
            else:
                return {
                    "exists": False,
                    "activity_data": None
                }
                
        except Exception as e:
            logger.error(f"Failed to get today status: {e}")
            return None

class AnalysisPreprocessing:
    """Preprocessing for data analysis operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def fetch_analysis_data(self, user_id: str, category: str = None, task_title: str = None) -> Dict[str, Any]:
        """Fetch data needed for analysis."""
        try:
            # Build query based on analysis type
            if category:
                return await self._fetch_category_analysis(user_id, category)
            elif task_title:
                return await self._fetch_task_analysis(user_id, task_title)
            else:
                return await self._fetch_overall_analysis(user_id)
                
        except Exception as e:
            logger.error(f"Failed to fetch analysis data: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch analysis data: {str(e)}",
                "error": str(e)
            }
    
    async def _fetch_category_analysis(self, user_id: str, category: str) -> Dict[str, Any]:
        """Fetch data for category-specific analysis."""
        try:
            # Get all widgets in the category
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.category == category,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            category_widgets = result.scalars().all()
            
            if not category_widgets:
                return {
                    "success": False,
                    "message": f"No widgets found in category '{category}'"
                }
            
            # Get activity data for all widgets in category
            category_activity = []
            for widget in category_widgets:
                widget_activity = await self._get_widget_activity_summary(widget.id)
                if widget_activity:
                    category_activity.append({
                        "widget_title": widget.title,
                        "widget_type": widget.widget_type,
                        "activity_summary": widget_activity
                    })
            
            # Compile category statistics
            category_stats = self._compile_category_stats(category_activity)
            
            return {
                "success": True,
                "category": category,
                "widgets_count": len(category_widgets),
                "category_activity": category_activity,
                "category_stats": category_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch category analysis: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch category analysis: {str(e)}",
                "error": str(e)
            }
    
    async def _fetch_task_analysis(self, user_id: str, task_title: str) -> Dict[str, Any]:
        """Fetch data for task-specific analysis."""
        try:
            # Find the specific task
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.title == task_title,
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                return {
                    "success": False,
                    "message": f"Task '{task_title}' not found"
                }
            
            # Get detailed activity data
            activity_summary = await self._get_widget_activity_summary(widget.id)
            
            return {
                "success": True,
                "task_title": task_title,
                "widget_type": widget.widget_type,
                "category": widget.category,
                "activity_summary": activity_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch task analysis: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch task analysis: {str(e)}",
                "error": str(e)
            }
    
    async def _fetch_overall_analysis(self, user_id: str) -> Dict[str, Any]:
        """Fetch data for overall user analysis."""
        try:
            # Get all user widgets
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            all_widgets = result.scalars().all()
            
            # Compile overall statistics
            overall_stats = {
                "total_widgets": len(all_widgets),
                "categories": {},
                "widget_types": {},
                "completion_rates": {}
            }
            
            for widget in all_widgets:
                # Category stats
                category = widget.category or "uncategorized"
                overall_stats["categories"][category] = overall_stats["categories"].get(category, 0) + 1
                
                # Widget type stats
                widget_type = widget.widget_type or "unknown"
                overall_stats["widget_types"][widget_type] = overall_stats["widget_types"].get(widget_type, 0) + 1
                
                # Get completion rate for this widget
                activity_summary = await self._get_widget_activity_summary(widget.id)
                if activity_summary and "completion_rate" in activity_summary:
                    overall_stats["completion_rates"][widget.title] = activity_summary["completion_rate"]
            
            return {
                "success": True,
                "overall_stats": overall_stats,
                "widgets": [
                    {
                        "title": w.title,
                        "type": w.widget_type,
                        "category": w.category,
                        "frequency": w.frequency_text
                    }
                    for w in all_widgets
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch overall analysis: {e}")
            return {
                "success": False,
                "message": f"Failed to fetch overall analysis: {str(e)}",
                "error": str(e)
            }
    
    async def _get_widget_activity_summary(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get activity summary for a specific widget."""
        try:
            # Get daily widgets from last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.date >= thirty_days_ago
                )
            )
            
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            if not daily_widgets:
                return None
            
            # Compile summary
            summary = {
                "total_days": len(daily_widgets),
                "completed_days": 0,
                "completion_rate": 0.0,
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
            
            if summary["total_days"] > 0:
                summary["completion_rate"] = summary["completed_days"] / summary["total_days"]
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get widget activity summary: {e}")
            return None
    
    def _compile_category_stats(self, category_activity: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile statistics for a category."""
        if not category_activity:
            return {}
        
        total_widgets = len(category_activity)
        total_completion_rate = sum(
            activity["activity_summary"]["completion_rate"] 
            for activity in category_activity 
            if activity["activity_summary"] and "completion_rate" in activity["activity_summary"]
        )
        
        return {
            "total_widgets": total_widgets,
            "average_completion_rate": total_completion_rate / total_widgets if total_widgets > 0 else 0.0,
            "widget_types": list(set(activity["widget_type"] for activity in category_activity))
        } 