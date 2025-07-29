from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Float, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class DashboardWidgetDetails(Base):
    """Dashboard Widget Details - User input table for widget configurations"""
    __tablename__ = "dashboard_widget_details"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    widget_type = Column(String, nullable=False)  # 'todo-habit', 'todo-task', 'todo-event', 'alarm', 'singleitemtracker', 'websearch'
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    importance = Column(Float, nullable=False)  # 0.0 to 1.0 scale
    title = Column(String, nullable=False)  # Redundant but kept for convenience
    category = Column(String, nullable=True)  # 'Job', 'Health', 'Productivity', etc.
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")
    todo_details = relationship("ToDoDetails", back_populates="dashboard_widget", cascade="all, delete-orphan")
    single_item_tracker_details = relationship("SingleItemTrackerDetails", back_populates="dashboard_widget", cascade="all, delete-orphan")
    websearch_details = relationship("WebSearchDetails", back_populates="dashboard_widget", cascade="all, delete-orphan")
    alarm_details = relationship("AlarmDetails", back_populates="dashboard_widget", cascade="all, delete-orphan") 