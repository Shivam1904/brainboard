from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class SingleItemTracker(Base):
    """Single Item Tracker database model - for tracking metrics like weight, pages read, etc."""
    __tablename__ = "single_item_trackers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    item_name = Column(String, nullable=False)  # e.g., "Weight", "Pages Read", "Steps"
    item_unit = Column(String, nullable=True)   # e.g., "kg", "pages", "steps"
    current_value = Column(String, nullable=True)  # Current value as string to support various formats
    target_value = Column(String, nullable=True)   # Optional target value
    value_type = Column(String, default="number")  # "number", "text", "decimal"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="single_item_trackers")
    tracker_logs = relationship("SingleItemTrackerLog", back_populates="tracker", cascade="all, delete-orphan")

class SingleItemTrackerLog(Base):
    """Single Item Tracker Log database model - for tracking value history"""
    __tablename__ = "single_item_tracker_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tracker_id = Column(String, ForeignKey("single_item_trackers.id"), nullable=False)
    value = Column(String, nullable=False)  # Value as string
    date = Column(Date, nullable=False, default=lambda: datetime.utcnow().date())
    notes = Column(Text, nullable=True)  # Optional notes for the entry
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    tracker = relationship("SingleItemTracker", back_populates="tracker_logs")
