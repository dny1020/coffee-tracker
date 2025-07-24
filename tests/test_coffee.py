import pytest
from datetime import datetime, date
from app.models import CoffeeLog

def test_log_coffee(client, sample_coffee_data):
   """Test logging coffee consumption"""
   response = client.post("/coffee/", json=sample_coffee_data)
   assert response.status_code == 200
   
   data = response.json()
   assert data["caffeine_mg"] == 95.0
   assert data["coffee_type"] == "espresso"
   assert data["notes"] == "test coffee"
   assert "id" in data
   assert "timestamp" in data

def test_log_coffee_minimal(client):
   """Test logging coffee with minimal data"""
   response = client.post("/coffee/", json={"caffeine_mg": 120.0})
   assert response.status_code == 200
   
   data = response.json()
   assert data["caffeine_mg"] == 120.0
   assert data["coffee_type"] is None

def test_log_coffee_invalid_data(client):
   """Test logging coffee with invalid data"""
   response = client.post("/coffee/", json={"coffee_type": "espresso"})
   assert response.status_code == 422  # Missing required caffeine_mg

def test_get_today_caffeine_empty(client):
   """Test getting today's caffeine when no coffee logged"""
   response = client.get("/coffee/today")
   assert response.status_code == 200
   
   data = response.json()
   assert data["total_caffeine_mg"] == 0
   assert data["addiction_level"] == "amateur"
   assert data["date"] == str(date.today())

def test_get_today_caffeine_with_data(client, sample_coffee_data):
   """Test getting today's caffeine with logged coffee"""
   # Log some coffee
   client.post("/coffee/", json=sample_coffee_data)
   client.post("/coffee/", json={"caffeine_mg": 150.0, "coffee_type": "large coffee"})
   
   response = client.get("/coffee/today")
   assert response.status_code == 200
   
   data = response.json()
   assert data["total_caffeine_mg"] == 245.0
   assert data["addiction_level"] == "moderate"

def test_addiction_levels(client):
   """Test addiction level classifications"""
   # Amateur level (under 200mg)
   client.post("/coffee/", json={"caffeine_mg": 100.0})
   response = client.get("/coffee/today")
   assert response.json()["addiction_level"] == "amateur"
   
   # Reset by creating new client session would be complex,
   # so we'll add more to reach moderate
   client.post("/coffee/", json={"caffeine_mg": 150.0})
   response = client.get("/coffee/today")
   assert response.json()["addiction_level"] == "moderate"
   
   # Add more to reach severe
   client.post("/coffee/", json={"caffeine_mg": 200.0})
   response = client.get("/coffee/today")
   assert response.json()["addiction_level"] == "severe"

def test_get_coffee_logs(client, sample_coffee_data):
   """Test getting coffee logs"""
   # Log some coffee
   client.post("/coffee/", json=sample_coffee_data)
   client.post("/coffee/", json={"caffeine_mg": 120.0, "coffee_type": "americano"})
   
   response = client.get("/coffee/")
   assert response.status_code == 200
   
   data = response.json()
   assert len(data) == 2
   assert data[0]["caffeine_mg"] in [95.0, 120.0]  # Order might vary

def test_get_coffee_logs_with_limit(client, sample_coffee_data):
   """Test getting coffee logs with limit"""
   # Log multiple coffees
   for i in range(5):
       client.post("/coffee/", json={"caffeine_mg": 50.0 + i * 10})
   
   response = client.get("/coffee/?limit=3")
   assert response.status_code == 200
   
   data = response.json()
   assert len(data) == 3

def test_update_coffee(client, sample_coffee_data):
   """Test updating coffee log"""
   # Create coffee log
   response = client.post("/coffee/", json=sample_coffee_data)
   coffee_id = response.json()["id"]
   
   # Update it
   update_data = {"caffeine_mg": 110.0, "notes": "updated notes"}
   response = client.put(f"/coffee/{coffee_id}", json=update_data)
   assert response.status_code == 200
   
   data = response.json()
   assert data["caffeine_mg"] == 110.0
   assert data["notes"] == "updated notes"
   assert data["coffee_type"] == "espresso"  # Unchanged

def test_update_nonexistent_coffee(client):
   """Test updating non-existent coffee log"""
   response = client.put("/coffee/999", json={"caffeine_mg": 100.0})
   assert response.status_code == 404
   assert "not found" in response.json()["detail"].lower()

def test_delete_coffee(client, sample_coffee_data):
   """Test deleting coffee log"""
   # Create coffee log
   response = client.post("/coffee/", json=sample_coffee_data)
   coffee_id = response.json()["id"]
   
   # Delete it
   response = client.delete(f"/coffee/{coffee_id}")
   assert response.status_code == 200
   assert "deleted" in response.json()["message"].lower()
   
   # Verify it's gone
   response = client.get("/coffee/")
   data = response.json()
   assert len(data) == 0

def test_delete_nonexistent_coffee(client):
   """Test deleting non-existent coffee log"""
   response = client.delete("/coffee/999")
   assert response.status_code == 404
   assert "not found" in response.json()["detail"].lower()

def test_get_week_caffeine_empty(client):
   """Test getting weekly caffeine when no data"""
   response = client.get("/coffee/week")
   assert response.status_code == 200
   
   data = response.json()
   assert isinstance(data, list)
   assert len(data) == 0

def test_get_week_caffeine_with_data(client):
   """Test getting weekly caffeine with data"""
   # Log some coffee
   client.post("/coffee/", json={"caffeine_mg": 95.0})
   client.post("/coffee/", json={"caffeine_mg": 120.0})
   
   response = client.get("/coffee/week")
   assert response.status_code == 200
   
   data = response.json()
   assert len(data) >= 1
   assert "date" in data[0]
   assert "total_mg" in data[0]
   assert data[0]["total_mg"] == 215.0

def test_partial_update_coffee(client, sample_coffee_data):
   """Test partial update of coffee log"""
   # Create coffee log
   response = client.post("/coffee/", json=sample_coffee_data)
   coffee_id = response.json()["id"]
   
   # Update only notes
   response = client.put(f"/coffee/{coffee_id}", json={"notes": "just notes update"})
   assert response.status_code == 200
   
   data = response.json()
   assert data["notes"] == "just notes update"
   assert data["caffeine_mg"] == 95.0  # Unchanged
   assert data["coffee_type"] == "espresso"  # Unchanged

def test_coffee_timestamp_auto_set(client, sample_coffee_data):
   """Test that timestamp is automatically set"""
   before = datetime.utcnow()
   response = client.post("/coffee/", json=sample_coffee_data)
   after = datetime.utcnow()
   
   data = response.json()
   timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
   
   assert before <= timestamp <= after