"""
AI Database Service
Handles all database operations for AI prompt preprocessing.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, datetime, timedelta

from models.dashboard_widget_details import DashboardWidgetDetails
from models.daily_widget import DailyWidget

logger = logging.getLogger(__name__)

class AIDatabaseService:
    """Service for handling database operations for AI prompt preprocessing."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._current_user_id: Optional[str] = None
    
    def set_user_id(self, user_id: str) -> None:
        """Set the current user ID for database operations."""
        self._current_user_id = user_id
    
    def get_user_id(self) -> Optional[str]:
        """Get the current user ID."""
        return self._current_user_id
    
    async def fetch_all_task_list(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all tasks for the user."""
        try:
            if not self._current_user_id:
                logger.warning("No user ID set for database operation")
                return []
            
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == self._current_user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widgets = result.scalars().all()
            
            return [
                {
                    "id": widget.id,
                    "title": widget.title,
                    "category": widget.category,
                    "widget_type": widget.widget_type
                }
                for widget in widgets
            ]
        except Exception as e:
            logger.error(f"Failed to fetch all task list: {e}")
            return []
    
    async def fetch_today_list(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch today's tasks."""
        try:
            if not self._current_user_id:
                logger.warning("No user ID set for database operation")
                return []
            
            today = date.today()
            
            stmt = select(DailyWidget).join(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == self._current_user_id,
                    DailyWidget.date == today
                )
            )
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            return [
                {
                    "widget_title": dw.widget.title if dw.widget else "Unknown",
                    "date": dw.date.isoformat(),
                    "activity_data": dw.activity_data
                }
                for dw in daily_widgets
            ]
        except Exception as e:
            logger.error(f"Failed to fetch today list: {e}")
            return []
    
    async def fetch_activity_log(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch activity log based on payload parameters."""
        try:
            if not self._current_user_id:
                logger.warning("No user ID set for database operation")
                return []
            
            date_period = payload.get('date_period', 'month')
            category_list = payload.get('category_list', [])
            
            # Calculate date range
            end_date = date.today()
            if date_period == 'week':
                start_date = end_date - timedelta(days=7)
            elif date_period == 'month':
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=365)
            
            # Build query
            conditions = [
                DashboardWidgetDetails.user_id == self._current_user_id,
                DailyWidget.date >= start_date,
                DailyWidget.date <= end_date
            ]
            
            if category_list:
                conditions.append(DashboardWidgetDetails.category.in_(category_list))
            
            stmt = select(DailyWidget).join(DashboardWidgetDetails).where(and_(*conditions))
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            return [
                {
                    "date": dw.date.isoformat(),
                    "widget_title": dw.widget.title if dw.widget else "Unknown",
                    "category": dw.widget.category if dw.widget else "Unknown",
                    "activity_data": dw.activity_data
                }
                for dw in daily_widgets
            ]
        except Exception as e:
            logger.error(f"Failed to fetch activity log: {e}")
            return []
    
    async def fetch_task_details(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch detailed information about a specific task."""
        try:
            if not self._current_user_id:
                logger.warning("No user ID set for database operation")
                return {}
            
            task_title = payload.get('task_title', '')
            
            if not task_title:
                return {}
            
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == self._current_user_id,
                    DashboardWidgetDetails.title == task_title,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            widget = result.scalar_one_or_none()
            
            if widget:
                return {
                    "id": widget.id,
                    "title": widget.title,
                    "category": widget.category,
                    "widget_type": widget.widget_type,
                    "widget_config": widget.widget_config
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to fetch task details: {e}")
            return {}
    
    async def fetch_task_activity(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch activity data for a specific task."""
        try:
            if not self._current_user_id:
                logger.warning("No user ID set for database operation")
                return []
            
            task_title = payload.get('task_title', '')
            date_period = payload.get('date_period', 'today')
            
            if not task_title:
                return []
            
            # Calculate date range
            end_date = date.today()
            if date_period == 'today':
                start_date = end_date
            elif date_period == 'week':
                start_date = end_date - timedelta(days=7)
            else:
                start_date = end_date - timedelta(days=30)
            
            stmt = select(DailyWidget).join(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.user_id == self._current_user_id,
                    DashboardWidgetDetails.title == task_title,
                    DailyWidget.date >= start_date,
                    DailyWidget.date <= end_date
                )
            )
            result = await self.db_session.execute(stmt)
            daily_widgets = result.scalars().all()
            
            return [
                {
                    "date": dw.date.isoformat(),
                    "activity_data": dw.activity_data
                }
                for dw in daily_widgets
            ]
        except Exception as e:
            logger.error(f"Failed to fetch task activity: {e}")
            return []
    
    async def fetch_user_reference_data(self, user_id: str) -> Dict[str, Any]:
        """Fetch user-specific reference data from database."""
        try:
            # Get all user task names
            stmt = select(DashboardWidgetDetails.title).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False,
                    DashboardWidgetDetails.widget_type.notin_(['weatherWidget', 'calendarWidget', 'yearCalendar', 'allSchedules', 'simpleClock', 'notes', 'pillarsGraph', 'aiChat', 'habitTracker'])
                )
            )
            result = await self.db_session.execute(stmt)
            task_names = [row[0] for row in result.fetchall()]
            
            # Get user categories
            stmt = select(DashboardWidgetDetails.category).where(
                and_(
                    DashboardWidgetDetails.user_id == user_id,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db_session.execute(stmt)
            user_categories = list(set([row[0] for row in result.fetchall() if row[0]]))
            
            return {
                "user_task_names": task_names,
                "user_categories": user_categories,
                "total_tasks": len(task_names)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch user reference data: {e}")
            return {}
    
    async def fetch_data_by_key(self, fetch_key: str, fetch_payload: Dict[str, Any]) -> Any:
        """Fetch data from database based on fetch key and payload."""
        try:
            if fetch_key == "all_task_list":
                return await self.fetch_all_task_list(fetch_payload)
            elif fetch_key == "today_list":
                return await self.fetch_today_list(fetch_payload)
            elif fetch_key == "activity_log":
                return await self.fetch_activity_log(fetch_payload)
            elif fetch_key == "task_details":
                return await self.fetch_task_details(fetch_payload)
            elif fetch_key == "task_activity":
                return await self.fetch_task_activity(fetch_payload)
            else:
                logger.warning(f"Unknown fetch key: {fetch_key}")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch data by key {fetch_key}: {e}")
            return None 