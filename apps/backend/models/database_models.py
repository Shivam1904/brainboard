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
    todo_items = relationship("TodoItem", back_populates="dashboard_widget", cascade="all, delete-orphan")
    todo_tasks = relationship("TodoTask", back_populates="dashboard_widget", cascade="all, delete-orphan")  # Legacy
    websearch_queries = relationship("WebSearchQuery", back_populates="dashboard_widget", cascade="all, delete-orphan")
    alarms = relationship("Alarm", back_populates="dashboard_widget", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="dashboard_widget", cascade="all, delete-orphan")
    single_item_trackers = relationship("SingleItemTracker", back_populates="dashboard_widget", cascade="all, delete-orphan")

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

# Keep the old TodoTask model for backward compatibility during migration
class TodoTask(Base):
    """DEPRECATED: Todo Task database model - Use TodoItem instead"""
    __tablename__ = "todo_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_widget_id = Column(String, ForeignKey("dashboard_widgets.id"), nullable=False)
    content = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    frequency = Column(String, nullable=False, default="daily")  # 'daily', 'weekly', 'monthly', 'once'
    priority = Column(Integer, nullable=True, default=3)  # 1-5 scale (1=low, 5=high)
    category = Column(String, nullable=True)  # 'work', 'personal', 'health', etc.
    is_done = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=True)  # Whether task repeats
    last_completed_date = Column(Date, nullable=True)  # Track completion for recurring tasks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    title = Column(String, nullable=False)  # e.g., "Yogi Bday", "Sit Straight"
    alarm_type = Column(String, nullable=False)  # "once", "daily", "weekly", "monthly", "yearly"
    alarm_times = Column(JSON, nullable=False)  # List of times: ["09:00", "15:00"] or ["09:00"] 
    frequency_value = Column(Integer, nullable=True)  # For daily-5, weekly-2, etc. (interval)
    specific_date = Column(Date, nullable=True)  # For one-time alarms like "Jun 20"
    is_active = Column(Boolean, default=True)
    is_snoozed = Column(Boolean, default=False)
    snooze_until = Column(DateTime, nullable=True)
    last_triggered = Column(DateTime, nullable=True)
    next_trigger_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
# SINGLE ITEM TRACKER MODEL
# ============================================================================

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
