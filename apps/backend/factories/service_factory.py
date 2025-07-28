from sqlalchemy.orm import Session
from services.web_search_service import WebSearchService
from services.ai_summarization_service import AISummarizationService
from services.summary_service import SummaryService
from services.widget_service import WidgetService

class ServiceFactory:
    """Factory for creating service instances with proper dependencies"""
    
    @staticmethod
    def create_web_search_service() -> WebSearchService:
        """Create web search service instance"""
        return WebSearchService()
    
    @staticmethod
    def create_ai_summarization_service() -> AISummarizationService:
        """Create AI summarization service instance"""
        return AISummarizationService()
    
    @staticmethod
    def create_summary_service(
        web_search: WebSearchService = None,
        ai_service: AISummarizationService = None
    ) -> SummaryService:
        """Create summary service with dependencies"""
        return SummaryService(
            web_search=web_search or ServiceFactory.create_web_search_service(),
            ai_service=ai_service or ServiceFactory.create_ai_summarization_service()
        )
    
    @staticmethod
    def create_widget_service(
        db: Session,
        summary_service: SummaryService = None
    ) -> WidgetService:
        """Create widget service with database session and dependencies"""
        return WidgetService(
            db=db,
            summary_service=summary_service or ServiceFactory.create_summary_service()
        )
