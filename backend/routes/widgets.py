"""
Widgets routes for listing available widget types.
"""
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class WidgetType(BaseModel):
    """Widget type information."""
    id: str
    name: str
    description: str
    category: str
    icon: str
    config_schema: dict

@router.get("/", response_model=List[WidgetType])
async def get_available_widgets():
    """Get list of all available widget types."""
    widgets = [
        WidgetType(
            id="alarm",
            name="Alarm Widget",
            description="Set up alarms and reminders with custom times and snooze functionality",
            category="reminders",
            icon="alarm",
            config_schema={
                "title": {"type": "string", "required": True},
                "description": {"type": "string", "required": False},
                "alarm_times": {"type": "array", "items": {"type": "string"}, "required": True},
                "target_value": {"type": "string", "required": False},
                "is_snoozable": {"type": "boolean", "required": False, "default": True}
            }
        )
    ]
    
    return widgets

@router.get("/categories")
async def get_widget_categories():
    """Get list of widget categories."""
    categories = [
        {
            "id": "reminders",
            "name": "Reminders",
            "description": "Alarms, notifications, and time-based reminders"
        }
    ]
    
    return categories

@router.get("/{widget_type_id}", response_model=WidgetType)
async def get_widget_type(widget_type_id: str):
    """Get specific widget type information."""
    # This would typically fetch from a database or configuration
    # For now, we'll return a simple response
    widget_types = {
        "alarm": WidgetType(
            id="alarm",
            name="Alarm Widget",
            description="Set up alarms and reminders with custom times and snooze functionality",
            category="reminders",
            icon="alarm",
            config_schema={
                "title": {"type": "string", "required": True},
                "description": {"type": "string", "required": False},
                "alarm_times": {"type": "array", "items": {"type": "string"}, "required": True},
                "target_value": {"type": "string", "required": False},
                "is_snoozable": {"type": "boolean", "required": False, "default": True}
            }
        )
    }
    
    if widget_type_id not in widget_types:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Widget type '{widget_type_id}' not found"
        )
    
    return widget_types[widget_type_id] 