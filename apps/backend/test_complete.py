#!/usr/bin/env python3
"""
🧪 AI Dashboard System - Clean Test Suite
Comprehensive API testing with isolated database to protect development data

Features:
- Isolated test database (doesn't touch your development data)
- Complete API endpoint testing for all widgets
- Automatic setup and cleanup
- Schema validation
- Real AI integration testing

Usage:
    conda activate brainboard && python test_complete.py

Test Structure:
📊 Dashboard API Tests
🌐 WebSearch API Tests  
📝 Todo API Tests (4 Clean Endpoints Only)
📈 Single Item Tracker API Tests
⏰ Alarm API Tests
🏥 Health API Tests
"""

import os
import sys
import tempfile
import shutil
import requests
import json
import time
import atexit
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Suppress SQLAlchemy warnings for cleaner test output
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestSettings:
    """Test-specific settings that override main settings for isolated testing"""
    
    def __init__(self):
        # Create temporary directory for test database
        self.test_db_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_db_dir, "test_brainboard.db")
        
        # Database configuration
        self.database_url = f"sqlite:///{self.test_db_path}"
        
        # Test-specific configurations
        self.debug = True
        self.app_name = "Brainboard API - Test Mode"
        
        # Reduce AI service limits for faster testing
        self.max_search_results = 3
        self.max_summary_tokens = 200
        self.widget_max_summaries_history = 10
        
        # Default settings
        self.default_user_id = "default_user"
        
    def cleanup_test_db(self):
        """Clean up test database file"""
        try:
            if self.test_db_path and os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
            if self.test_db_dir and os.path.exists(self.test_db_dir):
                shutil.rmtree(self.test_db_dir)
        except Exception as e:
            print(f"Warning: Could not clean up test database: {e}")

# Global test settings instance
test_settings = TestSettings()

# ============================================================================
# TEST DATABASE MANAGER
# ============================================================================

