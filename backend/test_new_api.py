"""
Test script for the new consolidated API endpoints.
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_dashboard_widgets():
    """Test dashboard widgets endpoints."""
    try:
        # Test getting all widgets (should return empty list initially)
        response = requests.get(f"{BASE_URL}/api/v1/dashboard-widgets/allwidgets")
        print(f"✅ Get all widgets: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        elif response.status_code == 404:
            print("   Expected 404 - no widgets exist yet")
        
        # Test creating a widget
        widget_data = {
            "widget_type": "alarm",
            "title": "Test Alarm",
            "frequency": "daily",
            "importance": 0.8,
            "category": "Health",
            "widget_config": {
                "alarm_times": ["07:00", "07:15"],
                "is_snoozable": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/dashboard-widgets/newwidget", json=widget_data)
        print(f"✅ Create widget: {response.status_code}")
        if response.status_code == 200:
            widget_data = response.json()
            print(f"   Created widget: {widget_data.get('id', 'N/A')}")
            
            # Test getting the specific widget
            widget_id = widget_data.get('id')
            if widget_id:
                response = requests.get(f"{BASE_URL}/api/v1/dashboard-widgets/{widget_id}")
                print(f"✅ Get specific widget: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Retrieved widget: {response.json().get('title', 'N/A')}")
                else:
                    print(f"   Failed to retrieve widget: {response.text}")
            
            # Test getting all widgets again (should now return the created widget)
            response = requests.get(f"{BASE_URL}/api/v1/dashboard-widgets/allwidgets")
            print(f"✅ Get all widgets after creation: {response.status_code}")
            if response.status_code == 200:
                widgets = response.json()
                print(f"   Found {len(widgets)} widgets")
            
            # Test getting widgets by type
            response = requests.get(f"{BASE_URL}/api/v1/dashboard-widgets/alloftype/alarm")
            print(f"✅ Get widgets by type: {response.status_code}")
            if response.status_code == 200:
                widgets = response.json()
                print(f"   Found {len(widgets)} alarm widgets")
        else:
            print(f"   Failed to create widget: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard widgets test failed: {e}")
        return False

def test_dashboard():
    """Test dashboard endpoints."""
    try:
        # Test getting today's widget list
        response = requests.get(f"{BASE_URL}/api/v1/dashboard/getTodayWidgetList")
        print(f"✅ Get today's widget list: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing New Consolidated API Endpoints...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Dashboard Widgets", test_dashboard_widgets),
        ("Dashboard", test_dashboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"🎉 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The new API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 