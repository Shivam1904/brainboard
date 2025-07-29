from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean, Integer, Date, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class DailyWidget(Base):
    """Daily Widget database model - AI-generated daily widget selections"""
    __tablename__ = "daily_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    display_date = Column(Date, nullable=False)  # Date when this widget should be shown
    position = Column(Integer, nullable=False)  # Display order on dashboard
    grid_position = Column(JSON, nullable=True)  # Grid layout: {"x": 0, "y": 0, "width": 2, "height": 1}
    ai_reasoning = Column(Text, nullable=True)  # Why AI selected this widget for today
    is_pinned = Column(Boolean, default=False)  # User manually pinned this widget for today
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", overlaps="daily_widgets")
    dashboard_widget = relationship("DashboardWidget")
