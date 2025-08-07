"""
Dashboard Widget Details model - User input table for widget configurations.
"""
from sqlalchemy import Column, String, Boolean, Float, JSON, Text
from .base import BaseModel

class DashboardWidgetDetails(BaseModel):
    """Dashboard Widget Details - User input table for widget configurations"""
    __tablename__ = "dashboard_widget_details"
    
    user_id = Column(String, nullable=False)
    widget_type = Column(String, nullable=False)  # 'alarm', 'todo', 'single_item_tracker', 'websearch'
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    frequency_details = Column(JSON, nullable=True)  # Contains all frequency specific configuration
    importance = Column(Float, nullable=False)  # 0.0 to 1.0 scale
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # 'Job', 'Health', 'Productivity', etc.
    is_permanent = Column(Boolean, default=False)  # If True, widget is automatically included in daily plans
    
    # Consolidated details fields (JSON)
    widget_config = Column(JSON, nullable=False)  # Contains all widget-specific configuration
    
    def get_alarm_config(self):
        """Get alarm-specific configuration from widget_config"""
        if self.widget_type == 'alarm' and self.widget_config:
            return self.widget_config
        return {}
    
    def get_todo_config(self):
        """Get todo-specific configuration from widget_config"""
        if self.widget_type == 'todo' and self.widget_config:
            return self.widget_config
        return {}
    
    def get_tracker_config(self):
        """Get single item tracker-specific configuration from widget_config"""
        if self.widget_type == 'single_item_tracker' and self.widget_config:
            return self.widget_config
        return {}
    
    def get_websearch_config(self):
        """Get websearch-specific configuration from widget_config"""
        if self.widget_type == 'websearch' and self.widget_config:
            return self.widget_config
        return {}
    
    def update_widget_config(self, config_data):
        """Update specific widget configuration"""
        if not self.widget_config:
            self.widget_config = {}
        else:
            self.widget_config = config_data 