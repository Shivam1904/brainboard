from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class DailyWidget(Base):
    """Daily Widget - AI-generated daily widget selections"""
    __tablename__ = "daily_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_ids = Column(JSON, nullable=False)  # Array of widget IDs: ["id0", "id1", "id2", "id3"]
    widget_type = Column(String, nullable=False)  # 'todo', 'alarm', 'singleitemtracker', 'websearch'
    priority = Column(String, nullable=False)  # 'HIGH', 'LOW'
    reasoning = Column(Text, nullable=True)  # AI reasoning for selection
    date = Column(Date, nullable=False)  # Date when this widget should be shown
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    todo_activities = relationship("ToDoItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    single_item_tracker_activities = relationship("SingleItemTrackerItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    alarm_activities = relationship("AlarmItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
    websearch_activities = relationship("WebSearchItemActivity", back_populates="daily_widget", cascade="all, delete-orphan")
