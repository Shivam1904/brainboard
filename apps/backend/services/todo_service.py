"""
Todo Service - Business logic for todo operations
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging

from models.database import (
    ToDoDetails, ToDoItemActivity, DashboardWidgetDetails, DailyWidget
)

logger = logging.getLogger(__name__)

class TodoService:
    """Service for todo operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_today_todo_list(self, todo_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get today's todo activities filtered by type"""
        try:
            query = self.db.query(ToDoItemActivity).join(
                DailyWidget
            ).filter(
                DailyWidget.date == date.today(),
                DailyWidget.delete_flag == False
            )
            
            if todo_type:
                query = query.join(ToDoDetails).filter(
                    ToDoDetails.todo_type == todo_type
                )
            
            activities = query.all()
            
            result = []
            for activity in activities:
                todo_details = self.db.query(ToDoDetails).filter(
                    ToDoDetails.id == activity.tododetails_id
                ).first()
                
                if todo_details:
                    result.append({
                        "id": activity.id,
                        "widget_id": activity.widget_id,
                        "daily_widget_id": activity.daily_widget_id,
                        "todo_details_id": activity.tododetails_id,
                        "title": todo_details.title,
                        "todo_type": todo_details.todo_type,
                        "description": todo_details.description,
                        "due_date": todo_details.due_date.isoformat() if todo_details.due_date else None,
                        "status": activity.status,
                        "progress": activity.progress,
                        "created_at": activity.created_at.isoformat(),
                        "updated_at": activity.updated_at.isoformat()
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error getting today's todo list: {e}")
            return []
    
    def update_activity(self, activity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update todo activity"""
        try:
            logger.info(f"Attempting to update todo activity with ID: {activity_id}")
            logger.info(f"Update data: {update_data}")
            
            # First, let's check if the activity exists
            activity = self.db.query(ToDoItemActivity).filter(
                ToDoItemActivity.id == activity_id
            ).first()
            
            if not activity:
                logger.error(f"Todo activity with ID {activity_id} not found in database")
                # Let's also log all todo activities to see what's available
                all_activities = self.db.query(ToDoItemActivity).all()
                logger.info(f"All todo activities in database: {[{'id': a.id, 'widget_id': a.widget_id, 'created_at': a.created_at} for a in all_activities]}")
                return None
            
            logger.info(f"Found todo activity: {activity.id}, widget_id: {activity.widget_id}")
            
            # Update fields
            if "status" in update_data:
                activity.status = update_data["status"]
                logger.info(f"Updated status to: {update_data['status']}")
            if "progress" in update_data:
                activity.progress = update_data["progress"]
                logger.info(f"Updated progress to: {update_data['progress']}")
            
            activity.updated_at = datetime.utcnow()
            activity.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            logger.info(f"Successfully updated todo activity {activity_id}")
            
            return {
                "activity_id": activity.id,
                "status": activity.status,
                "progress": activity.progress,
                "updated_at": activity.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating todo activity {activity_id}: {e}")
            self.db.rollback()
            return None
    
    def get_todo_details_and_activity(self, daily_widget_id: str, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get todo details and activity for a specific widget"""
        try:
            # Get todo details
            todo_details = self.db.query(ToDoDetails).filter(
                ToDoDetails.widget_id == widget_id
            ).first()
            
            if not todo_details:
                return None
            
            # Get activity
            activity = self.db.query(ToDoItemActivity).filter(
                ToDoItemActivity.daily_widget_id == daily_widget_id,
                ToDoItemActivity.widget_id == widget_id
            ).first()
            
            return {
                "todo_details": {
                    "id": todo_details.id,
                    "widget_id": todo_details.widget_id,
                    "title": todo_details.title,
                    "todo_type": todo_details.todo_type,
                    "description": todo_details.description,
                    "due_date": todo_details.due_date.isoformat() if todo_details.due_date else None,
                    "created_at": todo_details.created_at.isoformat(),
                    "updated_at": todo_details.updated_at.isoformat()
                },
                "activity": {
                    "id": activity.id if activity else None,
                    "status": activity.status if activity else None,
                    "progress": activity.progress if activity else None,
                    "created_at": activity.created_at.isoformat() if activity else None,
                    "updated_at": activity.updated_at.isoformat() if activity else None
                } if activity else None
            }
        except Exception as e:
            logger.error(f"Error getting todo details and activity: {e}")
            return None
    
    def get_todo_list_by_type(self, todo_type: str) -> List[Dict[str, Any]]:
        """Get all todo details filtered by type"""
        try:
            todos = self.db.query(ToDoDetails).filter(
                ToDoDetails.todo_type == todo_type,
                ToDoDetails.delete_flag == False
            ).all()
            
            return [
                {
                    "id": todo.id,
                    "widget_id": todo.widget_id,
                    "title": todo.title,
                    "todo_type": todo.todo_type,
                    "description": todo.description,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "created_at": todo.created_at.isoformat(),
                    "updated_at": todo.updated_at.isoformat()
                }
                for todo in todos
            ]
        except Exception as e:
            logger.error(f"Error getting todo list by type {todo_type}: {e}")
            return []
    
    def get_todo_details(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get todo details for a specific widget"""
        try:
            todo = self.db.query(ToDoDetails).filter(
                ToDoDetails.widget_id == widget_id,
                ToDoDetails.delete_flag == False
            ).first()
            
            if not todo:
                return None
            
            return {
                "id": todo.id,
                "widget_id": todo.widget_id,
                "title": todo.title,
                "todo_type": todo.todo_type,
                "description": todo.description,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "created_at": todo.created_at.isoformat(),
                "updated_at": todo.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting todo details for widget {widget_id}: {e}")
            return None
    
    def update_todo_details(self, todo_details_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update todo details"""
        try:
            todo = self.db.query(ToDoDetails).filter(
                ToDoDetails.id == todo_details_id
            ).first()
            
            if not todo:
                return None
            
            # Update fields
            if "title" in update_data:
                todo.title = update_data["title"]
            if "todo_type" in update_data:
                todo.todo_type = update_data["todo_type"]
            if "description" in update_data:
                todo.description = update_data["description"]
            if "due_date" in update_data:
                todo.due_date = update_data["due_date"]
            
            todo.updated_at = datetime.utcnow()
            todo.updated_by = update_data.get("updated_by")
            
            self.db.commit()
            
            return {
                "id": todo.id,
                "widget_id": todo.widget_id,
                "title": todo.title,
                "todo_type": todo.todo_type,
                "description": todo.description,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "updated_at": todo.updated_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating todo details {todo_details_id}: {e}")
            self.db.rollback()
            return None 