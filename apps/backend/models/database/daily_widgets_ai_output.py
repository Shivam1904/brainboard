from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Date
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class DailyWidgetsAIOutput(Base):
    """Daily Widgets AI Output - AI-generated daily widget plans"""
    __tablename__ = "daily_widgets_ai_output"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    priority = Column(String, nullable=False)  # 'HIGH', 'LOW'
    reasoning = Column(Text, nullable=True)  # AI reasoning for selection
    result_json = Column(JSON, nullable=True)  # Full AI response as JSON
    date = Column(Date, nullable=False)  # Date for which this plan was generated
    
    # Additional AI-specific columns
    ai_model_used = Column(String, nullable=True)  # 'gpt-4', 'gpt-3.5-turbo'
    ai_prompt_used = Column(Text, nullable=True)  # The prompt sent to AI
    ai_response_time = Column(String, nullable=True)  # Time taken for AI response
    confidence_score = Column(String, nullable=True)  # AI confidence in the decision
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails") 