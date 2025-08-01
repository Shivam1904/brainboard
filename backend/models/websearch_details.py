"""
WebSearch details model for web search configurations.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import BaseModel

# ============================================================================
# MODEL
# ============================================================================
class WebSearchDetails(BaseModel):
    """WebSearch Details - User input table for web search configurations"""
    __tablename__ = "websearch_details"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="websearch_details")
    websearch_activities = relationship("WebSearchItemActivity", back_populates="websearch_details", cascade="all, delete-orphan") 