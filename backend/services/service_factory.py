"""
Service Factory for creating service instances with proper session management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from .dashboard_widget_service import DashboardWidgetService
from .daily_widget_service import DailyWidgetService
from .widget_priority_service import WidgetPriorityService

class ServiceFactory:
    """
    Factory for creating service instances with proper session management.
    
    This factory ensures that services don't commit or rollback transactions
    prematurely, preventing cursor reset issues when multiple services
    share the same session.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._dashboard_widget_service = None
        self._daily_widget_service = None
        self._widget_priority_service = None
    
    @property
    def dashboard_widget_service(self) -> DashboardWidgetService:
        """Get dashboard widget service instance"""
        if self._dashboard_widget_service is None:
            self._dashboard_widget_service = DashboardWidgetService(self.db)
        return self._dashboard_widget_service
    
    @property
    def daily_widget_service(self) -> DailyWidgetService:
        """Get daily widget service instance"""
        if self._daily_widget_service is None:
            self._daily_widget_service = DailyWidgetService(self.db)
        return self._daily_widget_service

    @property
    def widget_priority_service(self) -> WidgetPriorityService:
        """Get widget priority service instance (uses DB for completion history)."""
        if self._widget_priority_service is None:
            self._widget_priority_service = WidgetPriorityService(self.db)
        return self._widget_priority_service
