from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Integer, Date
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, date
import uuid

# ============================================================================
# USER MODEL
# ============================================================================

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with dashboard widgets
    dashboard_widgets = relationship("DashboardWidget", back_populates="user", cascade="all, delete-orphan")

# ============================================================================
# DASHBOARD WIDGET MODELS (Enhanced from existing Widget)
# ============================================================================

class DashboardWidget(Base):
    """Dashboard Widget configuration model (enhanced from existing Widget)"""
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
    last_shown_date = Column(Date, nullable=True)  # Track when last shown for AI
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")
    todo_tasks = relationship("TodoTask", back_populates="dashboard_widget", cascade="all, delete-orphan")
    websearch_queries = relationship("WebSearchQuery", back_populates="dashboard_widget", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="dashboard_widget", cascade="all, delete-orphan")
    alarms = relationship("Alarm", back_populates="dashboard_widget", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="dashboard_widget", cascade="all, delete-orphan")

# ============================================================================
# LEGACY MODEL (Keep for backward compatibility during migration)
# ============================================================================

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Integer, Date
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
import uuid

# ============================================================================
# CORE MODELS
# ============================================================================

class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widgets = relationship("DashboardWidget", back_populates="user", cascade="all, delete-orphan")

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
    last_shown_date = Column(Date, nullable=True)  # Track when last shown
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")
    summaries = relationship("Summary", back_populates="dashboard_widget", cascade="all, delete-orphan")
    todo_tasks = relationship("TodoTask", back_populates="dashboard_widget", cascade="all, delete-orphan")
    websearch_queries = relationship("WebSearchQuery", back_populates="dashboard_widget", cascade="all, delete-orphan")
    alarms = relationship("Alarm", back_populates="dashboard_widget", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="dashboard_widget", cascade="all, delete-orphan")

# ============================================================================
# LEGACY MODELS (for backward compatibility during migration)
# ============================================================================

class Widget(Base):
    """Legacy Widget database model - will be deprecated"""
    __tablename__ = "widgets"
    
    widget_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, default="default_user")
    widget_type = Column(String, nullable=False)  # e.g., "web-summary"
    current_query = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)  # JSON field for widget settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with summaries (legacy)
    summaries = relationship("Summary", foreign_keys="Summary.widget_id", cascade="all, delete-orphan")

# ============================================================================
# WIDGET-SPECIFIC DATA MODELS
# ============================================================================

class TodoTask(Base):
    """Todo Task database model"""
    __tablename__ = "todo_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    content = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="todo_tasks")

class WebSearchQuery(Base):
    """Web Search Query database model"""
    __tablename__ = "websearch_queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    search_term = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="websearch_queries")

class Alarm(Base):
    """Alarm database model"""
    __tablename__ = "alarms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    next_trigger_time = Column(DateTime, nullable=True)
    is_snoozed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="alarms")

class Habit(Base):
    """Habit database model"""
    __tablename__ = "habits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dashboard_widget = relationship("DashboardWidget", back_populates="habits")
    habit_logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    """Habit Log database model"""
    __tablename__ = "habit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # 'completed', 'missed', 'partial'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    habit = relationship("Habit", back_populates="habit_logs")

# ============================================================================
# ENHANCED SUMMARY MODEL (supports both legacy and new system)
# ============================================================================

class Summary(Base):
    """Enhanced Summary database model - supports both legacy and new system"""
    __tablename__ = "summaries"
    
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # Support both legacy and new system during migration
    widget_id = Column(String, ForeignKey("widgets.widget_id"), nullable=True)  # Legacy FK
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=True)  # New FK
    query = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)  # Store list of source URLs as JSON
    search_results_json = Column(JSON, nullable=True)  # NEW: Store full search results for widgets
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (support both systems)
    widget = relationship("Widget", foreign_keys=[widget_id])  # Legacy
    dashboard_widget = relationship("DashboardWidget", back_populates="summaries")  # New
    widget = relationship("Widget", foreign_keys=[widget_id])  # Legacy
    dashboard_widget = relationship("DashboardWidget", back_populates="summaries")  # New
