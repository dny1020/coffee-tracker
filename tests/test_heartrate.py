import pytest
from datetime import datetime, timedelta
from app.models import HeartRateLog, CoffeeLog

def test_log_heartrate(client, sample_heartrate_data):
    response = client.post("/heartrate/", json=sample_heartrate_data)
    assert response.status_code == 200
    data = response.json()
    assert data["bpm"] == 80
    assert data["context"] == "resting"
    assert data["notes"] == "test heartrate"
    assert "id" in data and "timestamp" in data

def test_log_heartrate_minimal(client):
    response = client.post("/heartrate/", json={"bpm": 75})
    assert response.status_code == 200
    data = response.json()
    assert data["bpm"] == 75
    assert data["context"] == "resting"
    assert data["notes"] is None

def test_log_heartrate_validation_low(client):
    response = client.post("/heartrate/", json={"bpm": 25})
    assert response.status_code == 422
    assert "30 BPM" in response.json()["detail"][0]["msg"]

def test_log_heartrate_validation_high(client):
    response = client.post("/heartrate/", json={"bpm": 300})
    assert response.status_code == 422
    assert "250 BPM" in response.json()["detail"][0]["msg"]

def test_log_heartrate_invalid_data(client):
    response = client.post("/heartrate/", json={"context": "resting"})
    assert response.status_code == 422

def test_get_current_heartrate_empty(client):
    response = client.get("/heartrate/current")
    assert response.status_code == 200
    assert "No heart rate data yet" in response.json()["message"]

def test_get_current_heartrate_with_data(client, sample_heartrate_data):
    client.post("/heartrate/", json=sample_heartrate_data)
    client.post("/heartrate/", json={"bpm": 95, "context": "post-coffee"})
    response = client.get("/heartrate/current")
    assert response.status_code == 200
    data = response.json()
    assert data["bpm"] == 95
    assert data["context"] == "post-coffee"
    assert data["status"] == "normal"
    assert "minutes_ago" in data and "is_recent" in data

def test_heartrate_status_classifications(client):
    client.post("/heartrate/", json={"bpm": 45})
    response = client.get("/heartrate/current")
    assert "bradycardia" in response.json()["status"]

    client.post("/heartrate/", json={"bpm": 80})
    response = client.get("/heartrate/current")
    assert response.json()["status"] == "normal"

    client.post("/heartrate/", json={"bpm": 130})
    response = client.get("/heartrate/current")
    assert "tachycardia" in response.json()["status"]

def test_get_heartrate_logs(client, sample_heartrate_data):
    client.post("/heartrate/", json=sample_heartrate_data)
    client.post("/heartrate/", json={"bpm": 90, "context": "active"})
    response = client.get("/heartrate/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    bpm_values = [entry["bpm"] for entry in data]
    assert 80 in bpm_values and 90 in bpm_values

def test_get_heartrate_logs_with_limit(client):
    for i in range(5):
        client.post("/heartrate/", json={"bpm": 70 + i * 5})
    response = client.get("/heartrate/?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_get_heartrate_range_empty(client):
    start = datetime.utcnow() - timedelta(hours=1)
    end = datetime.utcnow()
    response = client.get(f"/heartrate/range?start={start.isoformat()}&end={end.isoformat()}")
    assert response.status_code == 200
    assert "No data in that range" in response.json()["message"]

def test_get_heartrate_range_with_data(client):
    for bpm in [70, 80, 90]:
        client.post("/heartrate/", json={"bpm": bpm})
    start = datetime.utcnow() - timedelta(hours=1)
    end = datetime.utcnow() + timedelta(hours=1)
    response = client.get(f"/heartrate/range?start={start.isoformat()}&end={end.isoformat()}")
    data = response.json()
    assert data["readings_count"] == 3
    assert data["stats"]["min_bpm"] == 70
    assert data["stats"]["max_bpm"] == 90
    assert data["stats"]["avg_bpm"] == 80.0

def test_get_heartrate_stats_empty(client):
    response = client.get("/heartrate/stats")
    assert response.status_code == 200
    assert "No heart rate data" in response.json()["message"]

def test_get_heartrate_stats_with_data(client):
    client.post("/heartrate/", json={"bpm": 70, "context": "resting"})
    client.post("/heartrate/", json={"bpm": 120, "context": "active"})
    client.post("/heartrate/", json={"bpm": 85, "context": "post-coffee"})
    response = client.get("/heartrate/stats")
    data = response.json()
    assert data["total_readings"] == 3
    assert data["overall_stats"]["min_bpm"] == 70
    assert data["overall_stats"]["max_bpm"] == 120

def test_update_heartrate(client, sample_heartrate_data):
    post = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = post.json()["id"]
    update_data = {"bpm": 85, "notes": "updated notes"}
    response = client.put(f"/heartrate/{hr_id}", json=update_data)
    data = response.json()
    assert data["bpm"] == 85
    assert data["notes"] == "updated notes"
    assert data["context"] == "resting"

def test_update_heartrate_validation(client, sample_heartrate_data):
    post = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = post.json()["id"]
    response = client.put(f"/heartrate/{hr_id}", json={"bpm": 300})
    assert response.status_code == 422

def test_update_nonexistent_heartrate(client):
    response = client.put("/heartrate/999", json={"bpm": 80})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_heartrate(client, sample_heartrate_data):
    post = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = post.json()["id"]
    delete = client.delete(f"/heartrate/{hr_id}")
    assert delete.status_code == 200
    assert "deleted" in delete.json()["message"].lower()
    assert delete.json()["id"] == hr_id
    response = client.get("/heartrate/")
    assert len(response.json()) == 0

def test_delete_nonexistent_heartrate(client):
    response = client.delete("/heartrate/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_correlation_empty(client):
    response = client.get("/heartrate/correlation")
    assert response.status_code == 200
    assert response.json()["correlations"] == []
    assert "Not enough data" in response.json()["summary"]

def test_correlation_with_data(client):
    client.post("/coffee/", json={"caffeine_mg": 95.0, "coffee_type": "espresso"})
    client.post("/heartrate/", json={"bpm": 85, "context": "post-coffee"})
    response = client.get("/heartrate/correlation")
    data = response.json()
    assert "correlations" in data and "summary" in data

def test_correlation_custom_time_window(client):
    response = client.get("/heartrate/correlation?hours_after=4")
    assert response.status_code == 200
    data = response.json()
    if "analysis" in data:
        assert data["analysis"]["time_window_analyzed"] == "4 hours after coffee"

def test_extreme_but_valid_bpm_values(client):
    assert client.post("/heartrate/", json={"bpm": 30}).status_code == 200
    assert client.post("/heartrate/", json={"bpm": 250}).status_code == 200

def test_context_validation(client):
    valid_contexts = ["resting", "active", "post-coffee", "exercise", "sleeping", "panic", "stressed"]
    for ctx in valid_contexts:
        response = client.post("/heartrate/", json={"bpm": 80, "context": ctx})
        assert response.status_code == 200
        assert response.json()["context"] == ctx

def test_heartrate_timestamp_timezone(client, sample_heartrate_data):
    response = client.post("/heartrate/", json=sample_heartrate_data)
    ts = response.json()["timestamp"]
    assert "+" in ts or "Z" in ts or "T" in ts
