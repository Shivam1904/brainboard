from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.database_models import Widget, Summary
from models.schemas import CreateWidgetResponse, SummaryResponse, WidgetInfo
from data.widget_data import WidgetDataAccess
from data.summary_data import SummaryDataAccess
from services.base_service import BaseService
from services.summary_service import SummaryService
from core.config import settings
import uuid

logger = logging.getLogger(__name__)

class WidgetService(BaseService):
    """Service for widget business logic and operations"""
    
    def __init__(self, db: Session, summary_service: SummaryService = None):
        self.db = db
        self.widget_data = WidgetDataAccess(db)
        self.summary_data = SummaryDataAccess(db)
        self.summary_service = summary_service or SummaryService()
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate widget operation input"""
        if "query" in data:
            query = data.get("query", "")
            return isinstance(query, str) and len(query.strip()) > 0
        return True
    
    async def create_web_summary_widget(self, query: str, user_id: str = None) -> CreateWidgetResponse:
        """
        Create a new web summary widget and generate the first summary
        """
        try:
            if not await self.validate_input({"query": query}):
                raise ValueError("Invalid query for widget creation")
            
            user_id = user_id or settings.default_user_id
            widget_id = str(uuid.uuid4())
            summary_id = str(uuid.uuid4())
            
            logger.info(f"Creating web summary widget for user {user_id} with query: {query}")
            
            # Create widget in database
            widget = Widget(
                widget_id=widget_id,
                user_id=user_id,
                widget_type="web-summary",
                current_query=query,
                settings={"max_results": settings.max_search_results}
            )
            
            created_widget = await self.widget_data.create(widget)
            
            # Generate first summary
            summary_response = await self.summary_service.generate_summary(query, summary_id)
            
            # Save summary to database
            summary = Summary(
                summary_id=summary_id,
                widget_id=widget_id,
                query=query,
                summary_text=summary_response.summary,
                sources_json=summary_response.sources
            )
            
            await self.summary_data.create(summary)
            
            # Create response
            response = CreateWidgetResponse(
                widget_id=widget_id,
                user_id=user_id,
                summary=summary_response,
                widget_created_at=created_widget.created_at.isoformat() + "Z"
            )
            
            logger.info(f"Successfully created widget {widget_id}")
            return response
            
        except Exception as e:
            logger.error(f"Widget creation failed: {str(e)}")
            raise
    
    async def generate_new_summary(self, widget_id: str, query: str) -> SummaryResponse:
        """Generate a new summary for an existing widget"""
        try:
            if not await self.validate_input({"query": query}):
                raise ValueError("Invalid query for summary generation")
            
            # Verify widget exists
            widget = await self.widget_data.get_by_id(widget_id)
            if not widget:
                raise ValueError(f"Widget {widget_id} not found")
            
            summary_id = str(uuid.uuid4())
            
            logger.info(f"Generating new summary for widget {widget_id} with query: {query}")
            
            # Generate summary
            summary_response = await self.summary_service.generate_summary(query, summary_id)
            
            # Save summary to database
            summary = Summary(
                summary_id=summary_id,
                widget_id=widget_id,
                query=query,
                summary_text=summary_response.summary,
                sources_json=summary_response.sources
            )
            
            await self.summary_data.create(summary)
            
            # Update widget's current query
            widget.current_query = query
            widget.updated_at = datetime.utcnow()
            await self.widget_data.update(widget_id, widget)
            
            logger.info(f"Successfully generated new summary for widget {widget_id}")
            return summary_response
            
        except Exception as e:
            logger.error(f"Summary generation failed for widget {widget_id}: {str(e)}")
            raise
    
    async def get_latest_summary(self, widget_id: str) -> Optional[SummaryResponse]:
        """Get the latest summary for a widget"""
        try:
            # Verify widget exists
            widget = await self.widget_data.get_by_id(widget_id)
            if not widget:
                raise ValueError(f"Widget {widget_id} not found")
            
            # Get latest summary
            latest_summary = await self.summary_data.get_latest_by_widget_id(widget_id)
            if not latest_summary:
                return None
            
            # Convert to response format
            summary_response = SummaryResponse(
                id=latest_summary.summary_id,
                query=latest_summary.query,
                summary=latest_summary.summary_text,
                sources=latest_summary.sources_json or [],
                createdAt=latest_summary.created_at.isoformat() + "Z"
            )
            
            return summary_response
            
        except Exception as e:
            logger.error(f"Failed to get latest summary for widget {widget_id}: {str(e)}")
            raise
    
    async def get_widget_info(self, widget_id: str) -> Optional[WidgetInfo]:
        """Get complete widget information including latest summary"""
        try:
            widget = await self.widget_data.get_by_id(widget_id)
            if not widget:
                return None
            
            # Get latest summary
            latest_summary = await self.get_latest_summary(widget_id)
            
            widget_info = WidgetInfo(
                widget_id=widget.widget_id,
                user_id=widget.user_id,
                widget_type=widget.widget_type,
                current_query=widget.current_query,
                settings=widget.settings,
                latest_summary=latest_summary,
                created_at=widget.created_at.isoformat() + "Z",
                updated_at=widget.updated_at.isoformat() + "Z"
            )
            
            return widget_info
            
        except Exception as e:
            logger.error(f"Failed to get widget info for {widget_id}: {str(e)}")
            raise
    
    async def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget and all its summaries"""
        try:
            # Verify widget exists
            widget = await self.widget_data.get_by_id(widget_id)
            if not widget:
                return False
            
            # Delete all summaries for this widget
            await self.summary_data.delete_by_widget_id(widget_id)
            
            # Delete the widget
            deleted = await self.widget_data.delete(widget_id)
            
            if deleted:
                logger.info(f"Successfully deleted widget {widget_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete widget {widget_id}: {str(e)}")
            raise
