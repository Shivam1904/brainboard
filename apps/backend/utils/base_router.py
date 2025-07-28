"""
Base router class for widget-specific endpoints
"""

from abc import ABC, abstractmethod
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Generic, TypeVar
import logging

from core.database import get_db
from utils.router_utils import RouterUtils

logger = logging.getLogger(__name__)

# Generic types for widget data
WidgetDataType = TypeVar('WidgetDataType')
CreateRequestType = TypeVar('CreateRequestType')
UpdateRequestType = TypeVar('UpdateRequestType')
ResponseType = TypeVar('ResponseType')

class BaseWidgetRouter(ABC, Generic[WidgetDataType, CreateRequestType, UpdateRequestType, ResponseType]):
    """
    Base class for widget routers to reduce code duplication
    """
    
    def __init__(self, widget_type: str, prefix: str):
        self.widget_type = widget_type
        self.router = APIRouter(prefix=f"/api/v1/widgets/{prefix}", tags=[prefix])
        self.utils = RouterUtils()
        
        # Register common endpoints
        self._register_endpoints()
    
    def _register_endpoints(self) -> None:
        """Register common endpoints that all widgets share"""
        
        @self.router.get("/widget/{widget_id}/data")
        async def get_widget_data(
            widget_id: str,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Get complete widget data"""
            try:
                widget = self.utils.verify_widget_exists(db, widget_id, self.widget_type)
                return await self.get_widget_data_impl(widget_id, db)
            except Exception as e:
                self.utils.handle_database_error(f"get {self.widget_type} widget data", e)
        
        @self.router.delete("/widget/{widget_id}")
        async def delete_widget(
            widget_id: str,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Delete widget and all associated data"""
            try:
                widget = self.utils.verify_widget_exists(db, widget_id, self.widget_type)
                await self.delete_widget_impl(widget_id, db)
                return self.utils.format_success_response(f"Widget {widget_id} deleted successfully")
            except Exception as e:
                self.utils.handle_database_error(f"delete {self.widget_type} widget", e)
    
    @abstractmethod
    async def get_widget_data_impl(self, widget_id: str, db: Session) -> Dict[str, Any]:
        """Implementation for getting widget-specific data"""
        pass
    
    @abstractmethod
    async def delete_widget_impl(self, widget_id: str, db: Session) -> None:
        """Implementation for deleting widget-specific data"""
        pass
