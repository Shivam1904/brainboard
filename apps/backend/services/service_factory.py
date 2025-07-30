"""
Service Factory - Centralized service management
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging

from .todo_service import TodoService
from .alarm_service import AlarmService
from .single_item_tracker_service import SingleItemTrackerService
from .websearch_service import WebSearchService
from .dashboard_service import DashboardService

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory for creating and managing all services with a shared database session"""
    
    def __init__(self, db: Session):
        self.db = db
        self._services = {}
    
    @property
    def todo_service(self) -> TodoService:
        """Get or create TodoService instance"""
        if 'todo' not in self._services:
            self._services['todo'] = TodoService(self.db)
        return self._services['todo']
    
    @property
    def alarm_service(self) -> AlarmService:
        """Get or create AlarmService instance"""
        if 'alarm' not in self._services:
            self._services['alarm'] = AlarmService(self.db)
        return self._services['alarm']
    
    @property
    def single_item_tracker_service(self) -> SingleItemTrackerService:
        """Get or create SingleItemTrackerService instance"""
        if 'single_item_tracker' not in self._services:
            self._services['single_item_tracker'] = SingleItemTrackerService(self.db)
        return self._services['single_item_tracker']
    
    @property
    def websearch_service(self) -> WebSearchService:
        """Get or create WebSearchService instance"""
        if 'websearch' not in self._services:
            self._services['websearch'] = WebSearchService(self.db)
        return self._services['websearch']
    
    @property
    def dashboard_service(self) -> DashboardService:
        """Get or create DashboardService instance"""
        if 'dashboard' not in self._services:
            self._services['dashboard'] = DashboardService(self.db)
        return self._services['dashboard']
    
    def commit(self):
        """Commit all changes in the database session"""
        self.db.commit()
    
    def rollback(self):
        """Rollback all changes in the database session"""
        self.db.rollback()
    
    def close(self):
        """Close the database session"""
        self.db.close() 