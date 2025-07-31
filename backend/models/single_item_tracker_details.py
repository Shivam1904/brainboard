"""
SingleItemTracker Details model - User input table for tracker configurations.
"""
from sqlalchemy import Column, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class SingleItemTrackerDetails(BaseModel):
    """SingleItemTracker Details - User input table for tracker configurations"""
    __tablename__ = "single_item_tracker_details"
    
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    value_type = Column(String, nullable=False)  # 'number', 'text', 'decimal'
    value_unit = Column(String, nullable=True)  # 'kg', 'pages', 'steps'
    target_value = Column(String, nullable=True)  # Target value as string
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="single_item_tracker_details")
    tracker_activities = relationship("SingleItemTrackerItemActivity", back_populates="tracker_details", cascade="all, delete-orphan") 