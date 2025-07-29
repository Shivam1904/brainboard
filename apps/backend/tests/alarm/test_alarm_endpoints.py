import pytest
import requests

BASE_URL = "http://localhost:8000"

# Test creating alarm widget
@pytest.mark.parametrize("alarm_config", [
    {"title": "Morning Routine", "widget_type": "alarm", "category": "reminders", "importance": 4, "frequency": "daily"},
    {"title": "Work Schedule", "widget_type": "alarm", "category": "work", "importance": 5, "frequency": "weekly"},
    {"title": "Health Reminders", "widget_type": "alarm", "category": "health", "importance": 4, "frequency": "daily"}
])
def test_create_alarm_widget(alarm_config):
    response = requests.post(f"{BASE_URL}/api/v1/widgets", json=alarm_config)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == alarm_config["title"]

# Test getting alarms (requires widget_id)
@pytest.mark.skip(reason="Requires widget_id from creation test")
def test_get_alarms():
    widget_id = "REPLACE_WITH_VALID_ID"
    response = requests.get(f"{BASE_URL}/api/v1/widgets/alarm/{widget_id}/alarms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
