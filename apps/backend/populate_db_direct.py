#!/usr/bin/env python3
"""
🗄️ AI Dashboard System - Direct Database Population Script
Directly inserts realistic test data into SQLite database using SQL/ORM

This script bypasses the API and directly populates the database tables with:
- Dashboard Widgets (WebSearch, Todo, SingleItemTracker, Alarm)
- Daily Widget Selections (AI-curated daily dashboard layouts)
- WebSearch Queries and AI Summaries  
- Todo Items (Tasks, Events, Habits)
- SingleItemTracker instances and historical entries
- Alarm configurations with various types
- Realistic relationships and data variety

Usage:
    python populate_db_direct.py
"""

import os
import sys
import json
import uuid
import random
import traceback
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db, engine, SessionLocal
from core.config import settings
from models.database import (
    User, DashboardWidget, DailyWidget, Summary,
    TodoItem, WebSearchQuery, 
    Alarm,
    SingleItemTracker, SingleItemTrackerLog
)

class DirectDatabasePopulator:
    def __init__(self):
        self.session = SessionLocal()
        self.created_data = {
            "users": [],
            "dashboard_widgets": [],
            "daily_widgets": [],
            "websearch_queries": [],
            "summaries": [],
            "todo_items": [],
            "tracker_instances": [],
            "tracker_logs": [],
            "alarms": []
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "SECTION": "📋"}
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '📝')} {message}")
    
    def section_header(self, title: str, emoji: str = "📋"):
        """Print organized section headers"""
        print("\n" + "=" * 70)
        print(f"{emoji} {title}")
        print("=" * 70)
    
    def cleanup_existing_data(self):
        """Clean up existing test data to start fresh"""
        self.section_header("Cleaning Existing Data", "🧹")
        
        try:
            # Delete in reverse dependency order
            # Check which tables exist first
            with self.session.bind.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                existing_tables = [row[0] for row in result.fetchall()]
            
            # Only delete from tables that exist
            tables_to_clean = [
                "daily_widgets",
                "alarms",
                "single_item_tracker_logs",
                "single_item_trackers",
                "todo_items",
                "summaries",
                "websearch_queries",
                "dashboard_widgets"
                # Don't delete users - they might be needed for auth
            ]
            
            for table in tables_to_clean:
                if table in existing_tables:
                    self.session.execute(text(f"DELETE FROM {table}"))
                    self.log(f"Cleaned table: {table}", "SUCCESS")
                else:
                    self.log(f"Table {table} doesn't exist, skipping", "INFO")
            
            self.session.commit()
            self.log("Existing test data cleaned successfully", "SUCCESS")
            
        except Exception as e:
            self.log(f"Error cleaning existing data: {e}", "ERROR")
            self.session.rollback()
            raise
    
    def create_default_user(self):
        """Create default user for testing"""
        self.section_header("Creating Default User", "👤")
        
        try:
            # Check if default user already exists
            existing_user = self.session.query(User).filter(
                User.email == "default@brainboard.com"
            ).first()
            
            if existing_user:
                self.log("Default user already exists", "INFO")
                self.created_data["users"].append(existing_user)
                return existing_user
            
            # Create new default user
            user = User(
                id=str(uuid.uuid4()),
                email="default@brainboard.com",
                name="Brainboard Default User",
                created_at=datetime.utcnow()
            )
            
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            
            self.created_data["users"].append(user)
            self.log(f"Created default user: {user.name} (ID: {user.id})", "SUCCESS")
            return user
            
        except Exception as e:
            self.log(f"Error creating default user: {e}", "ERROR")
            self.session.rollback()
            raise
    
    def create_dashboard_widgets(self):
        """Create a simple set of dashboard widgets for testing"""
        self.section_header("Creating Dashboard Widgets", "📊")
        
        user = self.created_data["users"][0]
        
        # Simple, realistic widget configurations
        widget_configs = [
            # 2 Todo Widgets
            {"title": "Daily Tasks", "widget_type": "todo", "category": "productivity", "importance": 5, "frequency": "daily"},
            {"title": "Health Goals", "widget_type": "todo", "category": "health", "importance": 4, "frequency": "daily"},
            
            # 2 WebSearch Widgets  
            {"title": "Tech News", "widget_type": "websearch", "category": "technology", "importance": 4, "frequency": "daily"},
            {"title": "Health Tips", "widget_type": "websearch", "category": "health", "importance": 3, "frequency": "weekly"},
            
            # 2 Tracker Widgets
            {"title": "Step Counter", "widget_type": "singleitemtracker", "category": "health", "importance": 4, "frequency": "daily"},
            {"title": "Water Intake", "widget_type": "singleitemtracker", "category": "health", "importance": 3, "frequency": "daily"},
            
            # 2 Alarm Widgets
            {"title": "Morning Routine", "widget_type": "alarm", "category": "reminders", "importance": 5, "frequency": "daily"},
            {"title": "Work Schedule", "widget_type": "alarm", "category": "work", "importance": 4, "frequency": "weekly"},
        ]
        
        created_widgets = []
        
        for config in widget_configs:
            try:
                widget = DashboardWidget(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    title=config["title"],
                    widget_type=config["widget_type"],
                    category=config["category"],
                    importance=config["importance"],
                    frequency=config["frequency"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.session.add(widget)
                created_widgets.append(widget)
                
                self.log(f"✓ Created {config['widget_type']} widget: {config['title']}", "SUCCESS")
                
            except Exception as e:
                self.log(f"✗ Failed to create widget {config['title']}: {e}", "ERROR")
        
        self.session.commit()
        
        # Refresh all widgets to get IDs
        for widget in created_widgets:
            self.session.refresh(widget)
            self.created_data["dashboard_widgets"].append(widget)
        
        self.log(f"Created {len(created_widgets)} dashboard widgets", "SUCCESS")
        return created_widgets
    
    def create_websearch_data(self):
        """Create WebSearch queries and AI summaries"""
        self.section_header("Creating WebSearch Data", "🌐")
        
        websearch_widgets = [w for w in self.created_data["dashboard_widgets"] if w.widget_type == "websearch"]
        
        if not websearch_widgets:
            self.log("No websearch widgets found, skipping websearch data creation", "WARNING")
            return
        
        search_terms = {
            "Tech News": "latest technology trends and software development news",
            "Health Tips": "nutrition wellness fitness tips and health advice"
        }
        
        for widget in websearch_widgets:
            try:
                # Validate widget exists and is correct type
                if not widget.id or widget.widget_type != "websearch":
                    self.log(f"Invalid widget for websearch: {widget.title}", "ERROR")
                    continue
                
                # Create WebSearchQuery
                search_term = search_terms.get(widget.title, f"search for {widget.title}")
                
                query = WebSearchQuery(
                    id=str(uuid.uuid4()),
                    dashboard_widget_id=widget.id,
                    search_term=search_term,
                    created_at=datetime.utcnow()
                )
                
                self.session.add(query)
                self.session.commit()
                self.session.refresh(query)
                
                self.created_data["websearch_queries"].append(query)
                
                # Create AI Summary
                summary_content = f"""# {widget.title} Summary

## Key Findings
Based on the latest research and developments in {widget.title.lower()}, here are the most important insights:

### Main Points
1. **Emerging Trends**: The field is rapidly evolving with new innovations appearing regularly
2. **Best Practices**: Industry leaders recommend following established methodologies
3. **Future Outlook**: Continued growth and development expected in the coming months

### Actionable Recommendations
- Stay updated with the latest developments
- Follow industry experts and thought leaders  
- Implement best practices in your daily workflow
- Monitor progress and adjust strategies as needed

### Resources
- Industry publications and journals
- Expert blogs and newsletters
- Professional development courses
- Community forums and discussions

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                
                summary = Summary(
                    summary_id=str(uuid.uuid4()),
                    dashboard_widget_id=query.dashboard_widget_id,
                    query=f"Summarize latest developments in {widget.title}",
                    summary_text=summary_content,
                    created_at=datetime.utcnow()
                )
                
                self.session.add(summary)
                self.created_data["summaries"].append(summary)
                
                self.log(f"✓ Created WebSearch data for: {widget.title}", "SUCCESS")
                
            except Exception as e:
                self.log(f"✗ Failed to create WebSearch data for {widget.title}: {e}", "ERROR")
                self.session.rollback()
        
        self.session.commit()
        self.log(f"Created WebSearch data for {len(websearch_widgets)} widgets", "SUCCESS")
    
    def create_todo_data(self):
        """Create comprehensive Todo items (Tasks, Events, Habits)"""
        self.section_header("Creating Todo Data", "📝")
        
        todo_widgets = [w for w in self.created_data["dashboard_widgets"] if w.widget_type == "todo"]
        
        # Define todo item templates by category
        todo_templates = {
            "productivity": [
                {"title": "Complete quarterly review", "item_type": "task", "priority": "high", "frequency": "once", "category": "work", "due_date": date(2025, 8, 15)},
                {"title": "Update project documentation", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "work"},
                {"title": "Morning planning session", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["8:00am"], "category": "routine"},
                {"title": "Focus time block", "item_type": "habit", "priority": "high", "frequency": "daily-2", "frequency_times": ["10am", "2pm"], "category": "work"},
                {"title": "Team standup meeting", "item_type": "event", "priority": "high", "frequency": "daily", "scheduled_time": datetime(2025, 7, 29, 9, 0), "category": "meetings"},
                {"title": "Client presentation", "item_type": "event", "priority": "high", "frequency": "once", "scheduled_time": datetime(2025, 8, 5, 14, 0), "category": "work"},
            ],
            "health": [
                {"title": "Schedule doctor checkup", "item_type": "task", "priority": "medium", "frequency": "once", "category": "medical", "due_date": date(2025, 8, 30)},
                {"title": "Meal prep for the week", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "nutrition"},
                {"title": "Morning workout", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["7am"], "category": "exercise"},
                {"title": "Drink water", "item_type": "habit", "priority": "high", "frequency": "daily-8", "frequency_times": ["every 2 hours"], "category": "hydration"},
                {"title": "Take vitamins", "item_type": "habit", "priority": "medium", "frequency": "daily", "frequency_times": ["8am"], "category": "supplements"},
                {"title": "Yoga class", "item_type": "event", "priority": "medium", "frequency": "weekly-2", "scheduled_time": datetime(2025, 7, 30, 18, 0), "category": "exercise"},
            ],
            "work": [
                {"title": "Prepare monthly report", "item_type": "task", "priority": "high", "frequency": "monthly", "category": "reporting", "due_date": date(2025, 8, 31)},
                {"title": "Review team performance", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "management"},
                {"title": "Check team status", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["9am"], "category": "management"},
                {"title": "All-hands meeting", "item_type": "event", "priority": "high", "frequency": "monthly", "scheduled_time": datetime(2025, 8, 1, 15, 0), "category": "meetings"},
            ]
        }
        
        if not todo_widgets:
            self.log("No todo widgets found, skipping todo data creation", "WARNING")
            return
        
        for widget in todo_widgets:
            # Validate widget exists and is correct type
            if not widget.id or widget.widget_type != "todo":
                self.log(f"Invalid widget for todo: {widget.title}", "ERROR")
                continue
                
            # Get templates based on widget category
            templates = todo_templates.get(widget.category, todo_templates["productivity"])
            
            # Create items from templates
            created_count = 0
            for template in templates[:6]:  # Limit to 6 items per widget
                try:
                    todo_item = TodoItem(
                        id=str(uuid.uuid4()),
                        dashboard_widget_id=widget.id,
                        title=template["title"],
                        item_type=template["item_type"],
                        category=template["category"],
                        priority=template["priority"],
                        frequency=template["frequency"],
                        frequency_times=json.dumps(template.get("frequency_times")) if template.get("frequency_times") else None,
                        due_date=template.get("due_date"),
                        scheduled_time=template.get("scheduled_time"),
                        notes=f"Auto-generated todo item for {widget.title}",
                        is_completed=random.choice([True, False]) if random.random() < 0.3 else False,  # 30% chance of being completed
                        is_active=True,
                        last_completed_date=date.today() - timedelta(days=random.randint(1, 7)) if random.random() < 0.2 else None,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    self.session.add(todo_item)
                    self.created_data["todo_items"].append(todo_item)
                    created_count += 1
                    
                except Exception as e:
                    self.log(f"✗ Failed to create todo item {template['title']}: {e}", "ERROR")
            
            self.log(f"✓ Created {created_count} todo items for: {widget.title}", "SUCCESS")
        
        self.session.commit()
        self.log(f"Created {len(self.created_data['todo_items'])} total todo items", "SUCCESS")
    
    def create_tracker_data(self):
        """Create SingleItemTracker instances with historical data"""
        self.section_header("Creating Tracker Data", "📈")
        
        tracker_widgets = [w for w in self.created_data["dashboard_widgets"] if w.widget_type == "singleitemtracker"]
        
        if not tracker_widgets:
            self.log("No tracker widgets found, skipping tracker data creation", "WARNING")
            return
        
        # Define tracker configurations
        tracker_configs = {
            "Step Counter": {"item_name": "Steps", "item_unit": "steps", "current_value": "8500", "target_value": "10000", "value_type": "number"},
            "Water Intake": {"item_name": "Water", "item_unit": "glasses", "current_value": "6", "target_value": "8", "value_type": "number"}
        }
        
        # Historical data templates
        historical_data = {
            "Steps": [
                {"value": "7800", "notes": "Rainy day, less walking"},
                {"value": "9200", "notes": "Good morning walk"},
                {"value": "12500", "notes": "Hiking day! Exceeded goal"},
                {"value": "8100", "notes": "Regular office day"},
                {"value": "10300", "notes": "Evening gym session"}
            ],
            "Water": [
                {"value": "5", "notes": "Need to drink more"},
                {"value": "8", "notes": "Perfect hydration day"},
                {"value": "6", "notes": "Good progress"},
                {"value": "7", "notes": "Almost reached goal"},
                {"value": "8", "notes": "Consistent hydration"}
            ]
        }
        
        for widget in tracker_widgets:
            # Validate widget exists and is correct type
            if not widget.id or widget.widget_type != "singleitemtracker":
                self.log(f"Invalid widget for tracker: {widget.title}", "ERROR")
                continue
                
            # Get config based on widget title (fallback to first config)
            config_key = next((k for k in tracker_configs.keys() if k in widget.title), list(tracker_configs.keys())[0])
            config = tracker_configs[config_key]
            
            try:
                # Create tracker instance
                tracker = SingleItemTracker(
                    id=str(uuid.uuid4()),
                    dashboard_widget_id=widget.id,
                    item_name=config["item_name"],
                    item_unit=config["item_unit"],
                    current_value=config["current_value"],
                    target_value=config["target_value"],
                    value_type=config["value_type"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self.session.add(tracker)
                self.session.commit()
                self.session.refresh(tracker)
                
                self.created_data["tracker_instances"].append(tracker)
                
                # Create historical entries
                entries = historical_data.get(config["item_name"], historical_data["Steps"])
                created_entries = 0
                
                for i, entry_data in enumerate(entries):
                    # Create entries with timestamps spread over last 7 days
                    entry_time = datetime.utcnow() - timedelta(days=len(entries)-i-1, hours=12)
                    
                    log_entry = SingleItemTrackerLog(
                        id=str(uuid.uuid4()),
                        tracker_id=tracker.id,
                        value=entry_data["value"],
                        notes=entry_data["notes"],
                        date=(datetime.utcnow() - timedelta(days=len(entries)-i-1)).date(),
                        created_at=entry_time
                    )
                    
                    self.session.add(log_entry)
                    self.created_data["tracker_logs"].append(log_entry)
                    created_entries += 1
                
                self.log(f"✓ Created tracker '{config['item_name']}' with {created_entries} entries for: {widget.title}", "SUCCESS")
                
            except Exception as e:
                self.log(f"✗ Failed to create tracker for {widget.title}: {e}", "ERROR")
                self.session.rollback()
        
        self.session.commit()
        self.log(f"Created {len(self.created_data['tracker_instances'])} trackers with {len(self.created_data['tracker_logs'])} total entries", "SUCCESS")
    
    def create_alarm_data(self):
        """Create Alarm configurations with various types"""
        self.section_header("Creating Alarm Data", "⏰")
        
        alarm_widgets = [w for w in self.created_data["dashboard_widgets"] if w.widget_type == "alarm"]
        
        if not alarm_widgets:
            self.log("No alarm widgets found, skipping alarm data creation", "WARNING")
            return
        
        # Define alarm templates by category
        alarm_templates = {
            "reminders": [
                {"title": "Morning Routine Start", "alarm_type": "daily", "alarm_times": ["06:30"]},
                {"title": "Take Vitamins", "alarm_type": "daily", "alarm_times": ["08:00"]},
                {"title": "Evening Wind Down", "alarm_type": "daily", "alarm_times": ["21:30"]},
            ],
            "work": [
                {"title": "Daily Standup", "alarm_type": "daily", "alarm_times": ["09:00"]},
                {"title": "Lunch Break", "alarm_type": "daily", "alarm_times": ["12:30"]},
                {"title": "End of Workday", "alarm_type": "daily", "alarm_times": ["17:30"]},
            ]
        }
        
        for widget in alarm_widgets:
            # Validate widget exists and is correct type
            if not widget.id or widget.widget_type != "alarm":
                self.log(f"Invalid widget for alarm: {widget.title}", "ERROR")
                continue
                
            # Get templates based on widget category
            templates = alarm_templates.get(widget.category, alarm_templates["reminders"])
            
            created_count = 0
            for template in templates[:5]:  # Limit to 5 alarms per widget
                try:
                    alarm = Alarm(
                        id=str(uuid.uuid4()),
                        dashboard_widget_id=widget.id,
                        title=template["title"],
                        alarm_type=template["alarm_type"],
                        alarm_times=template["alarm_times"],
                        frequency_value=template.get("frequency_value"),
                        specific_date=template.get("specific_date"),
                        is_active=random.choice([True, False]) if random.random() < 0.2 else True,  # 80% active
                        is_snoozed=False,
                        snooze_until=None,
                        last_triggered=datetime.utcnow() - timedelta(hours=random.randint(1, 24)) if random.random() < 0.3 else None,
                        next_trigger_time=datetime.utcnow() + timedelta(hours=random.randint(1, 48)),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    self.session.add(alarm)
                    self.created_data["alarms"].append(alarm)
                    created_count += 1
                    
                except Exception as e:
                    self.log(f"✗ Failed to create alarm {template['title']}: {e}", "ERROR")
            
            self.log(f"✓ Created {created_count} alarms for: {widget.title}", "SUCCESS")
        
        self.session.commit()
        self.log(f"Created {len(self.created_data['alarms'])} total alarms", "SUCCESS")
    
    def create_daily_widgets(self):
        """Create simple daily widget selections for today and yesterday"""
        self.section_header("Creating Daily Widget Selections", "📅")
        
        if not self.created_data["dashboard_widgets"]:
            self.log("No dashboard widgets found, skipping daily widget creation", "WARNING")
            return
            
        user = self.created_data["users"][0]
        all_widgets = self.created_data["dashboard_widgets"]
        
        # Simple approach: Create daily widgets for yesterday, today, and tomorrow
        dates_to_create = [
            date.today() - timedelta(days=1),  # Yesterday
            date.today(),                       # Today  
            date.today() + timedelta(days=1)    # Tomorrow
        ]
        
        total_created = 0
        
        for target_date in dates_to_create:
            # Simple selection: Pick 3-4 widgets per day with variety
            selected_widgets = self._simple_widget_selection(all_widgets, target_date)
            
            created_count = 0
            for position, widget in enumerate(selected_widgets):
                try:
                    # Simple grid positioning
                    grid_position = {"x": 0 if position % 2 == 0 else 6, "y": position * 2, "width": 6, "height": 3}
                    
                    # Simple AI reasoning
                    reasoning = f"Selected {widget.title} for {target_date.strftime('%A')} based on {widget.frequency} frequency and {widget.importance}/5 importance."
                    
                    daily_widget = DailyWidget(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        dashboard_widget_id=widget.id,
                        display_date=target_date,
                        position=position,
                        grid_position=grid_position,
                        ai_reasoning=reasoning,
                        is_pinned=position == 0,  # Pin the first widget only
                        created_at=datetime.utcnow()
                    )
                    
                    self.session.add(daily_widget)
                    self.created_data["daily_widgets"].append(daily_widget)
                    created_count += 1
                    
                except Exception as e:
                    self.log(f"✗ Failed to create daily widget for {widget.title}: {e}", "ERROR")
            
            self.log(f"✓ Created {created_count} daily widgets for {target_date}", "SUCCESS")
            total_created += created_count
        
        self.session.commit()
        self.log(f"Created {total_created} total daily widget selections", "SUCCESS")
    
    def _simple_widget_selection(self, all_widgets, target_date):
        """Simple widget selection - pick top 3-4 widgets ensuring variety"""
        # Group widgets by type for variety
        by_type = {}
        for widget in all_widgets:
            widget_type = widget.widget_type
            if widget_type not in by_type:
                by_type[widget_type] = []
            by_type[widget_type].append(widget)
        
        selected = []
        
        # Pick one widget from each type, prioritizing by importance
        for widget_type in ["todo", "websearch", "singleitemtracker", "alarm"]:
            if widget_type in by_type and len(selected) < 4:
                # Pick the highest importance widget of this type
                best_widget = max(by_type[widget_type], key=lambda w: w.importance)
                selected.append(best_widget)
        
        # If we still need more widgets, add the remaining highest importance ones
        while len(selected) < 3:
            remaining = [w for w in all_widgets if w not in selected]
            if not remaining:
                break
            best_remaining = max(remaining, key=lambda w: w.importance)
            selected.append(best_remaining)
        
        return selected
    
    def verify_data_creation(self):
        """Verify that all data was created successfully"""
        self.section_header("Data Verification", "✅")
        
        try:
            # Count records in each table
            counts = {
                "users": self.session.query(User).count(),
                "dashboard_widgets": self.session.query(DashboardWidget).count(),
                "daily_widgets": self.session.query(DailyWidget).count(),
                "websearch_queries": self.session.query(WebSearchQuery).count(),
                "summaries": self.session.query(Summary).count(),
                "todo_items": self.session.query(TodoItem).count(),
                "tracker_instances": self.session.query(SingleItemTracker).count(),
                "tracker_logs": self.session.query(SingleItemTrackerLog).count(),
                "alarms": self.session.query(Alarm).count(),
            }
            
            # Verify widget type distribution
            widget_types = self.session.execute(text("""
                SELECT widget_type, COUNT(*) as count 
                FROM dashboard_widgets 
                GROUP BY widget_type 
                ORDER BY widget_type
            """)).fetchall()
            
            # Verify foreign key relationships
            self.log("Verifying foreign key relationships:", "INFO")
            
            # Check WebSearch queries have valid widget IDs
            orphaned_queries = self.session.execute(text("""
                SELECT COUNT(*) FROM websearch_queries wq 
                LEFT JOIN dashboard_widgets dw ON wq.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Check Summaries have valid widget IDs
            orphaned_summaries = self.session.execute(text("""
                SELECT COUNT(*) FROM summaries s 
                LEFT JOIN dashboard_widgets dw ON s.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Check Todo items have valid widget IDs
            orphaned_todos = self.session.execute(text("""
                SELECT COUNT(*) FROM todo_items t 
                LEFT JOIN dashboard_widgets dw ON t.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Check Trackers have valid widget IDs
            orphaned_trackers = self.session.execute(text("""
                SELECT COUNT(*) FROM single_item_trackers sit 
                LEFT JOIN dashboard_widgets dw ON sit.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Check Tracker logs have valid tracker IDs
            orphaned_logs = self.session.execute(text("""
                SELECT COUNT(*) FROM single_item_tracker_logs sitl 
                LEFT JOIN single_item_trackers sit ON sitl.tracker_id = sit.id 
                WHERE sit.id IS NULL
            """)).scalar()
            
            # Check Alarms have valid widget IDs
            orphaned_alarms = self.session.execute(text("""
                SELECT COUNT(*) FROM alarms a 
                LEFT JOIN dashboard_widgets dw ON a.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Check Daily Widgets have valid widget IDs
            orphaned_daily_widgets = self.session.execute(text("""
                SELECT COUNT(*) FROM daily_widgets dw_daily 
                LEFT JOIN dashboard_widgets dw ON dw_daily.dashboard_widget_id = dw.id 
                WHERE dw.id IS NULL
            """)).scalar()
            
            # Report relationship integrity
            if (orphaned_queries == 0 and orphaned_summaries == 0 and orphaned_todos == 0 and 
                orphaned_trackers == 0 and orphaned_logs == 0 and orphaned_alarms == 0 and 
                orphaned_daily_widgets == 0):
                self.log("✅ All foreign key relationships are valid", "SUCCESS")
            else:
                self.log(f"❌ Found orphaned records: queries={orphaned_queries}, summaries={orphaned_summaries}, todos={orphaned_todos}, trackers={orphaned_trackers}, logs={orphaned_logs}, alarms={orphaned_alarms}, daily_widgets={orphaned_daily_widgets}", "ERROR")
            
            self.log("Database verification results:", "SUCCESS")
            for table, count in counts.items():
                self.log(f"  {table}: {count} records", "SUCCESS")
            
            self.log("Widget type distribution:", "SUCCESS")
            for widget_type, count in widget_types:
                self.log(f"  {widget_type}: {count} widgets", "SUCCESS")
            
            # Summary statistics
            print(f"\n📊 Database Population Summary:")
            print(f"   👤 Users: {counts['users']}")
            print(f"   📊 Dashboard Widgets: {counts['dashboard_widgets']}")
            print(f"   📅 Daily Widget Selections: {counts['daily_widgets']}")
            print(f"   🌐 WebSearch Queries: {counts['websearch_queries']}")
            print(f"   🤖 AI Summaries: {counts['summaries']}")
            print(f"   📝 Todo Items: {counts['todo_items']}")
            print(f"   📈 Tracker Instances: {counts['tracker_instances']}")
            print(f"   📋 Tracker Logs: {counts['tracker_logs']}")
            print(f"   ⏰ Alarms: {counts['alarms']}")
            
            return True
            
        except Exception as e:
            self.log(f"Verification failed: {e}", "ERROR")
            return False
    
    def run_population(self):
        """Execute the complete database population process"""
        print("\n" + "🗄️" * 60)
        print("🗄️ AI DASHBOARD - DIRECT DATABASE POPULATION")
        print("🗄️ Directly inserting realistic test data into SQLite database")
        print("🗄️" * 60)
        
        start_time = datetime.now()
        
        # Ensure tables are created before cleaning and populating
        from core.database import init_db
        init_db()

        try:
            # Step 1: Clean existing data
            self.cleanup_existing_data()
            
            # Step 2: Create default user
            self.create_default_user()
            
            # Step 3: Create dashboard widgets
            self.create_dashboard_widgets()
            
            # Step 4: Create WebSearch data
            self.create_websearch_data()
            
            # Step 5: Create Todo data
            self.create_todo_data()
            
            # Step 6: Create Tracker data
            self.create_tracker_data()
            
            # Step 7: Create Alarm data
            self.create_alarm_data()
            
            # Step 8: Create Daily Widget Selections (AI-curated)
            self.create_daily_widgets()
            
            # Step 9: Verify data creation
            success = self.verify_data_creation()
            
            # Final results
            duration = (datetime.now() - start_time).total_seconds()
            self.section_header("Population Complete", "🎉")
            
            print(f"⏱️  Total Duration: {duration:.1f} seconds")
            print(f"📊 Dashboard Widgets: {len(self.created_data['dashboard_widgets'])} created")
            print(f"📅 Daily Widget Selections: {len(self.created_data['daily_widgets'])} created")
            print(f"🌐 WebSearch Queries: {len(self.created_data['websearch_queries'])} created")
            print(f"🤖 AI Summaries: {len(self.created_data['summaries'])} generated")
            print(f"📝 Todo Items: {len(self.created_data['todo_items'])} created")
            print(f"📈 Tracker Instances: {len(self.created_data['tracker_instances'])} created")
            print(f"📋 Tracker Logs: {len(self.created_data['tracker_logs'])} created")
            print(f"⏰ Alarms: {len(self.created_data['alarms'])} created")
            print(f"\n🎉 DIRECT DATABASE POPULATION SUCCESSFUL!")
            print(f"🗄️ All data inserted directly into SQLite database!")
            
            return success
            
        except Exception as e:
            self.log(f"Population failed: {e}", "ERROR")
            traceback.print_exc()
            return False
        finally:
            self.session.close()

def main():
    """Main execution function"""
    print("🗄️ AI Dashboard Direct Database Populator")
    print("💾 This script directly inserts data into the SQLite database")
    
    # Ask for confirmation
    response = input("\n⚠️  This will CLEAR existing widget data and populate with fresh test data. Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        return
    
    # Run population
    populator = DirectDatabasePopulator()
    success = populator.run_population()
    
    print("\n" + "🏁" * 60)
    if success:
        print("🏁 DIRECT DATABASE POPULATION COMPLETED SUCCESSFULLY!")
        print("🏁 Database is now populated with realistic test data.")
        print("🏁 You can start the API server and explore the data.")
    else:
        print("🏁 DIRECT DATABASE POPULATION FAILED!")
        print("🏁 Check the errors above for details.")
    print("🏁" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
