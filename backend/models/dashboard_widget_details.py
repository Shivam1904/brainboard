"""
Dashboard Widget Details model - User input table for widget configurations.
"""
from sqlalchemy import Column, String, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class DashboardWidgetDetails(BaseModel):
    """Dashboard Widget Details - User input table for widget configurations"""
    __tablename__ = "dashboard_widget_details"
    
    user_id = Column(String, nullable=False)  # Simplified for now
    widget_type = Column(String, nullable=False)  # 'alarm'
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    importance = Column(Float, nullable=False)  # 0.0 to 1.0 scale
    title = Column(String, nullable=False)  # Redundant but kept for convenience
    category = Column(String, nullable=True)  # 'Job', 'Health', 'Productivity', etc.
    is_permanent = Column(Boolean, default=False)  # If True, widget is automatically included in daily plans
    
    # Relationships
    alarm_details = relationship("AlarmDetails", back_populates="dashboard_widget", cascade="all, delete-orphan")
    single_item_tracker_details = relationship("SingleItemTrackerDetails", back_populates="dashboard_widget", cascade="all, delete-orphan")
    todo_details = relationship("TodoDetails", back_populates="dashboard_widget", cascade="all, delete-orphan") 