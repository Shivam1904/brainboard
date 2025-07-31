"""
SingleItemTracker Item Activity model - Daily tracker activities.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class SingleItemTrackerItemActivity(BaseModel):
    """SingleItemTracker Item Activity - Daily tracker activities"""
    __tablename__ = "single_item_tracker_item_activities"
    
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=True)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    singleitemtrackerdetails_id = Column(String, ForeignKey("single_item_tracker_details.id"), nullable=False)
    value = Column(String, nullable=True)  # Current value
    time_added = Column(DateTime, nullable=True)  # When value was added
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="single_item_tracker_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    tracker_details = relationship("SingleItemTrackerDetails", back_populates="tracker_activities") 