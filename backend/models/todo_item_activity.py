"""
TODO Item Activity model - AI-generated daily todo activities.
"""
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class TodoItemActivity(BaseModel):
    """TODO Item Activity - AI-generated daily todo activities"""
    __tablename__ = "todo_item_activities"
    
    daily_widget_id = Column(String, ForeignKey("daily_widgets.id"), nullable=False)
    widget_id = Column(String, ForeignKey("dashboard_widget_details.id"), nullable=False)
    tododetails_id = Column(String, ForeignKey("todo_details.id"), nullable=False)
    status = Column(String, nullable=False)  # 'in progress', 'completed', 'pending'
    progress = Column(Integer, nullable=True)  # Progress percentage
    
    # Relationships
    daily_widget = relationship("DailyWidget", back_populates="todo_activities")
    dashboard_widget = relationship("DashboardWidgetDetails")
    todo_details = relationship("TodoDetails", back_populates="todo_activities") 