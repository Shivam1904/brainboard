from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class SingleItemTrackerDetails(Base):
    """Single Item Tracker Details - User input table for tracker configurations"""
    __tablename__ = "single_item_tracker_details"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    value_type = Column(String, nullable=False)  # 'number', 'text', 'decimal'
    value_unit = Column(String, nullable=True)  # 'kg', 'pages', 'steps'
    target_value = Column(String, nullable=True)  # Target value as string
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="single_item_tracker_details")
    tracker_activities = relationship("SingleItemTrackerItemActivity", back_populates="tracker_details", cascade="all, delete-orphan") 