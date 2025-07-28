#!/usr/bin/env python3
"""
🧪 AI Dashboard System - Dummy Data Population Script
Deletes existing database and creates fresh dummy data for testing

Current Focus:
🌐 WebSearch Widget Data
📊 Dashboard Widget Data

Usage:
    python populate_dummy_data.py
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DummyDataPopulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_data = {
            "widgets": [],
            "websearch_widgets": [],
            "summaries": [],
            "todo_widgets": [],
            "todo_items": []
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
    
    def request(self, method: str, url: str, data=None, description: str = ""):
        """Make HTTP request with error handling"""
        try:
            start = time.time()
            
            if method == "GET":
                resp = self.session.get(url)
            elif method == "POST":
                resp = self.session.post(url, json=data)
            elif method == "PUT":
                resp = self.session.put(url, json=data)
            elif method == "DELETE":
                resp = self.session.delete(url)
            
            duration = (time.time() - start) * 1000
            
            if resp.status_code >= 400:
                error_msg = f"{method} {url} -> {resp.status_code}"
                if description:
                    error_msg += f" ({description})"
                try:
                    error_detail = resp.json()
                    if "detail" in error_detail:
                        error_msg += f" - {error_detail['detail']}"
                except:
                    pass
                self.log(error_msg, "ERROR")
                return {"error": True, "status": resp.status_code, "message": error_msg}
            
            result = resp.json() if resp.content else {}
            if description:
                self.log(f"{description} -> {resp.status_code} ({duration:.0f}ms)", "SUCCESS")
            return result
            
        except Exception as e:
            error_msg = f"{method} {url} -> Failed: {e}"
            if description:
                error_msg += f" ({description})"
            self.log(error_msg, "ERROR")
            return {"error": True, "message": str(e)}
    
    def check_server_health(self):
        """Check if server is running and healthy"""
        self.section_header("Server Health Check", "🏥")
        
        try:
            result = self.request("GET", f"{self.base_url}/api/health", description="Health check")
            if not result.get("error"):
                self.log("Server is running and healthy", "SUCCESS")
                return True
            else:
                self.log("Server health check failed", "ERROR")
                return False
        except Exception as e:
            self.log(f"Cannot connect to server: {e}", "ERROR")
            return False
    
    def clear_specific_tables(self):
        """Clear only the tables we're going to populate (safer than deleting entire DB)"""
        self.section_header("Clearing Target Tables", "🧹")
        
        # First check if we have any existing data to clear
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets", 
                             description="Check existing widgets")
        
        existing_widgets = []
        if isinstance(result, list):
            existing_widgets = result
            self.log(f"Found {len(existing_widgets)} existing widgets", "INFO")
        elif not result.get("error"):
            existing_widgets = result.get("widgets", [])
            self.log(f"Found {len(existing_widgets)} existing widgets", "INFO")
        
        # Clear existing websearch widgets and their data
        websearch_widgets = [w for w in existing_widgets if w.get("widget_type") == "websearch"]
        if websearch_widgets:
            self.log(f"Clearing {len(websearch_widgets)} existing websearch widgets...", "INFO")
            for widget in websearch_widgets:
                widget_id = widget.get("id")
                if widget_id:
                    # Delete websearch widget (this should cascade and delete related summaries)
                    self.request("DELETE", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}", 
                               description=f"Clear existing websearch widget: {widget.get('title', 'Unknown')}")
        
        # Clear other widget types we're going to create
        widget_types_to_clear = ["todo", "alarm", "singleitemtracker"]
        for widget_type in widget_types_to_clear:
            widgets_of_type = [w for w in existing_widgets if w.get("widget_type") == widget_type]
            if widgets_of_type:
                self.log(f"Clearing {len(widgets_of_type)} existing {widget_type} widgets...", "INFO")
                for widget in widgets_of_type:
                    widget_id = widget.get("id")
                    if widget_id:
                        # Delete the widget (should cascade to related data)
                        self.request("DELETE", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}", 
                                   description=f"Clear existing {widget_type} widget: {widget.get('title', 'Unknown')}")
        
        self.log("Target tables cleared successfully", "SUCCESS")
        return True
    
    def verify_tables_cleared(self):
        """Verify that target tables are cleared"""
        self.log("Verifying tables are cleared...", "INFO")
        
        # Check that widgets are cleared
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets", 
                             description="Verify widgets cleared")
        
        remaining_widgets = 0
        if isinstance(result, list):
            remaining_widgets = len(result)
        elif not result.get("error"):
            remaining_widgets = len(result.get("widgets", []))
        
        if remaining_widgets == 0:
            self.log("All target widgets cleared successfully", "SUCCESS")
            return True
        else:
            self.log(f"Warning: {remaining_widgets} widgets still remain", "WARNING")
            return True  # Continue anyway
    
    def create_websearch_widgets(self):
        """Create diverse websearch widgets with realistic data"""
        self.section_header("Creating WebSearch Widgets", "🌐")
        
        websearch_configs = [
            {
                "title": "AI & Machine Learning Research",
                "search_term": "latest machine learning algorithms and AI breakthroughs 2025",
                "frequency": "weekly",
                "category": "technology",
                "importance": 5
            },
            {
                "title": "Web Development Trends",
                "search_term": "React Next.js TypeScript best practices modern web development",
                "frequency": "daily",
                "category": "development",
                "importance": 4
            },
            {
                "title": "Startup News & Funding",
                "search_term": "startup funding rounds venture capital tech news",
                "frequency": "daily",
                "category": "business",
                "importance": 3
            },
            {
                "title": "Health & Fitness Updates",
                "search_term": "nutrition fitness workout health research studies",
                "frequency": "weekly",
                "category": "health",
                "importance": 3
            },
            {
                "title": "Climate Change News",
                "search_term": "climate change environmental sustainability renewable energy",
                "frequency": "weekly",
                "category": "environment",
                "importance": 4
            },
            {
                "title": "Cryptocurrency Market",
                "search_term": "Bitcoin Ethereum cryptocurrency market analysis blockchain",
                "frequency": "daily",
                "category": "finance",
                "importance": 2
            },
            {
                "title": "Space Exploration Updates",
                "search_term": "NASA SpaceX space exploration Mars missions astronomy",
                "frequency": "weekly",
                "category": "science",
                "importance": 3
            },
            {
                "title": "Cybersecurity Threats",
                "search_term": "cybersecurity threats data breaches security vulnerabilities",
                "frequency": "daily",
                "category": "security",
                "importance": 5
            }
        ]
        
        for i, config in enumerate(websearch_configs):
            self.log(f"Creating websearch widget {i+1}/{len(websearch_configs)}: {config['title']}", "INFO")
            
            result = self.request("POST", f"{self.base_url}/api/v1/widgets/websearch/generateSearch", 
                                 config, f"Create websearch widget: {config['title']}")
            
            if not result.get("error"):
                widget_id = result.get("widget_id")
                search_query_id = result.get("search_query_id")
                
                self.created_data["websearch_widgets"].append({
                    "widget_id": widget_id,
                    "search_query_id": search_query_id,
                    "title": config["title"],
                    "search_term": config["search_term"],
                    "category": config["category"]
                })
                
                self.log(f"✓ Created widget: {config['title']} (ID: {widget_id})", "SUCCESS")
            else:
                self.log(f"✗ Failed to create widget: {config['title']}", "ERROR")
    
    def generate_ai_summaries(self):
        """Generate AI summaries for some of the websearch widgets"""
        self.section_header("Generating AI Summaries", "🤖")
        
        # Generate summaries for first 4 widgets to save time
        widgets_to_summarize = self.created_data["websearch_widgets"][:4]
        
        summary_queries = [
            "Provide detailed analysis of current trends and breakthrough technologies",
            "What are the most important developments and best practices to follow",
            "Summarize key insights and actionable recommendations",
            "Highlight emerging patterns and future predictions"
        ]
        
        for i, widget in enumerate(widgets_to_summarize):
            widget_id = widget["widget_id"]
            title = widget["title"]
            query = summary_queries[i % len(summary_queries)]
            
            self.log(f"Generating AI summary for: {title}", "INFO")
            
            summary_data = {"query": query}
            result = self.request("POST", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}/summarize", 
                                 summary_data, f"Generate summary for: {title}")
            
            if not result.get("error") and result.get("success"):
                self.log(f"✓ Generated summary for: {title}", "SUCCESS")
                self.created_data["summaries"].append({
                    "widget_id": widget_id,
                    "widget_title": title,
                    "query": query
                })
                
                # Small delay to avoid overwhelming the AI service
                time.sleep(1)
            else:
                self.log(f"✗ Failed to generate summary for: {title}", "WARNING")
    
    def create_additional_dashboard_widgets(self):
        """Create additional dashboard widgets for comprehensive testing"""
        self.section_header("Creating Additional Dashboard Widgets", "📊")
        
        additional_widgets = [
            {
                "title": "Daily Task Planner",
                "widget_type": "todo",
                "frequency": "daily",
                "category": "productivity",
                "importance": 5,
                "settings": {"max_tasks": 20, "show_completed": True}
            },
            {
                "title": "Morning Reminders",
                "widget_type": "alarm",
                "frequency": "daily",
                "category": "reminders",
                "importance": 4,
                "settings": {"snooze_enabled": True, "default_snooze": 10}
            },
            {
                "title": "Fitness Tracker",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "category": "health",
                "importance": 4,
                "settings": {"item_name": "Steps", "unit": "steps", "target": "10000"}
            },
            {
                "title": "Work Schedule",
                "widget_type": "alarm",
                "frequency": "weekly",
                "category": "work",
                "importance": 5,
                "settings": {"work_hours": "9-17", "break_reminders": True}
            }
        ]
        
        for widget_config in additional_widgets:
            result = self.request("POST", f"{self.base_url}/api/v1/dashboard/widget", 
                                 widget_config, f"Create {widget_config['widget_type']} widget")
            
            if not result.get("error"):
                widget_id = result.get("id")
                self.created_data["widgets"].append({
                    "id": widget_id,
                    "type": widget_config["widget_type"],
                    "title": widget_config["title"]
                })
                self.log(f"✓ Created {widget_config['widget_type']} widget: {widget_config['title']}", "SUCCESS")
                
                # Track todo widgets separately for populating items
                if widget_config["widget_type"] == "todo":
                    self.created_data["todo_widgets"].append({
                        "id": widget_id,
                        "title": widget_config["title"],
                        "category": widget_config["category"]
                    })
            else:
                self.log(f"✗ Failed to create widget: {widget_config['title']}", "ERROR")
    
    def create_todo_items(self):
        """Create realistic todo items (Tasks/Events/Habits) for todo widgets"""
        self.section_header("Creating Todo Items", "📝")
        
        if not self.created_data["todo_widgets"]:
            self.log("No todo widgets found to populate", "WARNING")
            return
        
        # Define realistic todo items for each category
        todo_item_templates = {
            "productivity": [
                # Tasks
                {"title": "Complete quarterly review", "item_type": "task", "priority": "high", "frequency": "once", "category": "work", "due_date": "2025-08-15"},
                {"title": "Update project documentation", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "work"},
                {"title": "Clean desk and organize files", "item_type": "task", "priority": "low", "frequency": "weekly", "category": "organization"},
                {"title": "Review and respond to emails", "item_type": "task", "priority": "high", "frequency": "daily", "category": "communication"},
                {"title": "Plan next week's priorities", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "planning"},
                
                # Habits
                {"title": "Morning planning session", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["8:00am"], "category": "routine"},
                {"title": "Focus time block", "item_type": "habit", "priority": "high", "frequency": "daily-2", "frequency_times": ["10am", "2pm"], "category": "work"},
                {"title": "End-of-day reflection", "item_type": "habit", "priority": "medium", "frequency": "daily", "frequency_times": ["6pm"], "category": "reflection"},
                {"title": "Weekly review meeting", "item_type": "habit", "priority": "medium", "frequency": "weekly", "frequency_times": ["Friday 4pm"], "category": "planning"},
                
                # Events
                {"title": "Team standup meeting", "item_type": "event", "priority": "high", "frequency": "daily", "scheduled_time": "2025-07-29T09:00:00", "category": "meetings"},
                {"title": "Client presentation", "item_type": "event", "priority": "high", "frequency": "once", "scheduled_time": "2025-08-05T14:00:00", "category": "work"},
                {"title": "Project deadline", "item_type": "event", "priority": "high", "frequency": "once", "due_date": "2025-08-10", "category": "deadlines"}
            ],
            "health": [
                # Tasks
                {"title": "Schedule doctor checkup", "item_type": "task", "priority": "medium", "frequency": "once", "category": "medical", "due_date": "2025-08-30"},
                {"title": "Buy vitamins and supplements", "item_type": "task", "priority": "low", "frequency": "monthly", "category": "health"},
                {"title": "Meal prep for the week", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "nutrition"},
                
                # Habits
                {"title": "Morning workout", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["7am"], "category": "exercise"},
                {"title": "Drink water", "item_type": "habit", "priority": "high", "frequency": "daily-8", "frequency_times": ["every 2 hours"], "category": "hydration"},
                {"title": "Take vitamins", "item_type": "habit", "priority": "medium", "frequency": "daily", "frequency_times": ["8am"], "category": "supplements"},
                {"title": "Evening stretch", "item_type": "habit", "priority": "medium", "frequency": "daily", "frequency_times": ["9pm"], "category": "flexibility"},
                {"title": "Meditation session", "item_type": "habit", "priority": "medium", "frequency": "daily", "frequency_times": ["6am"], "category": "mindfulness"},
                
                # Events
                {"title": "Yoga class", "item_type": "event", "priority": "medium", "frequency": "weekly-2", "scheduled_time": "2025-07-30T18:00:00", "category": "exercise"},
                {"title": "Dental appointment", "item_type": "event", "priority": "medium", "frequency": "once", "scheduled_time": "2025-08-15T10:00:00", "category": "medical"}
            ],
            "work": [
                # Tasks
                {"title": "Prepare monthly report", "item_type": "task", "priority": "high", "frequency": "monthly", "category": "reporting", "due_date": "2025-08-31"},
                {"title": "Review team performance", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "management"},
                {"title": "Update project timeline", "item_type": "task", "priority": "medium", "frequency": "weekly", "category": "planning"},
                
                # Habits
                {"title": "Check team status", "item_type": "habit", "priority": "high", "frequency": "daily", "frequency_times": ["9am"], "category": "management"},
                {"title": "Skill development time", "item_type": "habit", "priority": "medium", "frequency": "weekly-3", "frequency_times": ["lunch break"], "category": "learning"},
                
                # Events
                {"title": "All-hands meeting", "item_type": "event", "priority": "high", "frequency": "monthly", "scheduled_time": "2025-08-01T15:00:00", "category": "meetings"},
                {"title": "Performance review", "item_type": "event", "priority": "high", "frequency": "once", "scheduled_time": "2025-08-20T11:00:00", "category": "hr"}
            ]
        }
        
        from datetime import datetime, date
        
        for todo_widget in self.created_data["todo_widgets"]:
            widget_id = todo_widget["id"]
            widget_title = todo_widget["title"]
            widget_category = todo_widget["category"]
            
            self.log(f"Populating todo items for: {widget_title}", "INFO")
            
            # Get relevant templates based on widget category
            templates = todo_item_templates.get(widget_category, todo_item_templates["productivity"])
            
            # Create items from templates
            created_count = 0
            for template in templates[:8]:  # Limit to 8 items per widget
                todo_data = {
                    "dashboard_widget_id": widget_id,
                    "title": template["title"],
                    "item_type": template["item_type"],
                    "priority": template["priority"],
                    "frequency": template["frequency"],
                    "category": template["category"]
                }
                
                # Add optional fields if present
                if "frequency_times" in template:
                    todo_data["frequency_times"] = template["frequency_times"]
                if "due_date" in template:
                    todo_data["due_date"] = template["due_date"]
                if "scheduled_time" in template:
                    todo_data["scheduled_time"] = template["scheduled_time"]
                if "notes" in template:
                    todo_data["notes"] = template["notes"]
                
                # Create the todo item using our clean API
                result = self.request("POST", f"{self.base_url}/api/v1/widgets/todo/items", 
                                     todo_data, f"Create {template['item_type']}: {template['title']}")
                
                if not result.get("error"):
                    item_id = result.get("id")
                    self.created_data["todo_items"].append({
                        "id": item_id,
                        "widget_id": widget_id,
                        "title": template["title"],
                        "type": template["item_type"],
                        "priority": template["priority"]
                    })
                    created_count += 1
                else:
                    self.log(f"✗ Failed to create todo item: {template['title']}", "ERROR")
            
            self.log(f"✓ Created {created_count} todo items for {widget_title}", "SUCCESS")
        
        # Mark some items as completed for realistic data
        self.mark_some_items_completed()
    
    def mark_some_items_completed(self):
        """Mark some todo items as completed for realistic data"""
        self.log("Marking some items as completed for realistic data...", "INFO")
        
        # Mark about 30% of items as completed
        import random
        items_to_complete = random.sample(
            self.created_data["todo_items"], 
            min(len(self.created_data["todo_items"]) // 3, 10)
        )
        
        completed_count = 0
        for item in items_to_complete:
            item_id = item["id"]
            
            result = self.request("POST", f"{self.base_url}/api/v1/widgets/todo/items/{item_id}?completed=true", 
                                 description=f"Mark completed: {item['title']}")
            
            if not result.get("error"):
                completed_count += 1
        
        self.log(f"✓ Marked {completed_count} items as completed", "SUCCESS")
    
    def verify_data_creation(self):
        """Verify that all data was created successfully"""
        self.section_header("Data Verification", "✅")
        
        # Check total widget count
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets", 
                             description="Get all widgets")
        
        if isinstance(result, list):
            total_widgets = len(result)
            websearch_widgets = len([w for w in result if w.get("widget_type") == "websearch"])
            
            self.log(f"Total widgets created: {total_widgets}", "SUCCESS")
            self.log(f"WebSearch widgets: {websearch_widgets}", "SUCCESS")
            self.log(f"Other widgets: {total_widgets - websearch_widgets}", "SUCCESS")
        
        # Check summaries
        summary_count = 0
        for ws_widget in self.created_data["websearch_widgets"][:4]:  # Check first 4
            widget_id = ws_widget["widget_id"]
            result = self.request("GET", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}/summary",
                                 description=f"Check summaries for {ws_widget['title']}")
            
            if isinstance(result, list) and len(result) > 0:
                summary_count += len(result)
        
        self.log(f"AI summaries generated: {summary_count}", "SUCCESS")
        
        # Check todo items
        todo_item_count = len(self.created_data["todo_items"])
        self.log(f"Todo items created: {todo_item_count}", "SUCCESS")
        
        # Summary statistics
        print(f"\n📊 Data Population Summary:")
        print(f"   🌐 WebSearch widgets: {len(self.created_data['websearch_widgets'])}")
        print(f"   📊 Dashboard widgets: {len(self.created_data['widgets'])}")
        print(f"   📝 Todo widgets: {len(self.created_data['todo_widgets'])}")
        print(f"   ✅ Todo items: {todo_item_count}")
        print(f"   🤖 AI summaries: {summary_count}")
    
    def run_population(self):
        """Execute the complete data population process"""
        print("\n" + "🚀" * 60)
        print("🚀 AI DASHBOARD - DUMMY DATA POPULATION")
        print("🚀 Creating realistic test data for development")
        print("🚀" * 60)
        
        start_time = time.time()
        
        try:
            # Step 1: Check server health
            if not self.check_server_health():
                self.log("Server is not available. Please start the server first.", "ERROR")
                return False
            
            # Step 2: Clear target tables (safer than deleting entire DB)
            if not self.clear_specific_tables():
                self.log("Failed to clear target tables", "ERROR")
                return False
            
            # Step 3: Verify tables are cleared
            if not self.verify_tables_cleared():
                self.log("Table clearing verification failed", "WARNING")
                # Continue anyway
            
            # Step 4: Create websearch widgets
            self.create_websearch_widgets()
            
            # Step 5: Generate AI summaries
            self.generate_ai_summaries()
            
            # Step 6: Create additional dashboard widgets
            self.create_additional_dashboard_widgets()
            
            # Step 7: Create todo items for todo widgets
            self.create_todo_items()
            
            # Step 8: Verify data creation
            self.verify_data_creation()
            
            # Final results
            duration = time.time() - start_time
            self.section_header("Population Complete", "🎉")
            
            print(f"⏱️  Total Duration: {duration:.1f} seconds")
            print(f"🌐 WebSearch widgets: {len(self.created_data['websearch_widgets'])} created")
            print(f"📊 Dashboard widgets: {len(self.created_data['widgets'])} created")
            print(f"📝 Todo items: {len(self.created_data['todo_items'])} created")
            print(f"🤖 AI summaries: {len(self.created_data['summaries'])} generated")
            print(f"\n🎉 DUMMY DATA POPULATION SUCCESSFUL!")
            
            return True
            
        except Exception as e:
            self.log(f"Population failed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main execution function"""
    print("🧪 AI Dashboard Dummy Data Populator")
    print("💡 Make sure FastAPI server is running: conda activate brainboard && python main.py")
    
    # Ask for confirmation
    response = input("\n⚠️  This will CLEAR existing widget data (websearch, todo, alarm, tracker). Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        return
    
    # Run population
    populator = DummyDataPopulator()
    success = populator.run_population()
    
    print("\n" + "🏁" * 60)
    if success:
        print("🏁 DUMMY DATA POPULATION COMPLETED SUCCESSFULLY!")
        print("🏁 You can now run tests or explore the API with realistic data.")
    else:
        print("🏁 DUMMY DATA POPULATION FAILED!")
    print("🏁" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
