from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widgets = relationship("DashboardWidget", back_populates="user", cascade="all, delete-orphan")
    daily_widgets = relationship("DailyWidget", cascade="all, delete-orphan")
