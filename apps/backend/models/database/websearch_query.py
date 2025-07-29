from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class WebSearchQuery(Base):
    """Web Search Query database model"""
    __tablename__ = "websearch_queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    search_term = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="websearch_queries")
