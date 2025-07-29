
import pytest
import requests

BASE_URL = "http://localhost:8000"

# Fixture to create a dashboard widget of type 'todo'
@pytest.fixture
def todo_widget():
    widget_config = {
        "title": "Test Todo Widget",
        "widget_type": "todo",
        "frequency": "daily",
        "category": "test",
        "importance": 1
    }
    response = requests.post(f"{BASE_URL}/api/v1/widgets", json=widget_config)
    assert response.status_code in (200, 201)
    widget = response.json()
    yield widget
    # Teardown: delete widget
    requests.delete(f"{BASE_URL}/api/v1/widgets/{widget['id']}")

# Parametrize todo items, passing widget id from fixture
@pytest.mark.parametrize("item_config", [
    {"title": "India Shopping", "item_type": "task", "frequency": "daily", "priority": "high", "category": "health"},
    {"title": "Gym Workout", "item_type": "habit", "frequency": "weekly-2", "frequency_times": ["7am"], "priority": "low", "category": "health"},
    {"title": "Drink Water", "item_type": "habit", "frequency": "daily-8", "frequency_times": ["every 2 hr"], "priority": "high", "category": "health"},
    {"title": "Doctor Appointment", "item_type": "event", "frequency": "once", "priority": "medium", "category": "health", "due_date": "2025-08-01"}
])
def test_create_todo_item(todo_widget, item_config):
    item_config = dict(item_config)  # Copy to avoid mutation
    item_config["dashboard_widget_id"] = todo_widget["id"]
    response = requests.post(f"{BASE_URL}/api/v1/widgets/todo/items", json=item_config)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "id" in data
    assert data["title"] == item_config["title"]
