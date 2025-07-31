"""
Alarm Details model - User input table for alarm configurations.
"""
from sqlalchemy import Column, String, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class AlarmDetails(BaseModel):
    """Alarm Details - User input table for alarm configurations"""
    __tablename__ = "alarm_details"
    
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    alarm_times = Column(JSON, nullable=False)  # Array of times: ["09:00", "15:00"]
    target_value = Column(String, nullable=True)  # Optional target value
    is_snoozable = Column(Boolean, default=True)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="alarm_details")
    alarm_activities = relationship("AlarmItemActivity", back_populates="alarm_details", cascade="all, delete-orphan") 