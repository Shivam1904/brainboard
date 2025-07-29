from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class Summary(Base):
    """Enhanced Summary database model - supports both legacy and new system"""
    __tablename__ = "summaries"
    
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=True)
    query = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)
    search_results_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    dashboard_widget = relationship("DashboardWidget", back_populates="summaries")
