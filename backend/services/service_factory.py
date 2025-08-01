"""
Service Factory for creating service instances
"""

from sqlalchemy.ext.asyncio import AsyncSession
from .alarm_service import AlarmService
from .todo_service import TodoService
from .websearch_service import WebSearchService

class ServiceFactory:
    """Factory for creating service instances"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._alarm_service = None
        self._todo_service = None
        self._single_item_tracker_service = None
        self._websearch_service = None
    
    @property
    def alarm_service(self) -> AlarmService:
        """Get alarm service instance"""
        if self._alarm_service is None:
            self._alarm_service = AlarmService(self.db)
        return self._alarm_service
    
    @property
    def todo_service(self):
        """Get todo service instance - placeholder for now"""
        if self._todo_service is None:
            # Create a simple placeholder service
            self._todo_service = TodoService(self.db)
        return self._todo_service
    
    @property
    def single_item_tracker_service(self):
        """Get single item tracker service instance - placeholder for now"""
        if self._single_item_tracker_service is None:
            # Create a simple placeholder service
            self._single_item_tracker_service = SingleItemTrackerService(self.db)
        return self._single_item_tracker_service
    
    @property
    def websearch_service(self) -> WebSearchService:
        """Get websearch service instance"""
        if self._websearch_service is None:
            self._websearch_service = WebSearchService(self.db)
        return self._websearch_service


class SingleItemTrackerService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tracker_activity_for_today(self, daily_widget_id: str, widget_id: str, user_id: str):
        """Placeholder for tracker activity creation"""
        # TODO: Implement when tracker models are available
        return None 