"""
Dashboard Service - Business logic for dashboard operations
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timezone
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