#!/usr/bin/env python3
"""
Quick test script for Todo Widget API
"""

import requests
import json
from datetime import date

def test_todo_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Todo Widget API")
    print("=" * 50)
    
    # 1. Create a Todo widget first
    print("1. Creating Todo widget...")
    widget_data = {
        "title": "My Daily Tasks",
        "widget_type": "todo", 
        "frequency": "daily",
        "category": "productivity",
        "importance": 5
    }
    
    response = requests.post(f"{base_url}/api/v1/dashboard/widget", json=widget_data)
    if response.status_code != 201:
        print(f"❌ Failed to create widget: {response.status_code}")
        return
    
    widget_id = response.json()["id"]
    print(f"✅ Created widget: {widget_id}")
    
    # 2. Create some tasks with different frequencies
    print("\n2. Creating tasks with different frequencies...")
    
    tasks = [
        {
            "content": "Check emails daily",
            "frequency": "daily",
            "priority": 4,
            "category": "work"
        },
        {
            "content": "Weekly team meeting",
            "frequency": "weekly", 
            "priority": 5,
            "category": "work"
        },
        {
            "content": "Monthly budget review",
            "frequency": "monthly",
            "priority": 3,
            "category": "finance"
        },
        {
            "content": "One-time project setup",
            "frequency": "once",
            "priority": 2,
            "category": "project",
            "due_date": str(date.today())
        }
    ]
    
    task_ids = []
    for task_data in tasks:
        task_data["dashboard_widget_id"] = widget_id
        response = requests.post(f"{base_url}/api/widgets/todo/tasks", json=task_data)
        if response.status_code == 200:
            task_id = response.json()["id"]
            task_ids.append(task_id)
            print(f"✅ Created {task_data['frequency']} task: {task_data['content']}")
        else:
            print(f"❌ Failed to create task: {response.status_code}")
    
    print(f"\n📊 Created {len(task_ids)} tasks")
    
    # 3. Get today's tasks
    print("\n3. Getting today's tasks...")
    response = requests.get(f"{base_url}/api/widgets/todo/tasks/today", params={"widget_id": widget_id})
    if response.status_code == 200:
        data = response.json()
        tasks = data["tasks"]
        stats = data["stats"]
        
        print(f"✅ Found {len(tasks)} tasks for today")
        print(f"📈 Stats: {stats['total_tasks']} total, {stats['completion_rate']:.1f}% complete")
        
        for task in tasks:
            print(f"   - [{task['frequency']}] {task['content']} (Priority: {task['priority']})")
    else:
        print(f"❌ Failed to get today's tasks: {response.status_code}")
    
    # 4. Mark a task as complete
    print("\n4. Testing task completion...")
    if task_ids:
        task_id = task_ids[0]
        response = requests.put(f"{base_url}/api/widgets/todo/tasks/{task_id}/status", 
                              params={"is_done": True})
        if response.status_code == 200:
            print("✅ Marked task as complete")
        else:
            print(f"❌ Failed to mark task complete: {response.status_code}")
    
    # 5. Get all tasks
    print("\n5. Getting all tasks...")
    response = requests.get(f"{base_url}/api/widgets/todo/tasks/all", 
                          params={"widget_id": widget_id, "include_completed": True})
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ Found {len(tasks)} total tasks")
        completed = sum(1 for t in tasks if t["is_done"])
        print(f"📊 {completed} completed, {len(tasks) - completed} pending")
    else:
        print(f"❌ Failed to get all tasks: {response.status_code}")
    
    # 6. Test dashboard integration
    print("\n6. Testing dashboard integration...")
    response = requests.get(f"{base_url}/api/v1/dashboard/today")
    if response.status_code == 200:
        data = response.json()
        widgets = data.get("widgets", [])
        todo_widgets = [w for w in widgets if w.get("type") == "todo"]
        if todo_widgets:
            print(f"✅ Todo widget appears in dashboard with {len(todo_widgets[0]['data']['tasks'])} tasks")
        else:
            print("⚠️ Todo widget not found in today's dashboard")
    else:
        print(f"❌ Failed to get dashboard: {response.status_code}")
    
    print("\n🎉 Todo API test completed!")

if __name__ == "__main__":
    test_todo_api()
