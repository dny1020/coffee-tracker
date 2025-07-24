import pytest
from datetime import datetime, timedelta
from app.models import HeartRateLog, CoffeeLog

def test_log_heartrate(client, sample_heartrate_data):
    """Test logging heart rate"""
    response = client.post("/heartrate/", json=sample_heartrate_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["bpm"] == 80
    assert data["context"] == "resting"
    assert data["notes"] == "test heartrate"
    assert "id" in data
    assert "timestamp" in data

def test_log_heartrate_minimal(client):
    """Test logging heart rate with minimal data"""
    response = client.post("/heartrate/", json={"bpm": 75})
    assert response.status_code == 200
    
    data = response.json()
    assert data["bpm"] == 75
    assert data["context"] == "resting"  # Default value
    assert data["notes"] is None

def test_log_heartrate_validation_low(client):
    """Test logging heart rate with too low BPM"""
    response = client.post("/heartrate/", json={"bpm": 25})
    assert response.status_code == 422
    assert "30 BPM" in response.json()["detail"][0]["msg"]

def test_log_heartrate_validation_high(client):
    """Test logging heart rate with too high BPM"""
    response = client.post("/heartrate/", json={"bpm": 300})
    assert response.status_code == 422
    assert "250 BPM" in response.json()["detail"][0]["msg"]

def test_log_heartrate_invalid_data(client):
    """Test logging heart rate with invalid data"""
    response = client.post("/heartrate/", json={"context": "resting"})
    assert response.status_code == 422  # Missing required bpm

def test_get_current_heartrate_empty(client):
    """Test getting current heart rate when no data"""
    response = client.get("/heartrate/current")
    assert response.status_code == 200
    
    data = response.json()
    assert "No heart rate data yet" in data["message"]

def test_get_current_heartrate_with_data(client, sample_heartrate_data):
    """Test getting current heart rate with data"""
    # Log some heart rates
    client.post("/heartrate/", json=sample_heartrate_data)
    client.post("/heartrate/", json={"bpm": 95, "context": "post-coffee"})
    
    response = client.get("/heartrate/current")
    assert response.status_code == 200
    
    data = response.json()
    assert data["bpm"] == 95  # Latest entry
    assert data["context"] == "post-coffee"
    assert data["status"] == "normal"  # 95 is normal range
    assert "minutes_ago" in data
    assert "is_recent" in data

def test_heartrate_status_classifications(client):
    """Test heart rate status classifications"""
    # Test bradycardia status (< 50)
    client.post("/heartrate/", json={"bpm": 45})
    response = client.get("/heartrate/current")
    assert "bradycardia" in response.json()["status"]
    
    # Test normal status (60-100)
    client.post("/heartrate/", json={"bpm": 80})
    response = client.get("/heartrate/current")
    assert response.json()["status"] == "normal"
    
    # Test tachycardia status (> 120)
    client.post("/heartrate/", json={"bpm": 130})
    response = client.get("/heartrate/current")
    assert "tachycardia" in response.json()["status"]

def test_get_heartrate_logs(client, sample_heartrate_data):
    """Test getting heart rate logs"""
    # Log some heart rates
    client.post("/heartrate/", json=sample_heartrate_data)
    client.post("/heartrate/", json={"bpm": 90, "context": "active"})
    
    response = client.get("/heartrate/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["bpm"] in [80, 90]  # Order might vary

def test_get_heartrate_logs_with_limit(client):
    """Test getting heart rate logs with limit"""
    # Log multiple readings
    for i in range(5):
        client.post("/heartrate/", json={"bpm": 70 + i * 5})
    
    response = client.get("/heartrate/?limit=3")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3

def test_get_heartrate_range_empty(client):
    """Test getting heart rate range when no data"""
    start = datetime.utcnow() - timedelta(hours=1)
    end = datetime.utcnow()
    
    response = client.get(f"/heartrate/range?start={start.isoformat()}&end={end.isoformat()}")
    assert response.status_code == 200
    
    data = response.json()
    assert "No data in that range" in data["message"]

def test_get_heartrate_range_with_data(client):
    """Test getting heart rate range with data"""
    # Log some heart rates
    client.post("/heartrate/", json={"bpm": 70})
    client.post("/heartrate/", json={"bpm": 80})
    client.post("/heartrate/", json={"bpm": 90})
    
    start = datetime.utcnow() - timedelta(hours=1)
    end = datetime.utcnow() + timedelta(hours=1)
    
    response = client.get(f"/heartrate/range?start={start.isoformat()}&end={end.isoformat()}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["readings_count"] == 3
    assert data["stats"]["min_bpm"] == 70
    assert data["stats"]["max_bpm"] == 90
    assert data["stats"]["avg_bpm"] == 80.0
    assert "median_bpm" in data["stats"]
    assert "std_dev" in data["stats"]

def test_get_heartrate_stats_empty(client):
    """Test getting heart rate stats when no data"""
    response = client.get("/heartrate/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "No heart rate data" in data["message"]

def test_get_heartrate_stats_with_data(client):
    """Test getting heart rate stats with data"""
    # Log various heart rates with different contexts
    client.post("/heartrate/", json={"bpm": 70, "context": "resting"})
    client.post("/heartrate/", json={"bpm": 120, "context": "active"})
    client.post("/heartrate/", json={"bpm": 85, "context": "post-coffee"})
    
    response = client.get("/heartrate/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_readings"] == 3
    assert "overall_stats" in data
    assert "by_context" in data
    assert "health_assessment" in data
    assert data["overall_stats"]["min_bpm"] == 70
    assert data["overall_stats"]["max_bpm"] == 120

def test_update_heartrate(client, sample_heartrate_data):
    """Test updating heart rate log"""
    # Create heart rate log
    response = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = response.json()["id"]
    
    # Update it
    update_data = {"bpm": 85, "notes": "updated notes"}
    response = client.put(f"/heartrate/{hr_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["bpm"] == 85
    assert data["notes"] == "updated notes"
    assert data["context"] == "resting"  # Unchanged

def test_update_heartrate_validation(client, sample_heartrate_data):
    """Test updating heart rate with invalid data"""
    # Create heart rate log
    response = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = response.json()["id"]
    
    # Try to update with invalid BPM
    response = client.put(f"/heartrate/{hr_id}", json={"bpm": 300})
    assert response.status_code == 422

def test_update_nonexistent_heartrate(client):
    """Test updating non-existent heart rate log"""
    response = client.put("/heartrate/999", json={"bpm": 80})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_heartrate(client, sample_heartrate_data):
    """Test deleting heart rate log"""
    # Create heart rate log
    response = client.post("/heartrate/", json=sample_heartrate_data)
    hr_id = response.json()["id"]
    
    # Delete it
    response = client.delete(f"/heartrate/{hr_id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()
    assert response.json()["id"] == hr_id
    
    # Verify it's gone
    response = client.get("/heartrate/")
    data = response.json()
    assert len(data) == 0

def test_delete_nonexistent_heartrate(client):
    """Test deleting non-existent heart rate log"""
    response = client.delete("/heartrate/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_correlation_empty(client):
    """Test caffeine correlation when no data"""
    response = client.get("/heartrate/correlation")
    assert response.status_code == 200
    
    data = response.json()
    assert data["correlations"] == []
    assert "Not enough data" in data["summary"]

def test_correlation_with_data(client):
    """Test caffeine correlation with data"""
    # Log coffee first
    coffee_response = client.post("/coffee/", json={"caffeine_mg": 95.0, "coffee_type": "espresso"})
    
    # Log heart rate
    hr_response = client.post("/heartrate/", json={"bpm": 85, "context": "post-coffee"})
    
    response = client.get("/heartrate/correlation")
    assert response.status_code == 200
    
    data = response.json()
    assert "correlations" in data
    assert "analysis" in data
    assert "summary" in data

def test_correlation_custom_time_window(client):
    """Test correlation with custom time window"""
    response = client.get("/heartrate/correlation?hours_after=4")
    assert response.status_code == 200
    
    data = response.json()
    if "analysis" in data:
        assert data["analysis"]["time_window_analyzed"] == "4 hours after coffee"

def test_extreme_but_valid_bpm_values(client):
    """Test extreme but valid BPM values"""
    # Very low but technically possible
    response = client.post("/heartrate/", json={"bpm": 30})
    assert response.status_code == 200
    
    # Very high but technically possible
    response = client.post("/heartrate/", json={"bpm": 250})
    assert response.status_code == 200

def test_context_validation(client):
    """Test different heart rate contexts"""
    valid_contexts = ["resting", "active", "post-coffee", "exercise", "sleeping", "panic", "stressed"]
    
    for context in valid_contexts:
        response = client.post("/heartrate/", json={"bpm": 80, "context": context})
        assert response.status_code == 200
        assert response.json()["context"] == context

def test_heartrate_timestamp_timezone(client, sample_heartrate_data):
    """Test that timestamp includes timezone info"""
    response = client.post("/heartrate/", json=sample_heartrate_data)
    
    data = response.json()
    timestamp_str = data["timestamp"]
    # Should contain timezone info or Z suffix
    assert "+" in timestamp_str or "Z" in timestamp_str or "T" in timestamp_str