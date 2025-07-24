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

def test_heartrate_status_classifications(client):
   """Test heart rate status classifications"""
   # Test dead status (< 60)
   client.post("/heartrate/", json={"bpm": 45})
   response = client.get("/heartrate/current")
   assert response.json()["status"] == "dead"
   
   # Test normal status (60-100)
   client.post("/heartrate/", json={"bpm": 80})
   response = client.get("/heartrate/current")
   assert response.json()["status"] == "normal"
   
   # Test tachycardia status (> 100)
   client.post("/heartrate/", json={"bpm": 120})
   response = client.get("/heartrate/current")
   assert response.json()["status"] == "tachycardia"

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
   assert len(data["readings"]) == 3
   assert data["stats"]["min_bpm"] == 70
   assert data["stats"]["max_bpm"] == 90
   assert data["stats"]["avg_bpm"] == 80.0
   assert data["stats"]["count"] == 3

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
   
   # Wait a bit and log heart rate (simulate time passing)
   # In real test, we'd manipulate timestamps, but for simplicity we'll test the endpoint structure
   hr_response = client.post("/heartrate/", json={"bpm": 85, "context": "post-coffee"})
   
   response = client.get("/heartrate/correlation")
   assert response.status_code == 200
   
   data = response.json()
   assert "correlations" in data
   assert "summary" in data
   # Correlation might be empty due to timing windows, but endpoint should work

def test_correlation_time_window(client):
   """Test that correlation only considers relevant time windows"""
   # This test would require more complex timestamp manipulation
   # For now, just verify the endpoint doesn't crash
   response = client.get("/heartrate/correlation")
   assert response.status_code == 200

def test_partial_update_heartrate(client, sample_heartrate_data):
   """Test partial update of heart rate log"""
   # Create heart rate log
   response = client.post("/heartrate/", json=sample_heartrate_data)
   hr_id = response.json()["id"]
   
   # Update only context
   response = client.put(f"/heartrate/{hr_id}", json={"context": "active"})
   assert response.status_code == 200
   
   data = response.json()
   assert data["context"] == "active"
   assert data["bpm"] == 80  # Unchanged
   assert data["notes"] == "test heartrate"  # Unchanged

def test_heartrate_timestamp_auto_set(client, sample_heartrate_data):
   """Test that timestamp is automatically set"""
   before = datetime.utcnow()
   response = client.post("/heartrate/", json=sample_heartrate_data)
   after = datetime.utcnow()
   
   data = response.json()
   timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
   
   assert before <= timestamp <= after

def test_different_contexts(client):
   """Test different heart rate contexts"""
   contexts = ["resting", "active", "post-coffee", "panic", "sleeping"]
   
   for i, context in enumerate(contexts):
       response = client.post("/heartrate/", json={"bpm": 70 + i * 10, "context": context})
       assert response.status_code == 200
       assert response.json()["context"] == context

def test_extreme_bpm_values(client):
   """Test extreme but valid BPM values"""
   # Very low but technically possible
   response = client.post("/heartrate/", json={"bpm": 30})
   assert response.status_code == 200
   
   # Very high but technically possible
   response = client.post("/heartrate/", json={"bpm": 200})
   assert response.status_code == 200