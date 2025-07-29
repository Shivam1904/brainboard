from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Date
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class WebSearchSummaryAIOutput(Base):
    """WebSearch Summary AI Output - AI-generated web search summaries"""
    __tablename__ = "websearch_summary_ai_output"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    query = Column(String, nullable=False)  # The search query
    result_json = Column(JSON, nullable=True)  # Full AI response as JSON
    
    # Additional AI-specific columns
    ai_model_used = Column(String, nullable=True)  # 'gpt-4', 'gpt-3.5-turbo'
    ai_prompt_used = Column(Text, nullable=True)  # The prompt sent to AI
    ai_response_time = Column(String, nullable=True)  # Time taken for AI response
    search_results_count = Column(String, nullable=True)  # Number of search results processed
    summary_length = Column(String, nullable=True)  # Length of generated summary
    sources_used = Column(JSON, nullable=True)  # List of sources used for summary
    generation_type = Column(String, nullable=False, default="ai_generated")  # 'ai_generated' or 'fallback'
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails") 