import pytest
import requests

BASE_URL = "http://localhost:8000"

# Test widget creation
@pytest.mark.parametrize("widget_config", [
    {"title": "Daily Task Manager", "widget_type": "todo", "frequency": "daily", "category": "productivity", "importance": 5},
    {"title": "Research Assistant", "widget_type": "websearch", "frequency": "weekly", "category": "research", "importance": 3}
])
def test_create_dashboard_widget(widget_config):
    response = requests.post(f"{BASE_URL}/api/v1/widgets", json=widget_config)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == widget_config["title"]

# Test widget retrieval
def test_get_all_widgets():
    response = requests.get(f"{BASE_URL}/api/v1/widgets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0

# Test today's dashboard
def test_get_todays_dashboard():
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/widgets/today")
    assert response.status_code == 200
    data = response.json()
    assert "widgets" in data or isinstance(data, list)

# Test widget update
@pytest.mark.skip(reason="Requires widget id from creation test")
def test_update_dashboard_widget():
    # Example: update importance for a widget
    widget_id = "REPLACE_WITH_VALID_ID"
    update_data = {"importance": 10}
    response = requests.put(f"{BASE_URL}/api/v1/widgets/{widget_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["importance"] == 10

# Test widget deletion
@pytest.mark.skip(reason="Requires widget id from creation test")
def test_delete_dashboard_widget():
    widget_id = "REPLACE_WITH_VALID_ID"
    response = requests.delete(f"{BASE_URL}/api/v1/widgets/{widget_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success", True)
