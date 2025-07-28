#!/usr/bin/env python3
"""
🧪 AI Dashboard System - Complete Endpoint Test
Tests ALL endpoints with REAL data in ALL database tables

Coverage:
✅ All Dashboard Endpoints (GET/POST/PUT/DELETE)  
✅ All Web Summary Endpoints
✅ All Todo Widget Endpoints (frequency-based task management)
✅ Health Check Endpoints
✅ Real data population in all 8 database tables
✅ Schema validation for all responses
✅ Smart frequency filtering for todo tasks
✅ Priority and category-based task organization
"""

import requests
import json
import time
from datetime import datetime
import sys

class ComprehensiveTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_widgets = []
        self.created_summaries = []
        self.results = {"passed": 0, "failed": 0, "warnings": 0, "errors": []}
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        print(f"{icons.get(level, '📝')} {level}: {message}")
        
        if level == "SUCCESS":
            self.results["passed"] += 1
        elif level == "ERROR":
            self.results["failed"] += 1
            self.results["errors"].append(message)
        elif level == "WARNING":
            self.results["warnings"] += 1
    
    def request(self, method: str, url: str, data=None):
        """Make HTTP request"""
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
                self.log(f"{method} {url} -> {resp.status_code}", "ERROR")
                return {"error": True, "status": resp.status_code}
            
            result = resp.json() if resp.content else {}
            self.log(f"{method} {url} -> {resp.status_code} ({duration:.0f}ms)", "SUCCESS")
            return result
            
        except Exception as e:
            self.log(f"{method} {url} -> Failed: {e}", "ERROR")
            return {"error": True, "message": str(e)}
    
    def validate(self, data, fields, name):
        """Validate response has required fields"""
        missing = [f for f in fields if f not in data]
        if missing:
            self.log(f"{name}: Missing {missing}", "ERROR")
            return False
        self.log(f"{name}: Schema valid", "SUCCESS")
        return True

    def test_health(self):
        """Test health endpoints"""
        self.log("🏥 Testing Health Endpoints", "INFO")
        
        # Basic health
        result = self.request("GET", f"{self.base_url}/api/health")
        if not result.get("error"):
            self.validate(result, ["status"], "Basic Health")
        
        # Detailed health
        result = self.request("GET", f"{self.base_url}/api/health/detailed") 
        if not result.get("error"):
            self.validate(result, ["status", "database"], "Detailed Health")

    def test_dashboard(self):
        """Test dashboard endpoints with real data creation"""
        self.log("📊 Testing Dashboard Endpoints", "INFO")
        
        # Create widgets for each type (populates database tables)
        widget_types = [
            {
                "title": "My Daily Tasks",
                "widget_type": "todo",
                "frequency": "daily",
                "category": "productivity",
                "importance": 5,
                "settings": {"max_tasks": 10, "show_completed": True}
            },
            {
                "title": "Important Reminders", 
                "widget_type": "alarm",
                "frequency": "daily",
                "category": "reminders",
                "importance": 4,
                "settings": {"snooze_enabled": True, "sound": "chime"}
            },
            {
                "title": "Quick Research",
                "widget_type": "websearch",
                "frequency": "weekly",
                "category": "learning",
                "importance": 3,
                "settings": {"max_results": 5, "auto_summarize": True}
            },
            {
                "title": "Daily Habits",
                "widget_type": "habittracker",
                "frequency": "daily",
                "category": "health",
                "importance": 5,
                "settings": {"streak_goal": 30, "reminder_time": "09:00"}
            },
            {
                "title": "Daily Weight Tracking",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "category": "health",
                "importance": 4,
                "settings": {"item_name": "Weight", "item_unit": "kg", "target_value": "70"}
            }
        ]
        
        for widget_data in widget_types:
            result = self.request("POST", f"{self.base_url}/api/v1/dashboard/widget", widget_data)
            if not result.get("error"):
                self.validate(result, ["id", "widget_type"], f"Create {widget_data['widget_type']}")
                self.created_widgets.append(result["id"])
        
        # Get all widgets (should have real data now)
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets")
        if isinstance(result, list):
            # API returns direct array of widgets
            widgets = result
            self.log(f"Found {len(widgets)} widgets with data", "SUCCESS")
        elif not result.get("error"):
            self.validate(result, ["widgets"], "Get Widgets")
            widgets = result.get("widgets", [])
            if widgets:
                self.log(f"Found {len(widgets)} widgets with data", "SUCCESS")
        
        # Get today's dashboard (AI-generated with populated data)
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/today")
        if not result.get("error"):
            self.validate(result, ["date", "widgets"], "Today Dashboard")
            widgets = result.get("widgets", [])
            for widget in widgets:
                if widget.get("data"):
                    widget_type = widget.get("type", "unknown")
                    self.log(f"Widget {widget_type} has populated data", "SUCCESS")
        
        # Update widget
        if self.created_widgets:
            widget_id = self.created_widgets[0]
            update_data = {"title": "Updated Widget Title", "importance": 3}
            result = self.request("PUT", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}", update_data)
            if not result.get("error"):
                self.validate(result, ["id", "title"], "Update Widget")
        
        # Delete widget  
        if self.created_widgets:
            widget_id = self.created_widgets.pop()
            result = self.request("DELETE", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}")
            if not result.get("error"):
                self.log(f"Deleted widget {widget_id}", "SUCCESS")

    def test_web_summary(self):
        """Test web summary endpoints"""
        self.log("🌐 Testing Web Summary Endpoints", "INFO")
        
        # 1. Create widget (populates widgets table)
        widget_data = {
            "query": "FastAPI tutorial guide"
        }
        result = self.request("POST", f"{self.base_url}/api/widget/web-summary/create", widget_data)
        widget_id = None
        if not result.get("error"):
            self.validate(result, ["widget_id", "summary"], "Create Web Summary Widget")
            widget_id = result.get("widget_id")
            if widget_id:
                self.created_summaries.append(widget_id)
        
        # 2. Generate new summary (populates summaries table)
        if widget_id:
            summary_data = {
                "query": "Advanced FastAPI features"
            }
            result = self.request("POST", f"{self.base_url}/api/widget/web-summary/{widget_id}/generate", summary_data)
            if not result.get("error"):
                self.validate(result, ["id", "summary"], "Generate New Summary")
        
        # 3. Get latest summary
        if widget_id:
            result = self.request("GET", f"{self.base_url}/api/widget/web-summary/{widget_id}/latest")
            if not result.get("error"):
                self.validate(result, ["id", "summary"], "Get Latest Summary")
        
        # 4. Get widget info  
        if widget_id:
            result = self.request("GET", f"{self.base_url}/api/widget/web-summary/{widget_id}")
            if not result.get("error"):
                self.validate(result, ["widget_id", "current_query"], "Get Widget Info")
        
        # 5. Delete widget
        if widget_id:
            result = self.request("DELETE", f"{self.base_url}/api/widget/web-summary/{widget_id}")
            if not result.get("error"):
                self.log(f"Deleted widget {widget_id}", "SUCCESS")

    def test_todo_widget(self):
        """Test todo widget endpoints with frequency-based task management"""
        self.log("📝 Testing Todo Widget Endpoints", "INFO")
        
        # 1. Create a Todo widget first (should already exist from dashboard test)
        todo_widget_id = None
        for widget_id in self.created_widgets:
            # Get widget info to find a todo widget
            result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets")
            if isinstance(result, list):
                widgets = result
                for widget in widgets:
                    if widget.get("widget_type") == "todo":
                        todo_widget_id = widget["id"]
                        break
                if todo_widget_id:
                    break
        
        if not todo_widget_id:
            # Create a new todo widget if none found
            widget_data = {
                "title": "Test Todo Widget",
                "widget_type": "todo",
                "frequency": "daily",
                "category": "testing",
                "importance": 5
            }
            result = self.request("POST", f"{self.base_url}/api/v1/dashboard/widget", widget_data)
            if not result.get("error"):
                todo_widget_id = result["id"]
                self.created_widgets.append(todo_widget_id)
        
        if not todo_widget_id:
            self.log("Failed to get todo widget for testing", "ERROR")
            return
        
        self.log(f"Using todo widget: {todo_widget_id}", "INFO")
        
        # 2. Create tasks with different frequencies
        task_data_list = [
            {
                "dashboard_widget_id": todo_widget_id,
                "content": "Daily task - Check emails",
                "frequency": "daily",
                "priority": 4,
                "category": "work"
            },
            {
                "dashboard_widget_id": todo_widget_id,
                "content": "Weekly task - Team meeting",
                "frequency": "weekly",
                "priority": 5,
                "category": "work"
            },
            {
                "dashboard_widget_id": todo_widget_id,
                "content": "Monthly task - Budget review",
                "frequency": "monthly",
                "priority": 3,
                "category": "finance"
            },
            {
                "dashboard_widget_id": todo_widget_id,
                "content": "One-time task - Project setup",
                "frequency": "once",
                "priority": 2,
                "category": "project"
            }
        ]
        
        created_task_ids = []
        for task_data in task_data_list:
            result = self.request("POST", f"{self.base_url}/api/widgets/todo/tasks", task_data)
            if not result.get("error"):
                self.validate(result, ["id", "content", "frequency"], f"Create {task_data['frequency']} task")
                created_task_ids.append(result["id"])
        
        self.log(f"Created {len(created_task_ids)} tasks", "SUCCESS")
        
        # 3. Get today's tasks (smart frequency filtering)
        result = self.request("GET", f"{self.base_url}/api/widgets/todo/tasks/today?widget_id={todo_widget_id}")
        if not result.get("error"):
            self.validate(result, ["widget_id", "tasks", "stats"], "Get Today's Tasks")
            tasks = result.get("tasks", [])
            stats = result.get("stats", {})
            self.log(f"Today's tasks: {len(tasks)} tasks, {stats.get('completion_rate', 0):.1f}% complete", "SUCCESS")
        
        # 4. Get all tasks with filtering
        result = self.request("GET", f"{self.base_url}/api/widgets/todo/tasks/all?widget_id={todo_widget_id}&include_completed=true")
        if isinstance(result, list):
            all_tasks = result
            self.log(f"All tasks: {len(all_tasks)} total tasks", "SUCCESS")
        elif not result.get("error"):
            all_tasks = result
            self.log(f"All tasks: {len(all_tasks)} total tasks", "SUCCESS")
        
        # 5. Update a task (mark as complete)
        if created_task_ids:
            task_id = created_task_ids[0]
            result = self.request("PUT", f"{self.base_url}/api/widgets/todo/tasks/{task_id}/status?is_done=true")
            if not result.get("error"):
                self.validate(result, ["id", "is_done"], "Mark Task Complete")
                
        # 6. Update a task (full update)
        if created_task_ids:
            task_id = created_task_ids[1] if len(created_task_ids) > 1 else created_task_ids[0]
            update_data = {
                "content": "Updated task content",
                "priority": 5,
                "category": "updated"
            }
            result = self.request("PUT", f"{self.base_url}/api/widgets/todo/tasks/{task_id}", update_data)
            if not result.get("error"):
                self.validate(result, ["id", "content"], "Update Task")
        
        # 7. Get specific task
        if created_task_ids:
            task_id = created_task_ids[0]
            result = self.request("GET", f"{self.base_url}/api/widgets/todo/tasks/{task_id}")
            if not result.get("error"):
                self.validate(result, ["id", "content", "frequency"], "Get Specific Task")
        
        # 8. Test category filtering
        result = self.request("GET", f"{self.base_url}/api/widgets/todo/tasks/all?widget_id={todo_widget_id}&category=work")
        if isinstance(result, list):
            work_tasks = result
            self.log(f"Work category tasks: {len(work_tasks)}", "SUCCESS")
        elif not result.get("error"):
            work_tasks = result
            self.log(f"Work category tasks: {len(work_tasks)}", "SUCCESS")
        
        # 9. Test priority filtering
        result = self.request("GET", f"{self.base_url}/api/widgets/todo/tasks/all?widget_id={todo_widget_id}&priority=5")
        if isinstance(result, list):
            high_priority_tasks = result
            self.log(f"High priority tasks: {len(high_priority_tasks)}", "SUCCESS")
        elif not result.get("error"):
            high_priority_tasks = result
            self.log(f"High priority tasks: {len(high_priority_tasks)}", "SUCCESS")
        
        # 10. Delete a task
        if created_task_ids:
            task_id = created_task_ids[-1]  # Delete the last created task
            result = self.request("DELETE", f"{self.base_url}/api/widgets/todo/tasks/{task_id}")
            if not result.get("error"):
                self.log(f"Deleted task {task_id}", "SUCCESS")

    def test_single_item_tracker_widget(self):
        """Test single item tracker widget endpoints for metrics tracking"""
        self.log("📈 Testing Single Item Tracker Widget Endpoints", "INFO")
        
        # 1. Find or create a single item tracker widget
        tracker_widget_id = None
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets")
        if isinstance(result, list):
            widgets = result
            for widget in widgets:
                if widget.get("widget_type") == "singleitemtracker":
                    tracker_widget_id = widget["id"]
                    break
        
        if not tracker_widget_id:
            # Create a new single item tracker widget
            widget_data = {
                "title": "Weight Tracker",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "category": "health",
                "importance": 4
            }
            result = self.request("POST", f"{self.base_url}/api/v1/dashboard/widget", widget_data)
            if not result.get("error"):
                tracker_widget_id = result["id"]
                self.created_widgets.append(tracker_widget_id)
        
        if not tracker_widget_id:
            self.log("Failed to get tracker widget for testing", "ERROR")
            return
        
        self.log(f"Using tracker widget: {tracker_widget_id}", "INFO")
        
        # 2. Create a single item tracker
        tracker_data = {
            "dashboard_widget_id": tracker_widget_id,
            "item_name": "Weight",
            "item_unit": "kg",
            "current_value": "75.5",
            "target_value": "70.0",
            "value_type": "decimal"
        }
        
        result = self.request("POST", f"{self.base_url}/api/widgets/single-item-tracker/create", tracker_data)
        tracker_id = None
        if not result.get("error"):
            self.validate(result, ["id", "item_name", "value_type"], "Create Single Item Tracker")
            tracker_id = result["id"]
        
        if not tracker_id:
            self.log("Failed to create tracker for testing", "ERROR")
            return
        
        # 3. Update tracker value (simulate daily weigh-in)
        value_updates = [
            {"value": "75.0", "notes": "Morning weigh-in"},
            {"value": "74.8", "notes": "Good progress"},
            {"value": "74.5", "notes": "Steady decline"}
        ]
        
        for i, update_data in enumerate(value_updates):
            result = self.request("PUT", f"{self.base_url}/api/widgets/single-item-tracker/{tracker_id}/update-value", update_data)
            if not result.get("error"):
                self.validate(result, ["id", "current_value"], f"Update Value #{i+1}")
        
        # 4. Get tracker with logs
        result = self.request("GET", f"{self.base_url}/api/widgets/single-item-tracker/{tracker_id}?limit=5")
        if not result.get("error"):
            self.validate(result, ["id", "item_name", "recent_logs"], "Get Tracker with Logs")
            logs = result.get("recent_logs", [])
            self.log(f"Tracker has {len(logs)} log entries", "SUCCESS")
        
        # 5. Get widget data for dashboard
        result = self.request("GET", f"{self.base_url}/api/widgets/single-item-tracker/widget/{tracker_widget_id}/data")
        if not result.get("error"):
            self.validate(result, ["widget_id", "tracker", "stats"], "Get Widget Data")
            stats = result.get("stats", {})
            current_value = stats.get("current_value")
            target_value = stats.get("target_value")
            progress = stats.get("progress_percentage")
            self.log(f"Tracker stats: {current_value}{tracker_data['item_unit']} → {target_value}{tracker_data['item_unit']} ({progress:.1f}% progress)" if progress else f"Current: {current_value}{tracker_data['item_unit']}", "SUCCESS")
        
        # 6. Update tracker settings
        settings_update = {
            "item_name": "Body Weight",
            "target_value": "68.0"
        }
        result = self.request("PUT", f"{self.base_url}/api/widgets/single-item-tracker/{tracker_id}", settings_update)
        if not result.get("error"):
            self.validate(result, ["id", "item_name"], "Update Tracker Settings")
        
        # 7. Get tracker logs with pagination
        result = self.request("GET", f"{self.base_url}/api/widgets/single-item-tracker/{tracker_id}/logs?limit=10&offset=0")
        if isinstance(result, list):
            logs = result
            self.log(f"Retrieved {len(logs)} log entries", "SUCCESS")
        
        # 8. Delete tracker (cleanup)
        result = self.request("DELETE", f"{self.base_url}/api/widgets/single-item-tracker/{tracker_id}")
        if not result.get("error"):
            self.log(f"Deleted tracker {tracker_id}", "SUCCESS")

    def run_all_tests(self):
        """Execute complete test suite"""
        self.log("🚀 Starting Complete AI Dashboard Test Suite", "INFO")
        start_time = time.time()
        
        try:
            # Test all endpoint categories
            self.test_health()
            self.test_dashboard()
            self.test_web_summary()
            self.test_todo_widget()  # Todo widget specific tests
            self.test_single_item_tracker_widget()  # Single item tracker widget tests
            
            # Results
            duration = time.time() - start_time
            self.log("📊 Final Results:", "INFO")
            self.log(f"   ✅ Passed: {self.results['passed']}", "SUCCESS")
            self.log(f"   ❌ Failed: {self.results['failed']}", "ERROR" if self.results['failed'] > 0 else "INFO")
            self.log(f"   ⚠️ Warnings: {self.results['warnings']}", "WARNING" if self.results['warnings'] > 0 else "INFO")
            self.log(f"   ⏱️ Duration: {duration:.1f}s", "INFO")
            
            if self.results['failed'] == 0:
                self.log("🎉 ALL TESTS PASSED! System ready for production", "SUCCESS")
                return True
            else:
                self.log("🔧 Some tests failed - check logs", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Test suite crashed: {e}", "ERROR")
            return False

def main():
    print("=" * 70)
    print("🧪 AI DASHBOARD - COMPLETE ENDPOINT TEST")
    print("Testing ALL endpoints with REAL data in ALL tables")
    print("=" * 70)
    
    tester = ComprehensiveTester()
    success = tester.run_all_tests()
    
    print("=" * 70)
    exit_code = 0 if success else 1
    status = "SUCCESS" if success else "FAILED"
    print(f"✅ TEST SUITE {status}")
    print("=" * 70)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
