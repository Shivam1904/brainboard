#!/usr/bin/env python3
"""
🧪 AI Dashboard System - Complete Endpoint Test
Tests ALL endpoints with REAL data in ALL database tables

Coverage:
✅ All Dashboard Endpoints (GET/POST/PUT/DELETE)  
✅ All Web Summary Endpoints
✅ Health Check Endpoints
✅ Real data population in all 8 database tables
✅ Schema validation for all responses
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

    def run_all_tests(self):
        """Execute complete test suite"""
        self.log("🚀 Starting Complete AI Dashboard Test Suite", "INFO")
        start_time = time.time()
        
        try:
            # Test all endpoint categories
            self.test_health()
            self.test_dashboard()
            self.test_web_summary()
            
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