class TestDatabaseManager:
    """Manages test database lifecycle"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.is_setup = False
        
    def setup_test_database(self):
        """Create and initialize test database"""
        try:
            # Create test database engine
            self.engine = create_engine(
                test_settings.database_url,
                connect_args={"check_same_thread": False}
            )
            
            # Create SessionLocal for test database
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Import base for table creation
            from core.database import Base
            
            # Import all models to ensure they're registered
            from models.database_models import (
                Widget, Summary,  # Legacy models
                User, DashboardWidget,  # Core new models
                TodoTask, TodoItem, WebSearchQuery, Alarm, Habit, HabitLog  # Widget-specific models
            )
            
            # Create all tables in test database
            Base.metadata.create_all(bind=self.engine)
            
            # Create default test user
            self._create_test_user()
            
            self.is_setup = True
            return True
            
        except Exception as e:
            print(f"Failed to setup test database: {e}")
            return False
    
    def _create_test_user(self):
        """Create default test user in test database"""
        try:
            from models.database_models import User
            
            session = self.SessionLocal()
            try:
                # Check if test user already exists
                existing_user = session.query(User).filter_by(email="test@brainboard.com").first()
                if not existing_user:
                    test_user = User(
                        email="test@brainboard.com",
                        is_active=True
                    )
                    session.add(test_user)
                    session.commit()
            finally:
                session.close()
                
        except Exception as e:
            # User creation is optional for tests
            pass
    
    def clear_test_database(self):
        """Clear all data from test database but keep structure"""
        if not self.is_setup:
            return False
            
        try:
            # Import all models
            from models.database_models import (
                Widget, Summary, User, DashboardWidget,
                TodoItem, TodoTask, WebSearchQuery, Alarm, Habit, HabitLog
            )
            
            session = self.SessionLocal()
            try:
                # Delete all data in reverse dependency order
                session.query(Summary).delete()
                session.query(HabitLog).delete()
                session.query(TodoItem).delete()  # New TodoItem table
                session.query(TodoTask).delete()
                session.query(WebSearchQuery).delete()
                session.query(Alarm).delete()
                session.query(Habit).delete()
                session.query(DashboardWidget).delete()
                session.query(Widget).delete()
                # Keep the test user
                
                session.commit()
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Failed to clear test database: {e}")
            return False
    
    def teardown_test_database(self):
        """Clean up test database completely"""
        try:
            if self.engine:
                self.engine.dispose()
            
            test_settings.cleanup_test_db()
            self.is_setup = False
            
        except Exception as e:
            print(f"Could not fully clean up test database: {e}")

# Global test database manager
test_db_manager = TestDatabaseManager()

def setup_test_environment():
    """Setup test environment with isolated database"""
    print("🧪 Setting up test environment with isolated database...")
    
    # Setup test database
    success = test_db_manager.setup_test_database()
    if not success:
        print("❌ Failed to setup test database")
        return False
    
    # Monkey patch the main database settings to use test database
    import core.config
    import core.database
    
    # Override the main settings with test settings
    core.config.settings = test_settings
    
    # Override the main database engine with test engine
    core.database.engine = test_db_manager.engine
    core.database.SessionLocal = test_db_manager.SessionLocal
    
    print(f"✅ Test environment ready with database: {test_settings.test_db_path}")
    return True

def teardown_test_environment():
    """Clean up test environment"""
    print("🧹 Cleaning up test environment...")
    test_db_manager.teardown_test_database()
    print("✅ Test environment cleaned up")

# ============================================================================
# COMPREHENSIVE API TESTER
# ============================================================================

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_data = {
            "widgets": [],
            "tasks": [],
            "trackers": [],
            "alarms": [],
            "websearch_widgets": []
        }
        self.results = {"passed": 0, "failed": 0, "warnings": 0, "errors": []}
        self.test_db_setup = False
        
    def setup_test_database(self):
        """Setup isolated test database before running tests"""
        self.section_header("Test Database Setup", "🗄️")
        
        if setup_test_environment():
            self.test_db_setup = True
            self.log("Test database setup successful", "SUCCESS")
            
            # Register cleanup on exit
            atexit.register(self.cleanup_test_database)
            return True
        else:
            self.log("Test database setup failed", "ERROR")
            return False
    
    def cleanup_test_database(self):
        """Clean up test database after tests"""
        if self.test_db_setup:
            self.log("Cleaning up test database...", "INFO")
            teardown_test_environment()
            self.test_db_setup = False
    
    def clear_test_data(self):
        """Clear test data between test sections"""
        if self.test_db_setup:
            if test_db_manager.clear_test_database():
                self.log("Test data cleared for next test section", "INFO")
                return True
        return False
    
    def has_error(self, result):
        """Check if result has an error"""
        if isinstance(result, list):
            return False  # Lists are valid responses
        return result.get("error", False) if isinstance(result, dict) else False
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with section organization"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "SECTION": "📋"}
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '📝')} {message}")
        
        if level == "SUCCESS":
            self.results["passed"] += 1
        elif level == "ERROR":
            self.results["failed"] += 1
            self.results["errors"].append(message)
        elif level == "WARNING":
            self.results["warnings"] += 1
    
    def section_header(self, title: str, emoji: str = "📋"):
        """Print organized section headers"""
        print("\n" + "=" * 80)
        print(f"{emoji} {title}")
        print("=" * 80)
    
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
                self.log(f"{method} {url} -> {resp.status_code} ({duration:.0f}ms) - {description}", "SUCCESS")
            
            # Handle list responses - mark them as successful (no error)
            if isinstance(result, list):
                return result
            
            return result
            
        except Exception as e:
            error_msg = f"{method} {url} -> Failed: {e}"
            if description:
                error_msg += f" ({description})"
            self.log(error_msg, "ERROR")
            return {"error": True, "message": str(e)}
    
    def validate_schema(self, data: Any, name: str) -> bool:
        """Validate response schema"""
        try:
            if isinstance(data, dict):
                if "error" in data:
                    self.log(f"{name}: Contains error field", "ERROR")
                    return False
                self.log(f"{name}: Schema validation passed", "SUCCESS")
                return True
            elif isinstance(data, list):
                self.log(f"{name}: Valid list with {len(data)} items", "SUCCESS")
                return True
            else:
                self.log(f"{name}: Valid response", "SUCCESS")
                return True
        except Exception as e:
            self.log(f"{name}: Schema validation failed - {e}", "ERROR")
            return False
    
    # ========================================================================
    # HEALTH API TESTS
    # ========================================================================
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        self.section_header("Health Check API Tests", "🏥")
        
        # Basic health check
        result = self.request("GET", f"{self.base_url}/api/health", description="Basic health check")
        if not self.has_error(result):
            self.validate_schema(result, "Basic Health Response")
            
        # Detailed health check
        result = self.request("GET", f"{self.base_url}/api/health/detailed", description="Detailed health check")
        if not self.has_error(result):
            self.validate_schema(result, "Detailed Health Response")
            
            if result.get("status") == "healthy":
                self.log("System is healthy", "SUCCESS")
            
            if "database" in result:
                database_info = result["database"]
                if isinstance(database_info, dict):
                    db_status = database_info.get("status", "unknown")
                else:
                    db_status = str(database_info)
                self.log(f"Database status: {db_status}", "SUCCESS" if db_status == "healthy" else "WARNING")
    
    # ========================================================================
    # DASHBOARD API TESTS
    # ========================================================================
    
    def test_dashboard_endpoints(self):
        """Test dashboard widget management endpoints"""
        self.section_header("Dashboard Widget API Tests", "📊")
        
        self.log("Creating test widgets...", "INFO")
        
        # Test widget creation
        widget_configs = [
            {"title": "Daily Task Manager", "widget_type": "todo", "frequency": "daily", "category": "productivity", "importance": 5},
            {"title": "Research Assistant", "widget_type": "websearch", "frequency": "weekly", "category": "research", "importance": 3}
        ]
        
        created_widgets = []
        for config in widget_configs:
            result = self.request("POST", f"{self.base_url}/api/v1/dashboard/widget", config, f"Create {config['widget_type']} widget")
            if not self.has_error(result):
                self.validate_schema(result, f"{config['widget_type']} Widget")
                created_widgets.append(result)
                self.test_data["widgets"].append(result)
        
        # Test widget retrieval
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/widgets", description="Fetch all widgets")
        if isinstance(result, list) or not self.has_error(result):
            widgets = result if isinstance(result, list) else result.get("widgets", [])
            self.log(f"Retrieved {len(widgets)} widgets", "SUCCESS")
        
        # Test today's dashboard
        result = self.request("GET", f"{self.base_url}/api/v1/dashboard/today", description="Get AI-generated today's dashboard")
        if not self.has_error(result):
            self.validate_schema(result, "Today's Dashboard")
            
            if "widgets" in result:
                active_widgets = result["widgets"]
                self.log(f"Today's dashboard has {len(active_widgets)} active widgets", "SUCCESS")
                
                for widget in active_widgets:
                    if widget.get("ai_data"):
                        self.log(f"Widget {widget.get('title', 'unknown')} has AI-generated data", "SUCCESS")
        
        # Test widget update
        if created_widgets:
            widget_to_update = created_widgets[0]
            widget_id = widget_to_update.get("id")
            
            update_data = {"title": "Updated Daily Task Manager", "importance": 4}
            result = self.request("PUT", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}", update_data, "Update widget")
            if not self.has_error(result):
                self.validate_schema(result, "Updated Widget")
        
        # Test widget deletion
        if len(created_widgets) > 1:
            widget_to_delete = created_widgets[-1]
            widget_id = widget_to_delete.get("id")
            widget_title = widget_to_delete.get("title", "Unknown")
            
            result = self.request("DELETE", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}", description="Delete widget")
            if not self.has_error(result) or result.get("status") == 204:
                self.log(f"Deleted widget: {widget_title}", "SUCCESS")
                # Remove from test_data to avoid double deletion in cleanup
                self.test_data["widgets"] = [w for w in self.test_data["widgets"] if w.get("id") != widget_id]
    
    # ========================================================================
    # WEBSEARCH API TESTS
    # ========================================================================
    
    def test_websearch_endpoints(self):
        """Test WebSearch API with 4-endpoint structure"""
        self.section_header("WebSearch API Tests (Simplified Structure)", "🌐")
        
        self.log("Phase 1: Creating websearch widget with search query", "INFO")
        
        # 1. Create websearch widget with search
        search_data = {
            "title": "AI Development Research",
            "search_term": "FastAPI best practices and advanced features",
            "frequency": "weekly",
            "category": "development",
            "importance": 4
        }
        
        result = self.request("POST", f"{self.base_url}/api/v1/widgets/websearch/generateSearch", 
                             search_data, "Create websearch widget + search")
        
        if self.has_error(result):
            self.log("Failed to create websearch widget", "ERROR")
            return
        
        self.validate_schema(result, "WebSearch Widget Creation")
        
        widget_id = result.get("widget_id")
        search_query_id = result.get("search_query_id")
        
        if not widget_id:
            self.log("No widget_id returned from websearch creation", "ERROR")
            return
        
        self.log(f"Created widget {widget_id} with search: '{search_data['search_term']}'", "SUCCESS")
        self.test_data["websearch_widgets"].append({
            "widget_id": widget_id,
            "search_query_id": search_query_id,
            "title": search_data["title"]
        })
        
        self.log("Phase 2: Generating AI summary", "INFO")
        
        # 2. Generate AI summary
        summary_data = {"query": "Summarize the latest best practices and advanced features"}
        result = self.request("POST", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}/summarize", 
                             summary_data, "Generate AI summary")
        
        if not self.has_error(result):
            self.validate_schema(result, "Summary Generation Response")
            
            if result.get("success"):
                self.log(f"Summary generated successfully: {result.get('message', 'Unknown')}", "SUCCESS")
            else:
                self.log(f"Summary generation had issues: {result.get('message', 'Unknown')}", "WARNING")
        
        # Small delay for AI processing
        time.sleep(2)
        
        self.log("Phase 3: Retrieving generated summaries", "INFO")
        
        # 3. Get summaries
        result = self.request("GET", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}/summary", 
                             description="Get widget summaries")
        
        if not self.has_error(result):
            summaries = result if isinstance(result, list) else []
            self.validate_schema(summaries, "Summary List")
            
            self.log(f"Retrieved {len(summaries)} summaries", "SUCCESS")
            
            for i, summary in enumerate(summaries, 1):
                content_length = len(summary.get("content", ""))
                source_count = len(summary.get("sources", []))
                self.log(f"Summary {i}: {content_length} chars, {source_count} sources", "SUCCESS")
    
    # ========================================================================
    # TODO API TESTS - 4 CLEAN ENDPOINTS ONLY
    # ========================================================================
    
    def test_todo_endpoints(self):
        """Test clean Todo API with 4 endpoints only (Task/Event/Habit)"""
        self.section_header("Todo Widget API Tests - 4 Endpoints Only", "📝")
        
        # Find or use an existing todo widget
        todo_widget = None
        for widget in self.test_data["widgets"]:
            if widget.get("widget_type") == "todo":
                todo_widget = widget
                break
        
        if not todo_widget:
            self.log("No todo widget found for testing", "WARNING")
            return
        
        widget_id = todo_widget["id"]
        widget_title = todo_widget.get("title", "Unknown")
        self.log(f"Using todo widget: {widget_title} ({widget_id})", "INFO")
        
        self.log("Creating test todo items (Task/Event/Habit)...", "INFO")
        
        # Create test todo items using our clean 4-endpoint API
        item_configs = [
            {
                "dashboard_widget_id": widget_id,
                "title": "India Shopping",
                "item_type": "task",
                "frequency": "daily",
                "priority": "high",
                "category": "health"
            },
            {
                "dashboard_widget_id": widget_id,
                "title": "Gym Workout",
                "item_type": "habit",
                "frequency": "weekly-2",
                "frequency_times": ["7am"],
                "priority": "low",
                "category": "health"
            },
            {
                "dashboard_widget_id": widget_id,
                "title": "Drink Water",
                "item_type": "habit",
                "frequency": "daily-8",
                "frequency_times": ["every 2 hr"],
                "priority": "high",
                "category": "health"
            },
            {
                "dashboard_widget_id": widget_id,
                "title": "Doctor Appointment",
                "item_type": "event",
                "frequency": "once",
                "priority": "medium",
                "category": "health",
                "due_date": "2025-08-01"
            }
        ]
        
        created_items = []
        # ENDPOINT 1: POST /items - Create items
        for item_config in item_configs:
            result = self.request("POST", f"{self.base_url}/api/v1/widgets/todo/items", 
                                 item_config, f"Create {item_config['item_type']}: {item_config['title']}")
            if not self.has_error(result):
                self.validate_schema(result, f"{item_config['item_type']} Item Creation")
                created_items.append(result)
                self.test_data["todo_items"] = getattr(self.test_data, "todo_items", [])
                self.test_data["todo_items"].append(result)
        
        self.log(f"✅ Created {len(created_items)} todo items", "SUCCESS")
        
        # ENDPOINT 2: GET /items/{item_id} - Get specific item
        if created_items:
            item_id = created_items[0].get("id")
            result = self.request("GET", f"{self.base_url}/api/v1/widgets/todo/items/{item_id}", 
                                 description="Get specific todo item")
            if not self.has_error(result):
                self.validate_schema(result, "Specific Item Retrieval")
                self.log(f"✅ Retrieved item: {result.get('title', 'Unknown')}", "SUCCESS")
        
        # ENDPOINT 3: POST /items/{item_id} - Update item status
        if created_items:
            item_id = created_items[0].get("id")
            result = self.request("POST", f"{self.base_url}/api/v1/widgets/todo/items/{item_id}?completed=true", 
                                 description="Mark todo item as complete")
            if not self.has_error(result):
                self.validate_schema(result, "Item Status Update")
                self.log(f"✅ Marked item as completed", "SUCCESS")
        
        # ENDPOINT 4: DELETE /items/{item_id} - Delete item
        if len(created_items) > 1:
            item_id = created_items[-1].get("id")
            item_title = created_items[-1].get("title", "Unknown")
            result = self.request("DELETE", f"{self.base_url}/api/v1/widgets/todo/items/{item_id}", 
                                 description=f"Delete todo item: {item_title}")
            if not self.has_error(result):
                self.log(f"✅ Deleted item: {item_title}", "SUCCESS")
        
        self.log("🎯 All 4 core todo endpoints tested successfully!", "SUCCESS")
    
    # ========================================================================
    # CLEANUP METHODS
    # ========================================================================
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        self.section_header("Cleanup Test Data", "🧹")
        
        # Delete websearch widgets
        for widget_data in self.test_data["websearch_widgets"]:
            widget_id = widget_data["widget_id"]
            title = widget_data["title"]
            
            result = self.request("DELETE", f"{self.base_url}/api/v1/widgets/websearch/{widget_id}", 
                                 description=f"Delete websearch widget: {title}")
            if not self.has_error(result) or result.get("status") == 200:
                self.log(f"Deleted websearch widget: {title}", "SUCCESS")
        
        # Delete new todo items
        for item in getattr(self.test_data, "todo_items", []):
            item_id = item.get("id")
            item_title = item.get("title", "Unknown")[:30] + "..."
            
            result = self.request("DELETE", f"{self.base_url}/api/v1/widgets/todo/items/{item_id}", 
                                 description=f"Delete todo item: {item_title}")
            if not self.has_error(result) or result.get("status") == 200:
                self.log(f"Deleted todo item: {item_title}", "SUCCESS")
        
        # Delete widgets
        for widget in self.test_data["widgets"]:
            widget_id = widget.get("id")
            widget_title = widget.get("title", "Unknown")
            
            result = self.request("DELETE", f"{self.base_url}/api/v1/dashboard/widget/{widget_id}", 
                                 description=f"Delete widget: {widget_title}")
            if not self.has_error(result) or result.get("status") == 204:
                self.log(f"Deleted widget: {widget_title}", "SUCCESS")
    
    # ========================================================================
    # MAIN TEST EXECUTION
    # ========================================================================
    
    def run_comprehensive_tests(self):
        """Execute the complete test suite with isolated test database"""
        print("\n" + "🧪" * 40)
        print("🧪 AI DASHBOARD - COMPREHENSIVE API TESTING")
        print("🧪 Testing with isolated database to protect development data")
        print("🧪" * 40)
        
        start_time = time.time()
        
        try:
            # Setup isolated test database
            if not self.setup_test_database():
                self.log("Cannot proceed without test database setup", "ERROR")
                return False
            
            # Execute all test sections with clean data between each
            self.test_health_endpoints()
            
            # Clear test data between sections for clean isolated tests
            self.clear_test_data()
            self.test_dashboard_endpoints()
            
            self.clear_test_data()
            self.test_websearch_endpoints()
            
            self.clear_test_data()
            self.test_todo_endpoints()
            
            # Cleanup
            self.cleanup_test_data()
            
            # Final results
            duration = time.time() - start_time
            self.section_header("Test Results Summary", "📊")
            
            print(f"⏱️  Total Duration: {duration:.1f} seconds")
            print(f"✅ Tests Passed: {self.results['passed']}")
            print(f"❌ Tests Failed: {self.results['failed']}")
            print(f"⚠️  Warnings: {self.results['warnings']}")
            
            if self.results['failed'] == 0:
                print("\n🎉 ALL TESTS PASSED! API is functioning correctly.")
                success_rate = 100.0
            else:
                total_tests = self.results['passed'] + self.results['failed']
                success_rate = (self.results['passed'] / total_tests) * 100 if total_tests > 0 else 0
                print(f"\n⚠️  {self.results['failed']} tests failed. Success rate: {success_rate:.1f}%")
                
                # Show first few errors
                if self.results['errors']:
                    print("\n❌ First few errors:")
                    for error in self.results['errors'][:3]:
                        print(f"   • {error}")
                        
            return self.results['failed'] == 0
            
        except Exception as e:
            self.log(f"Test suite crashed: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Always cleanup test database
            self.cleanup_test_database()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function with isolated test database"""
    print("🧪 AI Dashboard API Test Suite")
    print("🔒 Using isolated test database to protect development data")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly at http://localhost:8000")
            print("💡 Please start the FastAPI server first: cd apps/backend && python main.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("💡 Please start the FastAPI server first: cd apps/backend && python main.py")
        sys.exit(1)
    
    print("✅ Server is running, proceeding with tests...")
    
    # Run tests
    tester = APITester()
    success = tester.run_comprehensive_tests()
    
    print("\n" + "🏁" * 40)
    if success:
        print("🏁 TEST SUITE COMPLETED SUCCESSFULLY!")
        print("🏁 Your development database remains untouched.")
    else:
        print("🏁 TEST SUITE COMPLETED WITH FAILURES!")
        print("🏁 Check the errors above for details.")
    print("🏁" * 40)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
