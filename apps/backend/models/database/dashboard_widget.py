from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Date
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class DashboardWidget(Base):
    """Dashboard Widget database model (master widget configurations)"""
    __tablename__ = "dashboard_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    widget_type = Column(String, nullable=False)  # 'todo', 'websearch', 'alarm', 'calendar', 'habittracker'
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    category = Column(String, nullable=True)
    importance = Column(Integer, nullable=True)  # 1-5 scale
    settings = Column(JSON, nullable=True)  # Widget-specific settings
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)  # User can hide/show widgets
    grid_size = Column(JSON, nullable=True)  # Grid layout: {"width": 2, "height": 1}
    last_shown_date = Column(Date, nullable=True)  # Track when last shown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")
    summaries = relationship("Summary", back_populates="dashboard_widget", cascade="all, delete-orphan")
    todo_items = relationship("TodoItem", back_populates="dashboard_widget", cascade="all, delete-orphan")
    websearch_queries = relationship("WebSearchQuery", back_populates="dashboard_widget", cascade="all, delete-orphan")
    alarms = relationship("Alarm", back_populates="dashboard_widget", cascade="all, delete-orphan")
    single_item_trackers = relationship("SingleItemTracker", back_populates="dashboard_widget", cascade="all, delete-orphan")
