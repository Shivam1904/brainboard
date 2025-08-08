"""
Daily Widget model - Daily widget instances.
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Date
from .base import BaseModel

class DailyWidget(BaseModel):
    """Daily Widget - AI-generated daily widget selections"""
    __tablename__ = "daily_widgets"
    
    widget_id = Column(String, nullable=False)  # Foreign key to dashboard_widget_details
    priority = Column(String, nullable=False)  # 'HIGH', 'LOW'
    reasoning = Column(Text, nullable=True)  # AI reasoning for selection
    date = Column(Date, nullable=False)  # Date when this widget should be shown
    is_active = Column(Boolean, default=True)  # Indicates if the widget is active
    
    # Consolidated activity fields (JSON)
    activity_data = Column(JSON, nullable=False)  # Contains all activity-specific data
    
    def get_alarm_activity(self):
        """Get alarm activity data from activity_data"""
        if self.activity_data:
            return self.activity_data.get('alarm_activity', {})
        return {}
    
    def get_todo_activity(self):
        """Get todo activity data from activity_data"""
        if self.activity_data:
            return self.activity_data.get('todo_activity', {})
        return {}
    
    def get_tracker_activity(self):
        """Get single item tracker activity data from activity_data"""
        if self.activity_data:
            return self.activity_data.get('tracker_activity', {})
        return {}
    
    def get_websearch_activity(self):
        """Get websearch activity data from activity_data"""
        if self.activity_data:
            return self.activity_data.get('websearch_activity', {})
        return {}
    
    def update_activity_data(self, activity_type, activity_data):
        """Update specific activity data"""
        if not self.activity_data:
            self.activity_data = {}
        
        if activity_type == 'alarm':
            self.activity_data['alarm_activity'] = activity_data
        elif activity_type == 'todo':
            self.activity_data['todo_activity'] = activity_data
        elif activity_type == 'single_item_tracker':
            self.activity_data['tracker_activity'] = activity_data
        elif activity_type == 'websearch':
            self.activity_data['websearch_activity'] = activity_data 