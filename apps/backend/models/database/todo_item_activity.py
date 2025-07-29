from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class ToDoItemActivity(Base):
    """ToDo Item Activity - AI-generated daily todo activities"""
    __tablename__ = "todo_item_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=False)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    tododetails_id = Column(String, ForeignKey("todo_details.id"), nullable=False)
    status = Column(String, nullable=False)  # 'in progress', 'completed', 'pending'
    progress = Column(Integer, nullable=True)  # Progress percentage: 32
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="todo_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    todo_details = relationship("ToDoDetails", back_populates="todo_activities") 