"""
Dashboard Service - Business logic for dashboard operations
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone, date
import logging

from models.database import DashboardWidgetDetails
from models.schemas.dashboard_schemas import CreateWidgetRequest
from core.database import SessionLocal

logger = logging.getLogger(__name__)

class DashboardService:
    """Service for dashboard operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_widget(self, request: CreateWidgetRequest, user_id: str) -> Dict[str, Any]:
        """
        Create a new dashboard widget with all necessary details
        """
        try:
            # Create new dashboard widget
            widget = DashboardWidgetDetails(
                user_id=user_id,
                widget_type=request.widget_type,
                frequency=request.frequency,
                importance=request.importance,
                title=request.title,
                category=request.category,
                created_by=user_id
            )
            
            self.db.add(widget)
            self.db.commit()
            self.db.refresh(widget)
            
            # Create corresponding details table entry based on widget type
            if request.widget_type in ["todo-habit", "todo-task", "todo-event"]:
                self._create_todo_details(widget.id, request, user_id)
            elif request.widget_type == "singleitemtracker":
                self._create_single_item_tracker_details(widget.id, request, user_id)
            elif request.widget_type == "websearch":
                self._create_websearch_details(widget.id, request, user_id)
            elif request.widget_type == "alarm":
                self._create_alarm_details(widget.id, request, user_id)
            
            self.db.commit()
            
            return {
                "message": "Widget created successfully",
                "widget_id": widget.id,
                "widget_type": widget.widget_type,
                "title": widget.title
            }
            
        except Exception as e:
            logger.error(f"Failed to create widget for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    def update_widget(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> Dict[str, Any]:
        """
        Update an existing dashboard widget with all necessary details
        """
        try:
            # Check if widget exists and belongs to user
            widget = self.db.query(DashboardWidgetDetails).filter(
                DashboardWidgetDetails.id == widget_id,
                DashboardWidgetDetails.user_id == user_id,
                DashboardWidgetDetails.delete_flag == False
            ).first()
            
            if not widget:
                raise ValueError("Widget not found")
            
            # Update dashboard widget details
            widget.widget_type = request.widget_type
            widget.frequency = request.frequency
            widget.importance = request.importance
            widget.title = request.title
            widget.category = request.category
            widget.updated_at = datetime.now(timezone.utc)
            
            # Update corresponding details table entry based on widget type
            if request.widget_type in ["todo-habit", "todo-task", "todo-event"]:
                self._update_todo_details(widget_id, request, user_id)
            elif request.widget_type == "singleitemtracker":
                self._update_single_item_tracker_details(widget_id, request, user_id)
            elif request.widget_type == "websearch":
                self._update_websearch_details(widget_id, request, user_id)
            elif request.widget_type == "alarm":
                self._update_alarm_details(widget_id, request, user_id)
            
            self.db.commit()
            
            return {
                "message": "Widget updated successfully",
                "widget_id": widget.id,
                "widget_type": widget.widget_type,
                "title": widget.title
            }
            
        except Exception as e:
            logger.error(f"Failed to update widget {widget_id} for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    def _update_todo_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Update todo details and potentially calendar widget"""
        from services.service_factory import ServiceFactory
        
        # Use provided todo_type or extract from widget type
        todo_type = request.todo_type or request.widget_type.replace("todo-", "")
        
        # Convert string date to Python date object
        due_date = None
        if request.due_date:
            due_date = datetime.strptime(request.due_date, '%Y-%m-%d').date()
        
        # Use the service factory to get todo service
        service_factory = ServiceFactory(self.db)
        todo_result = service_factory.todo_service.update_or_create_todo_details(
            widget_id=widget_id,
            title=request.title,
            todo_type=todo_type,
            due_date=due_date,
            user_id=user_id
        )
        
        # Log if calendar was created
        if todo_result.get("calendar_created"):
            logger.info(f"Calendar widget automatically created for user {user_id} during widget update")
    
    def _update_single_item_tracker_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Update single item tracker details"""
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(self.db)
        service_factory.single_item_tracker_service.update_or_create_tracker_details(
            widget_id=widget_id,
            title=request.title,
            value_type=request.value_data_type or "number",
            value_unit=request.value_data_unit or "units",
            target_value=request.target_value or "0",
            user_id=user_id
        )
    
    def _update_websearch_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Update websearch details"""
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(self.db)
        service_factory.websearch_service.update_or_create_websearch_details(
            widget_id=widget_id,
            title=request.title,
            user_id=user_id
        )
    
    def _update_alarm_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Update alarm details"""
        from services.service_factory import ServiceFactory
        
        # Use provided alarm time or default to 09:00
        alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
        
        service_factory = ServiceFactory(self.db)
        service_factory.alarm_service.update_or_create_alarm_details(
            widget_id=widget_id,
            title=request.title,
            alarm_times=alarm_times,
            user_id=user_id
        )
    
    def _create_todo_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create todo details and potentially calendar widget"""
        from services.service_factory import ServiceFactory
        
        # Use provided todo_type or extract from widget type
        todo_type = request.todo_type or request.widget_type.replace("todo-", "")
        
        # Convert string date to Python date object
        due_date = None
        if request.due_date:
            due_date = datetime.strptime(request.due_date, '%Y-%m-%d').date()
        
        # Use the service factory to get todo service
        service_factory = ServiceFactory(self.db)
        todo_result = service_factory.todo_service.create_todo_details_with_calendar(
            widget_id=widget_id,
            title=request.title,
            todo_type=todo_type,
            due_date=due_date,
            user_id=user_id
        )
        
        # Log if calendar was created
        if todo_result.get("calendar_created"):
            logger.info(f"Calendar widget automatically created for user {user_id}")
    
    def _create_single_item_tracker_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create single item tracker details"""
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(self.db)
        service_factory.single_item_tracker_service.create_tracker_details(
            widget_id=widget_id,
            title=request.title,
            value_type=request.value_data_type or "number",
            value_unit=request.value_data_unit or "units",
            target_value=request.target_value or "0",
            user_id=user_id
        )
    
    def _create_websearch_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create websearch details"""
        from services.service_factory import ServiceFactory
        
        service_factory = ServiceFactory(self.db)
        service_factory.websearch_service.create_websearch_details(
            widget_id=widget_id,
            title=request.title,
            user_id=user_id
        )
    
    def _create_alarm_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create alarm details"""
        from services.service_factory import ServiceFactory
        
        # Use provided alarm time or default to 09:00
        alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
        
        service_factory = ServiceFactory(self.db)
        service_factory.alarm_service.create_alarm_details(
            widget_id=widget_id,
            title=request.title,
            alarm_times=alarm_times,
            user_id=user_id
        )
    
    def get_today_widget_list(self, target_date: Optional[date] = None, user_id: str = None) -> Dict[str, Any]:
        """
        Get today's widget list from table DailyWidget
        Returns AI-generated daily widget selections for the specified date.
        """
        try:
            from models.database import DailyWidget
            
            if target_date is None:
                target_date = date.today()
            
            # Query DailyWidget table for today's widgets
            daily_widgets = self.db.query(DailyWidget).filter(
                DailyWidget.date == target_date,
                DailyWidget.is_active == True,
                DailyWidget.delete_flag == False
            ).order_by(DailyWidget.priority.desc()).all()
            
            widgets_data = []
            for daily_widget in daily_widgets:
                # Get the first widget ID from the array for basic info
                widget_id = daily_widget.widget_ids[0] if daily_widget.widget_ids else None
                
                # Get widget details if we have a widget ID
                widget_details = None
                if widget_id:
                    widget_details = self.db.query(DashboardWidgetDetails).filter(
                        DashboardWidgetDetails.id == widget_id,
                        DashboardWidgetDetails.user_id == user_id,
                        DashboardWidgetDetails.delete_flag == False
                    ).first()
                
                widget_data = {
                    "daily_widget_id": daily_widget.id,
                    "widget_ids": daily_widget.widget_ids,
                    "widget_type": daily_widget.widget_type,
                    "priority": daily_widget.priority,
                    "reasoning": daily_widget.reasoning,
                    "date": daily_widget.date.isoformat(),
                    "created_at": daily_widget.created_at.isoformat(),
                    "updated_at": daily_widget.updated_at.isoformat()
                }
                
                # Add widget details if available
                if widget_details:
                    widget_data.update({
                        "title": widget_details.title,
                        "category": widget_details.category,
                        "importance": widget_details.importance,
                        "frequency": widget_details.frequency
                    })
                
                widgets_data.append(widget_data)
            
            return {
                "date": target_date.isoformat(),
                "widgets": widgets_data,
                "total_widgets": len(widgets_data),
                "ai_generated": bool(widgets_data),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get today's widgets for user {user_id}: {e}")
            raise
    
    def get_all_widget_list(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get all dashboard widgets for the user
        Returns all widget configurations from DashboardWidgetDetails.
        """
        try:
            widgets = self.db.query(DashboardWidgetDetails).filter(
                DashboardWidgetDetails.user_id == user_id,
                DashboardWidgetDetails.delete_flag == False
            ).order_by(DashboardWidgetDetails.importance.desc()).all()
            
            widgets_data = []
            for widget in widgets:
                widget_data = {
                    "id": widget.id,
                    "title": widget.title,
                    "widget_type": widget.widget_type,
                    "frequency": widget.frequency,
                    "importance": widget.importance,
                    "is_permanent": widget.is_permanent,
                    "category": widget.category,
                    "created_at": widget.created_at.isoformat(),
                    "updated_at": widget.updated_at.isoformat()
                }
                widgets_data.append(widget_data)
            
            return {
                "widgets": widgets_data,
                "total_widgets": len(widgets_data)
            }
        except Exception as e:
            logger.error(f"Failed to get all widgets for user {user_id}: {e}")
            raise
    
    def add_widget_to_today(self, widget_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Add a widget to today's dashboard
        Creates entries in DailyWidget and corresponding activity tables.
        """
        try:
            from models.database import DailyWidget
            from services.service_factory import ServiceFactory
            
            # Check if widget exists and belongs to user
            widget = self.db.query(DashboardWidgetDetails).filter(
                DashboardWidgetDetails.id == widget_id,
                DashboardWidgetDetails.user_id == user_id,
                DashboardWidgetDetails.delete_flag == False
            ).first()
            
            if not widget:
                raise ValueError("Widget not found")
            
            # Check if widget is already in today's dashboard
            today = date.today()
            existing_daily_widget = self.db.query(DailyWidget).filter(
                DailyWidget.date == today,
                DailyWidget.widget_ids.contains([widget_id]),
                DailyWidget.delete_flag == False
            ).first()
            
            if existing_daily_widget:
                if not existing_daily_widget.is_active:
                    existing_daily_widget.is_active = True
                    existing_daily_widget.updated_at = datetime.now(timezone.utc)
                    self.db.commit()
                    return {
                        "message": "Widget was already in today's dashboard but was inactive. It has now been re-activated.",
                        "daily_widget_id": existing_daily_widget.id,
                        "widget_id": widget_id,
                        "widget_type": widget.widget_type,
                        "title": widget.title,
                        "action_type": "reactivated existing daily widget"
                    }
                else:
                    raise ValueError("Widget is already in today's dashboard")
            
            # Special handling for todo widgets (todo-task and todo-habit, but not todo-event)
            daily_widget = None
            if widget.widget_type in ["todo-task", "todo-habit"]:
                # Check if there's already a DailyWidget for this specific todo widget type today
                existing_todo_daily_widget = self.db.query(DailyWidget).filter(
                    DailyWidget.date == today,
                    DailyWidget.widget_type == widget.widget_type,
                    DailyWidget.delete_flag == False
                ).first()
                
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
                        self.db.flush()
                        
                        logger.info(f"Updated DailyWidget {daily_widget.id} with widget_ids: {daily_widget.widget_ids}")
                    else:
                        logger.info(f"Widget {widget_id} already exists in DailyWidget {daily_widget.id}")
                else:
                    # Create new DailyWidget for this specific todo widget type
                    logger.info(f"Creating new DailyWidget for widget {widget_id} of type {widget.widget_type}")
                    daily_widget = DailyWidget(
                        widget_ids=[widget_id],
                        widget_type=widget.widget_type,
                        priority="HIGH",
                        reasoning=f"Manually added {widget.title} to today's dashboard",
                        date=today,
                        created_by=user_id
                    )
                    self.db.add(daily_widget)
                    self.db.flush()
            else:
                # For non-todo widgets, create new DailyWidget entry
                daily_widget = DailyWidget(
                    widget_ids=[widget_id],
                    widget_type=widget.widget_type,
                    priority="HIGH",
                    reasoning=f"Manually added {widget.title} to today's dashboard",
                    date=today,
                    created_by=user_id
                )
                self.db.add(daily_widget)
                self.db.flush()
            
            # Create activity entries using service methods
            service_factory = ServiceFactory(self.db)
            
            if widget.widget_type in ["todo-habit", "todo-task", "todo-event"]:
                activity_result = service_factory.todo_service.create_todo_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create todo activity for widget {widget_id}")
            
            elif widget.widget_type == "singleitemtracker":
                activity_result = service_factory.single_item_tracker_service.create_tracker_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create tracker activity for widget {widget_id}")
            
            elif widget.widget_type == "alarm":
                activity_result = service_factory.alarm_service.create_alarm_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create alarm activity for widget {widget_id}")
            
            elif widget.widget_type == "websearch":
                activity_result = service_factory.websearch_service.create_websearch_activity_for_today(daily_widget.id, widget_id, user_id)
                if not activity_result:
                    logger.warning(f"Failed to create websearch activity for widget {widget_id}")
            
            self.db.commit()
            
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
                "message": f"Widget added to today's dashboard successfully ({action_type})",
                "daily_widget_id": daily_widget.id,
                "widget_id": widget_id,
                "widget_type": widget.widget_type,
                "title": widget.title,
                "action_type": action_type
            }
        except Exception as e:
            logger.error(f"Failed to add widget {widget_id} to today's dashboard for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    def update_daily_widget_active(self, daily_widget_id: str, is_active: bool) -> Dict[str, Any]:
        """
        Update the is_active column for a DailyWidget (activate/deactivate widget)
        """
        try:
            from models.database import DailyWidget
            
            daily_widget = self.db.query(DailyWidget).filter(
                DailyWidget.id == daily_widget_id,
                DailyWidget.delete_flag == False
            ).first()
            
            if not daily_widget:
                raise ValueError("DailyWidget not found")
            
            daily_widget.is_active = is_active
            daily_widget.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            
            return {
                "message": "DailyWidget is_active updated successfully", 
                "daily_widget_id": daily_widget_id, 
                "is_active": is_active
            }
        except Exception as e:
            logger.error(f"Failed to update is_active for DailyWidget {daily_widget_id}: {e}")
            self.db.rollback()
            raise 