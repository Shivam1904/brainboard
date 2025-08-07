"""
Dashboard Widget Service - Consolidated service for all widget types.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.dashboard_widget_details import DashboardWidgetDetails

DEFAULT_USER_ID = "user_001"


class DashboardWidgetService:
    """Service for managing dashboard widgets with JSON configuration."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_widget(self, widget_type: str, config_data: Dict[str, Any]) -> DashboardWidgetDetails:
        """Create a new widget with the given configuration."""
        widget = DashboardWidgetDetails(
            user_id=DEFAULT_USER_ID,
            widget_type=widget_type,
            frequency=config_data.get('frequency', 'daily'),
            frequency_details=config_data.get('frequency_details'),
            importance=config_data.get('importance', 0.5),
            title=config_data.get('title', ''),
            description=config_data.get('description'),
            category=config_data.get('category'),
            is_permanent=config_data.get('is_permanent', False),
            widget_config=config_data.get('widget_config', {})
        )
        
        self.db.add(widget)
        await self.db.flush()
        await self.db.refresh(widget)
        return widget
    
    async def get_widget(self, widget_id: str) -> Optional[DashboardWidgetDetails]:
        """Get a specific widget by ID."""
        stmt = select(DashboardWidgetDetails).where(
            DashboardWidgetDetails.id == widget_id,
            DashboardWidgetDetails.delete_flag == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_user_widgets(self) -> List[DashboardWidgetDetails]:
        """Get all widgets for a specific user."""
        stmt = select(DashboardWidgetDetails).where(
            DashboardWidgetDetails.user_id == DEFAULT_USER_ID,
            DashboardWidgetDetails.delete_flag == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def update_widget(self, widget_id: str, update_data: Dict[str, Any]) -> Optional[DashboardWidgetDetails]:
        """Update a widget with new data."""
        widget = await self.get_widget(widget_id)
        print("update_data", update_data)
        if not widget:
            return None
        
        # Update basic fields (excluding widget_type as it shouldn't be changed after creation)
        updateable_fields = ['frequency', 'frequency_details', 'importance', 'title', 'description', 'category', 'is_permanent', 'widget_config']
        for field in updateable_fields:
            if field in update_data:
                setattr(widget, field, update_data[field])
        
        print("updating widget", widget)
        await self.db.flush()
        await self.db.refresh(widget)
        return widget
    
    async def delete_widget(self, widget_id: str) -> bool:
        """Soft delete a widget by setting delete_flag to True."""
        widget = await self.get_widget(widget_id)
        if not widget:
            return False
        
        widget.delete_flag = True
        await self.db.flush()
        return True
    
    async def get_widgets_by_type(self, widget_type: str) -> List[DashboardWidgetDetails]:
        """Get all widgets of a specific type for a user."""
        stmt = select(DashboardWidgetDetails).where(
            DashboardWidgetDetails.user_id == DEFAULT_USER_ID,
            DashboardWidgetDetails.widget_type == widget_type,
            DashboardWidgetDetails.delete_flag == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    