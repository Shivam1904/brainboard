"""
WebSearch item activity model for daily websearch activities.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import BaseModel

# ============================================================================
# MODEL
# ============================================================================
class WebSearchItemActivity(BaseModel):
    """WebSearch Item Activity - AI-generated daily websearch activities"""
    __tablename__ = "websearch_item_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=False)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    websearchdetails_id = Column(String, ForeignKey("websearch_details.id"), nullable=False)
    status = Column(String, nullable=False)  # 'pending', 'completed', 'failed'
    reaction = Column(Text, nullable=True)  # User reaction to search results
    summary = Column(Text, nullable=True)  # AI-generated summary
    source_json = Column(JSON, nullable=True)  # Source data as JSON
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="websearch_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    websearch_details = relationship("WebSearchDetails", back_populates="websearch_activities") 