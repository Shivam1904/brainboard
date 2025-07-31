"""
TODO service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

from models.todo_details import TodoDetails
from models.todo_item_activity import TodoItemActivity

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Default values
DEFAULT_SYSTEM_USER = "system"
DEFAULT_USER = "user_001"

# ============================================================================
# SERVICE CLASS
# ============================================================================
class TodoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_todo_details_and_activity(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get todo details and activity for a widget."""
        try:
            # Get todo details
            stmt = select(TodoDetails).where(
                TodoDetails.widget_id == widget_id
            )
            result = await self.db.execute(stmt)
            todo_details = result.scalars().first()

            if not todo_details:
                return {"todo_details": None, "activities": []}

            # Get today's activities
            today = datetime.now().date()
            stmt = select(TodoItemActivity).where(
                TodoItemActivity.tododetails_id == todo_details.id,
                TodoItemActivity.created_at >= today
            )
            result = await self.db.execute(stmt)
            activities = result.scalars().all()

            return {
                "todo_details": {
                    "id": todo_details.id,
                    "widget_id": todo_details.widget_id,
                    "title": todo_details.title,
                    "todo_type": todo_details.todo_type,
                    "description": todo_details.description,
                    "due_date": todo_details.due_date,
                    "created_at": todo_details.created_at,
                    "updated_at": todo_details.updated_at
                },
                "activities": [
                    {
                        "id": activity.id,
                        "daily_widget_id": activity.daily_widget_id,
                        "widget_id": activity.widget_id,
                        "tododetails_id": activity.tododetails_id,
                        "status": activity.status,
                        "progress": activity.progress,
                        "created_at": activity.created_at,
                        "updated_at": activity.updated_at
                    }
                    for activity in activities
                ]
            }
        except Exception as e:
            logger.error(f"Error getting todo details and activity: {e}")
            raise

    async def update_status(self, activity_id: str, user_id: str, status: str) -> Dict[str, Any]:
        """Update todo activity status."""
        try:
            stmt = select(TodoItemActivity).where(TodoItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update activity
            activity.status = status
            activity.updated_at = datetime.now()
            activity.updated_by = user_id

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": f"Status updated to {status}",
                "activity": {
                    "id": activity.id,
                    "status": activity.status,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            raise

    async def update_progress(self, activity_id: str, user_id: str, progress: int) -> Dict[str, Any]:
        """Update todo activity progress."""
        try:
            stmt = select(TodoItemActivity).where(TodoItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update activity
            activity.progress = progress
            activity.updated_at = datetime.now()
            activity.updated_by = user_id

            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": f"Progress updated to {progress}%",
                "activity": {
                    "id": activity.id,
                    "progress": activity.progress,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            raise

    async def update_activity(self, activity_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a todo activity."""
        try:
            stmt = select(TodoItemActivity).where(TodoItemActivity.id == activity_id)
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            if not activity:
                return {"success": False, "message": "Activity not found"}

            # Update fields
            for key, value in update_data.items():
                if hasattr(activity, key):
                    setattr(activity, key, value)

            activity.updated_at = datetime.now()
            activity.updated_by = user_id
            await self.db.commit()
            await self.db.refresh(activity)

            return {
                "success": True,
                "message": "Activity updated",
                "activity": {
                    "id": activity.id,
                    "updated_at": activity.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
            raise

    async def get_todo_details(self, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get todo details for a widget."""
        try:
            stmt = select(TodoDetails).where(
                TodoDetails.widget_id == widget_id
            )
            result = await self.db.execute(stmt)
            todo_details = result.scalars().first()

            if not todo_details:
                return None

            return {
                "id": todo_details.id,
                "widget_id": todo_details.widget_id,
                "title": todo_details.title,
                "todo_type": todo_details.todo_type,
                "description": todo_details.description,
                "due_date": todo_details.due_date,
                "created_at": todo_details.created_at,
                "updated_at": todo_details.updated_at
            }
        except Exception as e:
            logger.error(f"Error getting todo details: {e}")
            raise

    async def create_todo(self, user_id: str, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new todo."""
        try:
            from models.dashboard_widget_details import DashboardWidgetDetails
            import uuid
            
            # Create widget first
            widget_id = str(uuid.uuid4())
            widget = DashboardWidgetDetails(
                id=widget_id,
                user_id=user_id,
                widget_type="todo",
                frequency="daily",
                importance=0.5,
                title=todo_data.get("title", "Todo"),
                category="Productivity",
                is_permanent=False
            )
            self.db.add(widget)
            
            # Create todo details
            todo_details = TodoDetails(
                widget_id=widget_id,
                title=todo_data.get("title", "Todo"),
                todo_type=todo_data.get("todo_type", "task"),
                description=todo_data.get("description"),
                due_date=todo_data.get("due_date")
            )
            self.db.add(todo_details)
            
            await self.db.commit()
            await self.db.refresh(todo_details)
            
            return {
                "success": True,
                "message": f"Todo '{todo_details.title}' created successfully",
                "data": {
                    "widget_id": widget_id,
                    "todo_id": todo_details.id,
                    "todo": {
                        "title": todo_details.title,
                        "todo_type": todo_details.todo_type,
                        "description": todo_details.description,
                        "due_date": todo_details.due_date
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating todo: {e}")
            await self.db.rollback()
            return {"success": False, "message": f"Failed to create todo: {str(e)}"}

    async def get_user_todos(self, user_id: str) -> Dict[str, Any]:
        """Get all todos for a user."""
        try:
            from models.dashboard_widget_details import DashboardWidgetDetails
            
            # Get all todo widgets for the user
            stmt = select(TodoDetails).join(DashboardWidgetDetails).where(
                DashboardWidgetDetails.user_id == user_id
            )
            result = await self.db.execute(stmt)
            todos = result.scalars().all()
            
            return {
                "success": True,
                "todos": [
                    {
                        "id": todo.id,
                        "widget_id": todo.widget_id,
                        "title": todo.title,
                        "todo_type": todo.todo_type,
                        "description": todo.description,
                        "due_date": todo.due_date.isoformat() if todo.due_date else None,
                        "created_at": todo.created_at.isoformat() if todo.created_at else None,
                        "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
                    }
                    for todo in todos
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user todos: {e}")
            return {"success": False, "message": f"Failed to get user todos: {str(e)}"}

    async def get_todos_by_type(self, user_id: str, todo_type: str) -> Dict[str, Any]:
        """Get todos by type (todo-habit, todo-task, todo-event)."""
        try:
            from models.dashboard_widget_details import DashboardWidgetDetails
            
            # Get todos of specific type for the user
            stmt = select(TodoDetails).join(DashboardWidgetDetails).where(
                DashboardWidgetDetails.user_id == user_id,
                TodoDetails.todo_type == todo_type
            )
            result = await self.db.execute(stmt)
            todos = result.scalars().all()
            
            return {
                "success": True,
                "todo_type": todo_type,
                "todos": [
                    {
                        "id": todo.id,
                        "widget_id": todo.widget_id,
                        "title": todo.title,
                        "todo_type": todo.todo_type,
                        "description": todo.description,
                        "due_date": todo.due_date.isoformat() if todo.due_date else None,
                        "created_at": todo.created_at.isoformat() if todo.created_at else None,
                        "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
                    }
                    for todo in todos
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting todos by type: {e}")
            return {"success": False, "message": f"Failed to get todos by type: {str(e)}"}

    async def update_todo_details(self, todo_details_id: str, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update todo details."""
        try:
            stmt = select(TodoDetails).where(TodoDetails.id == todo_details_id)
            result = await self.db.execute(stmt)
            todo_details = result.scalars().first()

            if not todo_details:
                return {"success": False, "message": "Todo details not found"}

            # Update fields
            for key, value in update_data.items():
                if hasattr(todo_details, key):
                    setattr(todo_details, key, value)

            todo_details.updated_at = datetime.now()
            todo_details.updated_by = user_id
            await self.db.commit()
            await self.db.refresh(todo_details)

            return {
                "success": True,
                "message": "Todo details updated",
                "todo_details": {
                    "id": todo_details.id,
                    "title": todo_details.title,
                    "todo_type": todo_details.todo_type,
                    "description": todo_details.description,
                    "due_date": todo_details.due_date,
                    "updated_at": todo_details.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating todo details: {e}")
            raise

    async def get_today_todo_list(self, user_id: str, todo_type: str) -> Dict[str, Any]:
        """Get today's todo activities filtered by type (habit/task/event)."""
        try:
            from models.daily_widget import DailyWidget
            from models.dashboard_widget_details import DashboardWidgetDetails
            
            # Get today's date
            today = datetime.now().date()
            
            # Get today's daily widgets for this todo type
            stmt = select(DailyWidget).where(
                DailyWidget.widget_type == todo_type,
                DailyWidget.date == today
            )
            result = await self.db.execute(stmt)
            daily_widgets = result.scalars().all()
            
            if not daily_widgets:
                return {
                    "todo_type": todo_type,
                    "todos": [],
                    "total_todos": 0
                }
            
            # Get all todo activities for today's daily widgets
            all_todos = []
            for daily_widget in daily_widgets:
                stmt = select(TodoItemActivity).where(
                    TodoItemActivity.daily_widget_id == daily_widget.id
                )
                result = await self.db.execute(stmt)
                activities = result.scalars().all()
                
                for activity in activities:
                    # Get todo details for this activity
                    stmt = select(TodoDetails).where(TodoDetails.id == activity.tododetails_id)
                    result = await self.db.execute(stmt)
                    todo_details = result.scalars().first()
                    
                    if todo_details:
                        all_todos.append({
                            "id": activity.id,
                            "daily_widget_id": activity.daily_widget_id,
                            "widget_id": activity.widget_id,
                            "tododetails_id": activity.tododetails_id,
                            "title": todo_details.title,
                            "todo_type": todo_details.todo_type,
                            "description": todo_details.description,
                            "due_date": todo_details.due_date.isoformat() if todo_details.due_date else None,
                            "status": activity.status,
                            "progress": activity.progress,
                            "created_at": activity.created_at.isoformat() if activity.created_at else None,
                            "updated_at": activity.updated_at.isoformat() if activity.updated_at else None
                        })
            
            return {
                "todo_type": todo_type,
                "todos": all_todos,
                "total_todos": len(all_todos)
            }
        except Exception as e:
            logger.error(f"Error getting today's todo list: {e}")
            return {"success": False, "message": f"Failed to get today's todo list: {str(e)}"}

    async def get_todo_item_details_and_activity(self, daily_widget_id: str, widget_id: str, user_id: str) -> Dict[str, Any]:
        """Get todo item details and activity for a specific widget."""
        try:
            # Get todo details
            stmt = select(TodoDetails).where(TodoDetails.widget_id == widget_id)
            result = await self.db.execute(stmt)
            todo_details = result.scalars().first()

            if not todo_details:
                return {"todo_details": None, "activity": None}

            # Get activity for this specific daily widget and todo
            stmt = select(TodoItemActivity).where(
                TodoItemActivity.daily_widget_id == daily_widget_id,
                TodoItemActivity.tododetails_id == todo_details.id
            )
            result = await self.db.execute(stmt)
            activity = result.scalars().first()

            return {
                "todo_details": {
                    "id": todo_details.id,
                    "widget_id": todo_details.widget_id,
                    "title": todo_details.title,
                    "todo_type": todo_details.todo_type,
                    "description": todo_details.description,
                    "due_date": todo_details.due_date.isoformat() if todo_details.due_date else None,
                    "created_at": todo_details.created_at.isoformat() if todo_details.created_at else None,
                    "updated_at": todo_details.updated_at.isoformat() if todo_details.updated_at else None
                },
                "activity": {
                    "id": activity.id,
                    "status": activity.status,
                    "progress": activity.progress,
                    "created_at": activity.created_at.isoformat() if activity.created_at else None,
                    "updated_at": activity.updated_at.isoformat() if activity.updated_at else None
                } if activity else None
            }
        except Exception as e:
            logger.error(f"Error getting todo item details and activity: {e}")
            return {"success": False, "message": f"Failed to get todo item details and activity: {str(e)}"} 