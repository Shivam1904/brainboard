"""
TODO Details model - User input table for todo configurations.
"""
from sqlalchemy import Column, String, ForeignKey, Boolean, Date, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class TodoDetails(BaseModel):
    """TODO Details - User input table for todo configurations"""
    __tablename__ = "todo_details"
    
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    title = Column(String, nullable=False)
    todo_type = Column(String, nullable=False)  # 'task' or 'habit'
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidgetDetails", back_populates="todo_details")
    todo_activities = relationship("TodoItemActivity", back_populates="todo_details", cascade="all, delete-orphan") 