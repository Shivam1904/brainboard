from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class SingleItemTrackerItemActivity(Base):
    """Single Item Tracker Item Activity - AI-generated daily tracker activities"""
    __tablename__ = "single_item_tracker_item_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=False)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    singleitemtrackerdetails_id = Column(String, ForeignKey("single_item_tracker_details.id"), nullable=False)
    value = Column(String, nullable=True)  # Current value
    time_added = Column(DateTime, nullable=True)  # When value was added
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="single_item_tracker_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    tracker_details = relationship("SingleItemTrackerDetails", back_populates="tracker_activities") 