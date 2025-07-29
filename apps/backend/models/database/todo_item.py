from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class TodoItem(Base):
    """
    Todo Item database model - Supports Task, Event, and Habit types
    Types:
    - Task: A one-time action item you need to complete
    - Event: A scheduled, time-bound activity  
    - Habit: A recurring activity you want to build into your routine
    """
    __tablename__ = "todo_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    # Core fields
    title = Column(String, nullable=False)
    item_type = Column(String, nullable=False)  # 'task', 'event', 'habit'
    category = Column(String, nullable=True)  # 'work', 'personal', 'health', etc.
    priority = Column(String, nullable=False, default='medium')  # 'low', 'medium', 'high'
    # Frequency and scheduling
    frequency = Column(String, nullable=True)  # 'daily', 'weekly-2', 'daily-8', etc.
    frequency_times = Column(JSON, nullable=True)  # For habits: ['7am'], ['every 2 hr']
    # Status and completion
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    # Dates
    due_date = Column(Date, nullable=True)  # For tasks and events
    scheduled_time = Column(DateTime, nullable=True)  # For events
    last_completed_date = Column(Date, nullable=True)  # For habits
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="todo_items")
