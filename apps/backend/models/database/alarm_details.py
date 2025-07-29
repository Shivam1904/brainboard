from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class AlarmDetails(Base):
    """Alarm Details - User input table for alarm configurations"""
    __tablename__ = "alarm_details"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    alarm_times = Column(JSON, nullable=False)  # Array of times: ["09:00", "15:00"]
    target_value = Column(String, nullable=True)  # Optional target value
    is_snoozable = Column(Boolean, default=True)
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="alarm_details")
    alarm_activities = relationship("AlarmItemActivity", back_populates="alarm_details", cascade="all, delete-orphan") 