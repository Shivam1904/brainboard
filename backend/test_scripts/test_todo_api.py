#!/usr/bin/env python3
"""
Test TODO API endpoints.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import aiohttp
import json
from datetime import datetime, date
from typing import Dict, Any

# ============================================================================
# CONSTANTS
# ============================================================================
BASE_URL = "http://localhost:8000"
TODO_BASE_URL = f"{BASE_URL}/api/v1/todo"
DEFAULT_USER_ID = "user_001"

# ============================================================================
# TEST FUNCTIONS
# ============================================================================
async def test_get_todo_details_and_activity(session: aiohttp.ClientSession, widget_id: str) -> Dict[str, Any]:
    """Test getting todo details and activity."""
    print(f"\n🔍 Testing getTodoDetailsAndActivity for widget: {widget_id}")
    
    url = f"{TODO_BASE_URL}/getTodoDetailsAndActivity/{widget_id}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_update_status(session: aiohttp.ClientSession, activity_id: str, status: str) -> Dict[str, Any]:
    """Test updating todo status."""
    print(f"\n🔄 Testing updateStatus for activity: {activity_id} to {status}")
    
    url = f"{TODO_BASE_URL}/updateStatus/{activity_id}"
    params = {"status": status}
    async with session.post(url, params=params) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_update_progress(session: aiohttp.ClientSession, activity_id: str, progress: int) -> Dict[str, Any]:
    """Test updating todo progress."""
    print(f"\n📊 Testing updateProgress for activity: {activity_id} to {progress}%")
    
    url = f"{TODO_BASE_URL}/updateProgress/{activity_id}"
    params = {"progress": progress}
    async with session.post(url, params=params) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_update_activity(session: aiohttp.ClientSession, activity_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test updating todo activity."""
    print(f"\n✏️ Testing updateActivity for activity: {activity_id}")
    
    url = f"{TODO_BASE_URL}/updateActivity/{activity_id}"
    async with session.post(url, json=update_data) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_todo_details(session: aiohttp.ClientSession, widget_id: str) -> Dict[str, Any]:
    """Test getting todo details."""
    print(f"\n📋 Testing getTodoDetails for widget: {widget_id}")
    
    url = f"{TODO_BASE_URL}/getTodoDetails/{widget_id}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_update_todo_details(session: aiohttp.ClientSession, todo_details_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test updating todo details."""
    print(f"\n✏️ Testing updateDetails for todo: {todo_details_id}")
    
    url = f"{TODO_BASE_URL}/updateDetails/{todo_details_id}"
    async with session.post(url, json=update_data) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_user_todos(session: aiohttp.ClientSession, user_id: str) -> Dict[str, Any]:
    """Test getting user todos."""
    print(f"\n👤 Testing getUserTodos for user: {user_id}")
    
    url = f"{TODO_BASE_URL}/user/{user_id}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_todo_list_by_type(session: aiohttp.ClientSession, todo_type: str) -> Dict[str, Any]:
    """Test getting todos by type."""
    print(f"\n📋 Testing getTodoList for type: {todo_type}")
    
    url = f"{TODO_BASE_URL}/getTodoList/{todo_type}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_today_todo_list(session: aiohttp.ClientSession, todo_type: str) -> Dict[str, Any]:
    """Test getting today's todo list by type."""
    print(f"\n📅 Testing getTodayTodoList for type: {todo_type}")
    
    url = f"{TODO_BASE_URL}/getTodayTodoList/{todo_type}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

async def test_get_todo_item_details_and_activity(session: aiohttp.ClientSession, daily_widget_id: str, widget_id: str) -> Dict[str, Any]:
    """Test getting todo item details and activity."""
    print(f"\n🔍 Testing getTodoItemDetailsAndActivity for daily_widget: {daily_widget_id}, widget: {widget_id}")
    
    url = f"{TODO_BASE_URL}/getTodoItemDetailsAndActivity/{daily_widget_id}/{widget_id}"
    async with session.get(url) as response:
        data = await response.json()
        print(f"Status: {response.status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        return data

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
async def run_todo_tests():
    """Run all TODO API tests."""
    print("🧪 Starting TODO API Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Get user todos first to find widget IDs
        user_todos = await test_get_user_todos(session, DEFAULT_USER_ID)
        
        # Test 2: Test getTodoList by type
        print("\n" + "=" * 30)
        print("📋 Testing getTodoList by type")
        await test_get_todo_list_by_type(session, "todo-task")
        await test_get_todo_list_by_type(session, "todo-habit")
        await test_get_todo_list_by_type(session, "todo-event")
        
        # Test 3: Test getTodayTodoList by type
        print("\n" + "=" * 30)
        print("📅 Testing getTodayTodoList by type")
        today_task_todos = await test_get_today_todo_list(session, "todo-task")
        today_habit_todos = await test_get_today_todo_list(session, "todo-habit")
        today_event_todos = await test_get_today_todo_list(session, "todo-event")
        
        # Test 4: Test getTodoItemDetailsAndActivity if we have data
        if today_task_todos.get("todos"):
            first_todo = today_task_todos["todos"][0]
            daily_widget_id = first_todo["daily_widget_id"]
            widget_id = first_todo["widget_id"]
            print("\n" + "=" * 30)
            print("🔍 Testing getTodoItemDetailsAndActivity")
            await test_get_todo_item_details_and_activity(session, daily_widget_id, widget_id)
        
        if user_todos.get("success") and user_todos.get("todos"):
            todo_widgets = user_todos["todos"]
            print(f"\n📋 Found {len(todo_widgets)} todo widgets")
            
            for i, todo in enumerate(todo_widgets):
                widget_id = todo["widget_id"]
                todo_id = todo["id"]
                print(f"\n🎯 Testing Todo {i+1}: {todo['title']} (ID: {todo_id})")
                
                # Test 5: Get todo details and activity
                details_and_activity = await test_get_todo_details_and_activity(session, widget_id)
                
                if details_and_activity.get("todo_details"):
                    # Test 6: Get todo details
                    await test_get_todo_details(session, widget_id)
                    
                    # Test 7: Update todo details
                    update_data = {
                        "description": f"Updated description for {todo['title']}",
                        "due_date": date.today().isoformat()
                    }
                    await test_update_todo_details(session, todo_id, update_data)
                
                if details_and_activity.get("activities"):
                    # Test 8: Update activity status
                    activity = details_and_activity["activities"][0]
                    activity_id = activity["id"]
                    
                    await test_update_status(session, activity_id, "completed")
                    await test_update_progress(session, activity_id, 75)
                    
                    # Test 9: Update activity with custom data
                    activity_update = {
                        "status": "in progress",
                        "progress": 50
                    }
                    await test_update_activity(session, activity_id, activity_update)
        else:
            print("❌ No todo widgets found. Please run generate_dummy_data.py first.")
    
    print("\n" + "=" * 50)
    print("✅ TODO API Tests Complete!")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(run_todo_tests()) 