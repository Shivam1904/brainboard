"""
Alarm Item Activity model - Daily alarm activities.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class AlarmItemActivity(BaseModel):
    """Alarm Item Activity - Daily alarm activities"""
    __tablename__ = "alarm_item_activities"
    
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=True)  # Add this field
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    alarmdetails_id = Column(String, ForeignKey("alarm_details.id"), nullable=False)
    started_at = Column(DateTime, nullable=True)  # When alarm was started
    snoozed_at = Column(DateTime, nullable=True)  # When alarm was snoozed
    snooze_until = Column(DateTime, nullable=True)  # When snooze expires
    snooze_count = Column(Integer, default=0)  # Number of times snoozed today
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="alarm_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    alarm_details = relationship("AlarmDetails", back_populates="alarm_activities") 