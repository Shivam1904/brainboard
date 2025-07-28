from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.database_models import Widget
from data.base_data import BaseDataAccess

class WidgetDataAccess(BaseDataAccess[Widget]):
    """Data access layer for Widget operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def create(self, entity: Widget) -> Widget:
        """Create a new widget"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    async def get_by_id(self, widget_id: str) -> Optional[Widget]:
        """Get widget by ID"""
        return self.db.query(Widget).filter(Widget.widget_id == widget_id).first()
    
    async def update(self, widget_id: str, entity: Widget) -> Optional[Widget]:
        """Update widget by ID"""
        db_widget = await self.get_by_id(widget_id)
        if not db_widget:
            return None
        
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and hasattr(db_widget, key):
                setattr(db_widget, key, value)
        
        self.db.commit()
        self.db.refresh(db_widget)
        return db_widget
    
    async def delete(self, widget_id: str) -> bool:
        """Delete widget by ID"""
        db_widget = await self.get_by_id(widget_id)
        if not db_widget:
            return False
        
        self.db.delete(db_widget)
        self.db.commit()
        return True
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Widget]:
        """List all widgets with pagination"""
        return self.db.query(Widget).offset(offset).limit(limit).all()
    
    async def get_by_user_id(self, user_id: str, limit: int = 100) -> List[Widget]:
        """Get all widgets for a specific user"""
        return (
            self.db.query(Widget)
            .filter(Widget.user_id == user_id)
            .order_by(desc(Widget.created_at))
            .limit(limit)
            .all()
        )
    
    async def get_by_user_and_type(self, user_id: str, widget_type: str) -> List[Widget]:
        """Get widgets by user and type"""
        return (
            self.db.query(Widget)
            .filter(Widget.user_id == user_id, Widget.widget_type == widget_type)
            .order_by(desc(Widget.created_at))
            .all()
        )
