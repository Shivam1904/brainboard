from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class Widget(Base):
    """Widget database model"""
    __tablename__ = "widgets"
    
    widget_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default_user")
    widget_type = Column(String, nullable=False)  # e.g., "web-summary"
    current_query = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)  # JSON field for widget settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with summaries
    summaries = relationship("Summary", back_populates="widget", cascade="all, delete-orphan")

class Summary(Base):
    """Summary database model"""
    __tablename__ = "summaries"
    
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("widgets.widget_id"), nullable=False)
    query = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)  # Store list of source URLs as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with widget
    widget = relationship("Widget", back_populates="summaries")
