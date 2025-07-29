from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class ToDoDetails(Base):
    """ToDo Details - User input table for todo configurations"""
    __tablename__ = "todo_details"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    todo_type = Column(String, nullable=False)  # 'task', 'habit'
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    
    # Audit columns
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
    delete_flag = Column(Boolean, default=False)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="todo_details")
    todo_activities = relationship("ToDoItemActivity", back_populates="todo_details", cascade="all, delete-orphan") 