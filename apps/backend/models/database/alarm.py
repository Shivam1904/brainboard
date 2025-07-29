from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class Alarm(Base):
    """Alarm database model"""
    __tablename__ = "alarms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    title = Column(String, nullable=False)  # e.g., "Yogi Bday", "Sit Straight"
    alarm_type = Column(String, nullable=False)  # "once", "daily", "weekly", "monthly", "yearly"
    alarm_times = Column(JSON, nullable=False)  # List of times: ["09:00", "15:00"] or ["09:00"] 
    frequency_value = Column(Integer, nullable=True)  # For daily-5, weekly-2, etc. (interval)
    specific_date = Column(Date, nullable=True)  # For one-time alarms like "Jun 20"
    is_active = Column(Boolean, default=True)
    is_snoozed = Column(Boolean, default=False)
    snooze_until = Column(DateTime, nullable=True)
    last_triggered = Column(DateTime, nullable=True)
    next_trigger_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="alarms")
