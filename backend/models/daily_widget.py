"""
Daily Widget model - Daily widget instances.
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Date
from sqlalchemy.orm import relationship
from .base import BaseModel

class DailyWidget(BaseModel):
    """Daily Widget - AI-generated daily widget selections"""
    __tablename__ = "daily_widgets"
    
    widget_ids = Column(JSON, nullable=False)  # Array of widget IDs: ["id0", "id1", "id2", "id3"]
    widget_type = Column(String, nullable=False)  # 'todo-habit', 'todo-task', 'todo-event', 'alarm', 'singleitemtracker', 'websearch'
    priority = Column(String, nullable=False)  # 'HIGH', 'LOW'
    reasoning = Column(Text, nullable=True)  # AI reasoning for selection
    date = Column(Date, nullable=False)  # Date when this widget should be shown
    is_active = Column(Boolean, default=True)  # Indicates if the widget is active
    
    # Relationships
    alarm_activities = relationship("AlarmItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    todo_activities = relationship("TodoItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    single_item_tracker_activities = relationship("SingleItemTrackerItemActivity", back_populates="daily_widget", cascade="all, delete-orphan") 