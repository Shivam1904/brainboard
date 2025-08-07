"""
Daily Widget service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, inspect
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timezone
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
    """
    Service for daily widget operations.
    
    Note: This service does NOT commit or rollback transactions.
    The calling layer (routes) is responsible for transaction management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_widget_list(self, user_id: str, target_date: date) -> List[Dict[str, Any]]:
        """
        Get today's widget list from table DailyWidget.
        
        Note: This method only reads data and does not modify the session.
        """
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
                    "daily_widget_id": daily_widget.id,
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
        """
        Add a widget to today's dashboard.
        Creates entries in DailyWidget and corresponding activity tables.
        
        Note: This method does NOT commit the transaction.
        The calling layer is responsible for committing.
        """
        try:
            from services.service_factory import ServiceFactory
            
            # Check if widget exists and belongs to user
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
                raise ValueError("Widget not found")
            
            # Check if widget is already in today's dashboard
            stmt = select(DailyWidget).where(
                and_(
                    DailyWidget.date == target_date,
                    DailyWidget.widget_ids.contains([widget_id]),
                    DailyWidget.delete_flag == False
                )
            )
            result = await self.db.execute(stmt)
            existing_daily_widget = result.scalars().first()
            
            if existing_daily_widget:
                if not existing_daily_widget.is_active:
                    existing_daily_widget.is_active = True
                    existing_daily_widget.updated_at = datetime.now(timezone.utc)
                    # Note: No commit here - calling layer handles it
                    return {
                        "success": True,
                        "message": "Widget was already in today's dashboard but was inactive. It has now been re-activated.",
                        "daily_widget_id": existing_daily_widget.id,
                        "widget_ids": existing_daily_widget.widget_ids
                    }
                else:
                    raise ValueError("Widget is already in today's dashboard")
            
            # Special handling for todo widgets (todo-task and todo-habit, but not todo-event)
            daily_widget = None
            if widget.widget_type in ["todo-task", "todo-habit"]:
                # Check if there's already a DailyWidget for this specific todo widget type today
                stmt = select(DailyWidget).where(
                    and_(
                        DailyWidget.date == target_date,
                        DailyWidget.widget_type == widget.widget_type,
                        DailyWidget.delete_flag == False
                    )
                )
                result = await self.db.execute(stmt)
                existing_todo_daily_widget = result.scalars().first()
                
                if existing_todo_daily_widget:
                    # Update existing DailyWidget by appending widget_id and reasoning
                    daily_widget = existing_todo_daily_widget
                    if widget_id not in daily_widget.widget_ids:
                        logger.info(f"Adding widget {widget_id} to existing DailyWidget {daily_widget.id} for type {widget.widget_type}")
                        
                        # Create a new list to ensure SQLAlchemy detects the change
                        updated_widget_ids = daily_widget.widget_ids.copy()
                        updated_widget_ids.append(widget_id)
                        daily_widget.widget_ids = updated_widget_ids
                        
                        # Append the new reasoning to existing reasoning
                        new_reasoning = f"Manually added {widget.title} to today's dashboard"
                        if daily_widget.reasoning:
                            daily_widget.reasoning = f"{daily_widget.reasoning}; {new_reasoning}"
                        else:
                            daily_widget.reasoning = new_reasoning
                        
                        daily_widget.updated_at = datetime.now(timezone.utc)
                        
                        # Explicitly add the modified object back to session to ensure update
                        self.db.add(daily_widget)
                        await self.db.flush()
                        
                        logger.info(f"Updated DailyWidget {daily_widget.id} with widget_ids: {daily_widget.widget_ids}")
                    else:
                        logger.info(f"Widget {widget_id} already exists in DailyWidget {daily_widget.id}")
                else:
                    # Create new DailyWidget for todo widgets
                    daily_widget = DailyWidget(
                        widget_ids=[widget_id],
                        widget_type=widget.widget_type,
                        priority="HIGH",
                        reasoning=f"Manually added {widget.title} to today's dashboard",
                        date=target_date,
                        created_by=user_id
                    )
                    self.db.add(daily_widget)
                    await self.db.flush()
            else:
                # For non-todo widgets, create a new DailyWidget
                daily_widget = DailyWidget(
                    widget_ids=[widget_id],
                    widget_type=widget.widget_type,
                    priority="HIGH",
                    reasoning=f"Manually added {widget.title} to today's dashboard",
                    date=target_date,
                    created_by=user_id
                )
                self.db.add(daily_widget)
                await self.db.flush()
            
            # Create activity entries using service methods
            # Note: These service methods should NOT commit transactions
            service_factory = ServiceFactory(self.db)
            
            if widget.widget_type in ["todo-habit", "todo-task", "todo-event"]:
                activity_result = await service_factory.todo_service.create_todo_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create todo activity for widget {widget_id}")
            
            elif widget.widget_type == "singleitemtracker":
                activity_result = await service_factory.single_item_tracker_service.create_tracker_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create tracker activity for widget {widget_id}")
            
            elif widget.widget_type == "alarm":
                activity_result = await service_factory.alarm_service.create_alarm_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create alarm activity for widget {widget_id}")
            
            elif widget.widget_type == "websearch":
                activity_result = await service_factory.websearch_service.create_websearch_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create websearch activity for widget {widget_id}")
            
            # Note: No commit here - calling layer handles it
            
            # Determine if we created a new DailyWidget or reused an existing one
            action_type = "created new daily widget"
            if widget.widget_type in ["todo-task", "todo-habit"]:
                if widget_id in daily_widget.widget_ids and len(daily_widget.widget_ids) == 1:
                    action_type = "widget already in today's dashboard"
                elif len(daily_widget.widget_ids) > 1:
                    action_type = "added to existing widget group"
                else:
                    action_type = "created new daily widget"
            
            return {
                "success": True,
                "message": f"Widget added to today's dashboard successfully ({action_type})",
                "daily_widget_id": daily_widget.id,
                "widget_ids": daily_widget.widget_ids
            }
        except Exception as e:
            logger.error(f"Failed to add widget {widget_id} to today's dashboard for user {user_id}: {e}")
            # Note: No rollback here - calling layer handles it
            raise

    async def remove_widget_from_today(self, daily_widget_id: str, user_id: str, target_date: date) -> Dict[str, Any]:
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
            daily_widget.updated_at = datetime.now(timezone.utc)
            # Note: No commit here - calling layer handles it
            
            return {
                "success": True,
                "message": "DailyWidget is_active updated successfully", 
                "daily_widget_id": daily_widget_id, 
                "is_active": False
            }
        except Exception as e:
            logger.error(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
            # Note: No rollback here - calling layer handles it
            raise 

    async def update_daily_widget_active(self, daily_widget_id: str, is_active: bool) -> Dict[str, Any]:
        """
        Update the is_active column for a DailyWidget (activate/deactivate widget)
        
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
            
            daily_widget.is_active = is_active
            daily_widget.updated_at = datetime.now(timezone.utc)
            # Note: No commit here - calling layer handles it
            
            return {
                "success": True,
                "message": f"DailyWidget is_active updated to {is_active}",
                "daily_widget_id": daily_widget_id,
                "is_active": is_active
            }
        except Exception as e:
            logger.error(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
            # Note: No rollback here - calling layer handles it
            raise 