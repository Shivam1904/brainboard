from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.database_models import Summary
from data.base_data import BaseDataAccess

class SummaryDataAccess(BaseDataAccess[Summary]):
    """Data access layer for Summary operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def create(self, entity: Summary) -> Summary:
        """Create a new summary"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    async def get_by_id(self, summary_id: str) -> Optional[Summary]:
        """Get summary by ID"""
        return self.db.query(Summary).filter(Summary.summary_id == summary_id).first()
    
    async def update(self, summary_id: str, entity: Summary) -> Optional[Summary]:
        """Update summary by ID"""
        db_summary = await self.get_by_id(summary_id)
        if not db_summary:
            return None
        
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and hasattr(db_summary, key):
                setattr(db_summary, key, value)
        
        self.db.commit()
        self.db.refresh(db_summary)
        return db_summary
    
    async def delete(self, summary_id: str) -> bool:
        """Delete summary by ID"""
        db_summary = await self.get_by_id(summary_id)
        if not db_summary:
            return False
        
        self.db.delete(db_summary)
        self.db.commit()
        return True
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Summary]:
        """List all summaries with pagination"""
        return (
            self.db.query(Summary)
            .order_by(desc(Summary.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    async def get_latest_by_widget_id(self, widget_id: str) -> Optional[Summary]:
        """Get the latest summary for a specific widget"""
        return (
            self.db.query(Summary)
            .filter(Summary.widget_id == widget_id)
            .order_by(desc(Summary.created_at))
            .first()
        )
    
    async def get_history_by_widget_id(self, widget_id: str, limit: int = 50) -> List[Summary]:
        """Get summary history for a specific widget"""
        return (
            self.db.query(Summary)
            .filter(Summary.widget_id == widget_id)
            .order_by(desc(Summary.created_at))
            .limit(limit)
            .all()
        )
    
    async def count_by_widget_id(self, widget_id: str) -> int:
        """Count total summaries for a widget"""
        return self.db.query(Summary).filter(Summary.widget_id == widget_id).count()
    
    async def delete_by_widget_id(self, widget_id: str) -> bool:
        """Delete all summaries for a specific widget"""
        deleted_count = (
            self.db.query(Summary)
            .filter(Summary.widget_id == widget_id)
            .delete()
        )
        self.db.commit()
        return deleted_count > 0
