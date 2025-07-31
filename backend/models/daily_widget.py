"""
Daily Widget model - Daily widget selections.
"""
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Date, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
import uuid

class DailyWidget(BaseModel):
    """Daily Widget - Daily widget selections"""
    __tablename__ = "daily_widgets"
    
    widget_ids = Column(JSON, nullable=False)  # Array of widget IDs: ["id0", "id1", "id2", "id3"]
    widget_type = Column(String, nullable=False)  # 'alarm'
    priority = Column(String, nullable=False)  # 'HIGH', 'MEDIUM', 'LOW'
    reasoning = Column(Text, nullable=True)  # Manual reasoning or AI reasoning
    date = Column(Date, nullable=False)  # Date when this widget should be shown
    is_active = Column(Boolean, default=True)  # Indicates if the widget is active
    
    # Relationships
    alarm_activities = relationship("AlarmItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    todo_activities = relationship("TodoItemActivity", back_populates="daily_widget", cascade="all, delete-orphan") 