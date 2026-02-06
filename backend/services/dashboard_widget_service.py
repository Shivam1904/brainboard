"""
Dashboard Widget Service - Consolidated service for all widget types.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from models.dashboard_widget_details import DashboardWidgetDetails
from schemas.dashboard_widget import DashboardWidgetCreate, DashboardWidgetUpdate
from config import settings

logger = logging.getLogger(__name__)


class DashboardWidgetService:
    """Service for managing dashboard widgets with JSON configuration."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_widget(self, widget_type: str, widget_data: DashboardWidgetCreate) -> DashboardWidgetDetails:
        """Create a new widget with the given configuration."""
        widget = DashboardWidgetDetails(
            user_id=settings.DEFAULT_USER_ID,
            widget_type=widget_type,
            frequency=widget_data.frequency,
            frequency_details=widget_data.frequency_details,
            importance=widget_data.importance,
            title=widget_data.title,
            description=widget_data.description,
            category=widget_data.category,
            is_permanent=widget_data.is_permanent,
            widget_config=widget_data.widget_config,
            created_by=settings.DEFAULT_USER_ID # Default create_by to system user if not in schema, or add to schema if needed. Schema doesn't have created_by.
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
            DashboardWidgetDetails.user_id == settings.DEFAULT_USER_ID,
            DashboardWidgetDetails.delete_flag == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def update_widget(self, widget_id: str, update_data: DashboardWidgetUpdate) -> Optional[DashboardWidgetDetails]:
        """Update a widget with new data."""
        widget = await self.get_widget(widget_id)
        # logger.debug(f"update_data: {update_data}")
        if not widget:
            return None
        
        # Convert Pydantic model to dict, excluding unset values
        update_dict = update_data.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2 or dict() for v1. Assuming v1/v2 compat or check installed version. simpler: dict(exclude_unset=True)
        # Let's use dict() for broad compatibility if we don't know version, or check imports.
        # But wait, standard is .dict() in v1, .model_dump() in v2.
        # Safest is update_data.dict(exclude_unset=True) if v1 or v2 (via mixin).
        # Actually, let's look at schema content again. It imports BaseModel from pydantic.
        # Usage in routes/dashboard_widgets.py implies .dict() works.
        
        update_dict = update_data.dict(exclude_unset=True)

        # Update basic fields (excluding widget_type as it shouldn't be changed after creation)
        updateable_fields = ['frequency', 'frequency_details', 'importance', 'title', 'description', 'category', 'is_permanent', 'widget_config']
        for field in updateable_fields:
            if field in update_dict:
                setattr(widget, field, update_dict[field])
                # Mark JSON fields as modified for SQLAlchemy to detect changes
                if field == 'widget_config':
                    flag_modified(widget, 'widget_config')
        
        logger.info(f"Updating widget: {widget.id}")
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
            DashboardWidgetDetails.user_id == settings.DEFAULT_USER_ID,
            DashboardWidgetDetails.widget_type == widget_type,
            DashboardWidgetDetails.delete_flag == False
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    