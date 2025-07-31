"""
Widget service for business logic.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
import logging

from models.dashboard_widget_details import DashboardWidgetDetails
from models.alarm_details import AlarmDetails
from models.todo_details import TodoDetails
from schemas.widget import WidgetResponse, WidgetTypeResponse, WidgetCategoryResponse, CreateWidgetRequest, CreateWidgetResponse

# ============================================================================
# CONSTANTS
# ============================================================================
logger = logging.getLogger(__name__)

# Widget type definitions
WIDGET_TYPE_DEFINITIONS = {
    "alarm": {
        "id": "alarm",
        "name": "Alarm Widget",
        "description": "Set up alarms and reminders with custom times and snooze functionality",
        "category": "reminders",
        "icon": "alarm",
        "config_schema": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False},
            "alarm_times": {"type": "array", "items": {"type": "string"}, "required": True},
            "target_value": {"type": "string", "required": False},
            "is_snoozable": {"type": "boolean", "required": False, "default": True}
        }
    },
    "todo-habit": {
        "id": "todo-habit",
        "name": "Habit Widget",
        "description": "Track daily habits and routines",
        "category": "health",
        "icon": "repeat",
        "config_schema": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False}
        }
    },
    "todo-task": {
        "id": "todo-task",
        "name": "Task Widget",
        "description": "Manage tasks with due dates and progress tracking",
        "category": "work",
        "icon": "check-square",
        "config_schema": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False},
            "due_date": {"type": "date", "required": False}
        }
    },
    "todo-event": {
        "id": "todo-event",
        "name": "Event Widget",
        "description": "Track events and milestones",
        "category": "productivity",
        "icon": "calendar",
        "config_schema": {
            "title": {"type": "string", "required": True},
            "description": {"type": "string", "required": False},
            "due_date": {"type": "date", "required": False}
        }
    }
}

# Category definitions
CATEGORY_DEFINITIONS = {
    "reminders": {
        "id": "reminders",
        "name": "Reminders",
        "description": "Alarms, notifications, and time-based reminders",
        "icon": "bell"
    },
    "health": {
        "id": "health",
        "name": "Health & Wellness",
        "description": "Health tracking, exercise, and wellness widgets",
        "icon": "heart"
    },
    "work": {
        "id": "work",
        "name": "Work & Productivity",
        "description": "Task management, productivity, and work-related widgets",
        "icon": "briefcase"
    }
}

# ============================================================================
# SERVICE CLASS
# ============================================================================
class WidgetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_widget_types(self) -> List[WidgetTypeResponse]:
        """Get available widget types with counts."""
        try:
            # Get counts for each widget type
            stmt = select(DashboardWidgetDetails.widget_type)
            result = await self.db.execute(stmt)
            widget_types = result.scalars().all()
            
            # Count occurrences
            type_counts = {}
            for widget_type in widget_types:
                type_counts[widget_type] = type_counts.get(widget_type, 0) + 1
            
            # Build response with counts using Pydantic models
            available_types = []
            for widget_id, definition in WIDGET_TYPE_DEFINITIONS.items():
                available_types.append(WidgetTypeResponse(
                    **definition,
                    count=type_counts.get(widget_id, 0)
                ))
            
            return available_types
        except Exception as e:
            logger.error(f"Error getting available widget types: {e}")
            raise

    async def get_widget_categories(self) -> List[WidgetCategoryResponse]:
        """Get widget categories."""
        return [WidgetCategoryResponse(**category) for category in CATEGORY_DEFINITIONS.values()]

    async def get_widget_type(self, widget_type_id: str) -> Optional[WidgetTypeResponse]:
        """Get specific widget type information."""
        definition = WIDGET_TYPE_DEFINITIONS.get(widget_type_id)
        if definition:
            return WidgetTypeResponse(**definition)
        return None

    async def get_user_widgets(self, user_id: str) -> List[WidgetResponse]:
        """Get all widgets for a user."""
        try:
            stmt = select(DashboardWidgetDetails).where(
                DashboardWidgetDetails.user_id == user_id
            )
            result = await self.db.execute(stmt)
            widgets = result.scalars().all()
            
            # Use Pydantic auto-conversion
            return [WidgetResponse.model_validate(widget) for widget in widgets]
        except Exception as e:
            logger.error(f"Error getting user widgets: {e}")
            raise

    async def create_widget(self, request: CreateWidgetRequest, user_id: str) -> CreateWidgetResponse:
        """Create a new dashboard widget with all necessary details."""
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
            await self.db.commit()
            await self.db.refresh(widget)
            
            # Create corresponding details table entry based on widget type
            if request.widget_type == "alarm":
                await self._create_alarm_details(widget.id, request, user_id)
            elif request.widget_type in ["todo-habit", "todo-task", "todo-event"]:
                await self._create_todo_details(widget.id, request, user_id)
            
            await self.db.commit()
            
            return CreateWidgetResponse(
                success=True,
                message="Widget created successfully",
                widget_id=widget.id,
                widget_type=widget.widget_type,
                title=widget.title
            )
            
        except Exception as e:
            logger.error(f"Failed to create widget for user {user_id}: {e}")
            await self.db.rollback()
            raise

    async def _create_alarm_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create alarm details."""
        # Use provided alarm time or default to 09:00
        alarm_times = [request.alarm_time] if request.alarm_time else ["09:00"]
        
        alarm_details = AlarmDetails(
            widget_id=widget_id,
            title=request.title,
            alarm_times=alarm_times
        )
        
        self.db.add(alarm_details)
        await self.db.commit()
        await self.db.refresh(alarm_details)

    async def _create_todo_details(self, widget_id: str, request: CreateWidgetRequest, user_id: str) -> None:
        """Create todo details."""
        # Map widget_type to todo_type
        todo_type_mapping = {
            "todo-habit": "todo-habit",
            "todo-task": "todo-task", 
            "todo-event": "todo-event"
        }
        
        # Parse due_date if provided
        due_date = None
        if request.due_date:
            try:
                from datetime import datetime
                due_date = datetime.strptime(request.due_date, "%Y-%m-%d").date()
            except ValueError:
                due_date = None
        
        todo_details = TodoDetails(
            widget_id=widget_id,
            title=request.title,
            todo_type=todo_type_mapping.get(request.widget_type, "todo-task"),
            description=request.description,
            due_date=due_date
        )
        
        self.db.add(todo_details)
        await self.db.commit()
        await self.db.refresh(todo_details) 