"""
Daily Widget service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, inspect
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, date, timezone
from typing import Dict, Any, Optional, List
import logging

from models.daily_widget import DailyWidget
from models.dashboard_widget_details import DashboardWidgetDetails

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)
DEFAULT_USER_ID = "user_001"

# ============================================================================
# SERVICE CLASS
# ============================================================================
class DailyWidgetService:
    """
    Service for daily widget operations.
    
    Note: This service does NOT commit or rollback transactions.
    The calling layer (routes) is responsible for transaction management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_widget_list(self) -> List[Dict[str, Any]]:
        """
        Get today's widget list from table DailyWidget.
        
        Note: This method only reads data and does not modify the session.
        """
        print("getting today's widget list", date.today())
        todaysdate = date.today() # in sqlaclchemy Date
        try:
            # Join DailyWidget with DashboardWidgetDetails to get widget information
            stmt = select(
                DailyWidget,
                DashboardWidgetDetails
            ).join(
                DashboardWidgetDetails,
                DailyWidget.widget_id == DashboardWidgetDetails.id
            ).where(
                DailyWidget.date == todaysdate,
                DailyWidget.is_active == True,
                DailyWidget.delete_flag == False,
                DashboardWidgetDetails.delete_flag == False
            ).order_by(DailyWidget.priority.desc())
            
            result = await self.db.execute(stmt)
            rows = result.all()
            
            widgets_data = []
            for daily_widget, widget_details in rows:
                widgets_data.append({
                    "id": daily_widget.id,
                    "daily_widget_id": daily_widget.id,  # Same as id for compatibility
                    "widget_id": daily_widget.widget_id,  # List containing the widget_id
                    "widget_type": widget_details.widget_type,
                    "priority": daily_widget.priority,
                    "reasoning": daily_widget.reasoning,
                    "date": daily_widget.date.isoformat(),  # Convert to ISO string
                    "is_active": daily_widget.is_active,
                    # Additional fields for frontend compatibility
                    "widget_id": daily_widget.widget_id,
                    "title": widget_details.title,
                    "frequency": widget_details.frequency,
                    "importance": widget_details.importance,
                    "category": widget_details.category,
                    "description": widget_details.description,
                    "is_permanent": widget_details.is_permanent,
                    "widget_config": widget_details.widget_config,
                    "activity_data": daily_widget.activity_data,
                    "created_at": daily_widget.created_at.isoformat() if daily_widget.created_at else None,
                    "updated_at": daily_widget.updated_at.isoformat() if daily_widget.updated_at else None,
                    "delete_flag": daily_widget.delete_flag
                })
            
            return widgets_data
            
        except Exception as e:
            logger.error(f"Error getting today's widget list: {e}")
            print(f"Error getting today's widget list: {e}")
            raise

    async def add_widget_to_today(self, widget_id: str) -> Dict[str, Any]:
        """
        Add a widget to today's dashboard.
        Creates entries in DailyWidget with JSON activity data.
        
        Note: This method does NOT commit the transaction.
        The calling layer is responsible for committing.
        """
        try:
            # Check if widget exists and belongs to user
            stmt = select(DashboardWidgetDetails).where(
                and_(
                    DashboardWidgetDetails.id == widget_id,
                    DashboardWidgetDetails.user_id == DEFAULT_USER_ID,
                    DashboardWidgetDetails.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            widget = result.scalars().first()
            
            if not widget:
                raise ValueError("Widget not found")
            
            # Check if widget is already in today's dashboard
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == date.today(),
                    DailyWidget.widget_id == widget_id,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            existing_daily_widget = result.scalars().first()
            
            if existing_daily_widget:
                if not existing_daily_widget.is_active:
                    existing_daily_widget.is_active = True
                    existing_daily_widget.updated_at = date.today()
                    # Note: No commit here - calling layer handles it
                    return {
                        "success": True,
                        "message": "Widget was already in today's dashboard but was inactive. It has now been re-activated.",
                        "daily_widget_id": existing_daily_widget.id,
                        "widget_id": existing_daily_widget.widget_id
                    }
                else:
                    raise ValueError("Widget is already in today's dashboard")
            
            # Create new DailyWidget with initial activity data
            initial_activity_data = self._get_initial_activity_data(widget.widget_type)
            
            daily_widget = DailyWidget(
                widget_id=widget_id,
                priority="HIGH",
                reasoning=f"Manually added {widget.title} to today's dashboard",
                date=date.today(),
                activity_data=initial_activity_data,
                created_by=DEFAULT_USER_ID
            )
            self.db.add(daily_widget)
            await self.db.flush()
            
            return {
                "success": True,
                "message": "Widget added to today's dashboard successfully",
                "daily_widget_id": daily_widget.id,
                "widget_id": daily_widget.widget_id
            }
        except Exception as e:
            logger.error(f"Failed to add widget {widget_id} to today's dashboard: {e}")
            print(f"Failed to add widget {widget_id} to today's dashboard: {e}")
            # Note: No rollback here - calling layer handles it
            raise

    def _get_initial_activity_data(self, widget_type: str) -> Dict[str, Any]:
        """Get initial activity data structure based on widget type."""
        if widget_type == 'alarm':
            return {
                'alarm_activity': {
                    'started_at': None,
                    'snoozed_at': None,
                    'snooze_until': None,
                    'snooze_count': 0
                }
            }
        elif widget_type == 'todo':
            return {
                'todo_activity': {
                    'status': 'not_started',
                    'progress': 0,
                    'started_at': None
                }
            }
        elif widget_type == 'single_item_tracker':
            return {
                'tracker_activity': {
                    'value': '0',
                    'time_added': None,
                    'notes': None
                }
            }
        elif widget_type == 'websearch':
            return {
                'websearch_activity': {
                    'status': 'pending',
                    'reaction': None,
                    'summary': None,
                    'source_json': None,
                    'completed_at': None
                }
            }
        else:
            return {}

    async def remove_widget_from_today(self, daily_widget_id: str) -> Dict[str, Any]:
        """
        Remove a widget from today's list.
        
        Note: This method does NOT commit the transaction.
        The calling layer is responsible for committing.
        """
        try:
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.id == daily_widget_id,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            daily_widget = result.scalars().first()
            
            if not daily_widget:
                raise ValueError("DailyWidget not found")
            
            daily_widget.is_active = False
            daily_widget.updated_at = date.today()
            # Note: No commit here - calling layer handles it
            
            return {
                "success": True,
                "message": "DailyWidget is_active updated successfully", 
                "daily_widget_id": daily_widget_id, 
                "is_active": False
            }
        except Exception as e:
            logger.error(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
            print(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
            # Note: No rollback here - calling layer handles it
            raise 

    async def update_activity(self, daily_widget_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update activity data for a daily widget."""
        try:
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.id == daily_widget_id,
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            daily_widget = result.scalars().first()
            
            if not daily_widget:
                print("DailyWidget not found")
                raise ValueError("DailyWidget not found")
            
            act = daily_widget.activity_data

            for key, value in activity_data.items():
                print(f"Updating activity data for {key} with value {value}")
                act[key] = value

            daily_widget.activity_data = act
            # Mark the JSON field as modified so SQLAlchemy detects the change
            flag_modified(daily_widget, 'activity_data')
            # Update activity data
            print(f"Updated activity data: {daily_widget}")
            daily_widget.updated_at = date.today()
            
            # Flush the changes to the database
            await self.db.flush()
            
            return {
                "success": True,
                "message": "Activity data updated successfully",
                "activity_data": daily_widget.activity_data
            }
        except Exception as e:
            logger.error(f"Failed to update activity data for DailyWidget {daily_widget_id}: {e}")
            print(f"Failed to update activity data for DailyWidget {daily_widget_id}: {e}")
            raise

    async def get_today_widget(self, daily_widget_id: str) -> Dict[str, Any]:
        """Get activity data for a daily widget."""
        try:
            # Join DailyWidget with DashboardWidgetDetails to get widget information
            stmt = select(
                DailyWidget,
                DashboardWidgetDetails
            ).join(
                DashboardWidgetDetails,
                DailyWidget.widget_id == DashboardWidgetDetails.id
            ).where(
                and_(
                    DailyWidget.id == daily_widget_id,
                    DailyWidget.delete_flag == False
                )
            )
            
            result = await self.db.execute(stmt)
            rows = result.all()
            
            for daily_widget, widget_details in rows:
                return {
                        "id": daily_widget.id,
                        "daily_widget_id": daily_widget.id,  # Same as id for compatibility
                        "widget_id": daily_widget.widget_id,  # List containing the widget_id
                        "widget_type": widget_details.widget_type,
                        "priority": daily_widget.priority,
                        "reasoning": daily_widget.reasoning,
                        "date": daily_widget.date.isoformat(),  # Convert to ISO string
                        "is_active": daily_widget.is_active,
                        # Additional fields for frontend compatibility
                        "widget_id": daily_widget.widget_id,
                        "title": widget_details.title,
                        "frequency": widget_details.frequency,
                        "importance": widget_details.importance,
                        "category": widget_details.category,
                        "description": widget_details.description,
                        "is_permanent": widget_details.is_permanent,
                        "widget_config": widget_details.widget_config,
                        "activity_data": daily_widget.activity_data,
                        "created_at": daily_widget.created_at.isoformat() if daily_widget.created_at else None,
                        "updated_at": daily_widget.updated_at.isoformat() if daily_widget.updated_at else None,
                        "delete_flag": daily_widget.delete_flag
                    }
        except Exception as e:
            logger.error(f"Failed to get activity data for DailyWidget {daily_widget_id}: {e}")
            print(f"Failed to get activity data for DailyWidget {daily_widget_id}: {e}")
            raise 