from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class AlarmItemActivity(Base):
    """Alarm Item Activity - AI-generated daily alarm activities"""
    __tablename__ = "alarm_item_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=False)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    alarmdetails_id = Column(String, ForeignKey("alarm_details.id"), nullable=False)
    started_at = Column(DateTime, nullable=True)  # When alarm was started
    snoozed_at = Column(DateTime, nullable=True)  # When alarm was snoozed
    snooze_until = Column(DateTime, nullable=True)  # When snooze expires
    snooze_count = Column(Integer, default=0)  # Number of times snoozed today
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="alarm_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    alarm_details = relationship("AlarmDetails", back_populates="alarm_activities") 