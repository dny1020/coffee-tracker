"""Simple but comprehensive tests for the Coffee Tracker API"""


def test_log_coffee_valid(client):
    """Test logging valid coffee entry."""
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": 95, "coffee_type": "espresso", "notes": "Morning coffee"},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["caffeine_mg"] == 95


def test_log_coffee_negative_caffeine(client):
    """Test that negative caffeine is rejected."""
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": -10},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 422


def test_log_coffee_excessive_caffeine(client):
    """Test that excessive caffeine is rejected."""
    response = client.post(
        "/coffee/",
        json={"caffeine_mg": 1500},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 422


def test_log_coffee_without_auth(client):
    """Test that logging without auth fails."""
    response = client.post("/coffee/", json={"caffeine_mg": 95})
    assert response.status_code == 403


def test_get_today_caffeine(client):
    """Test getting today's caffeine total."""
    response = client.get(
        "/coffee/today",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_caffeine_mg" in data


def test_get_week_caffeine(client):
    """Test getting weekly breakdown."""
    response = client.get(
        "/coffee/week",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "week_total_mg" in data


def test_get_coffee_logs(client):
    """Test getting coffee logs."""
    response = client.get(
        "/coffee/",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_coffee_stats(client):
    """Test getting coffee statistics."""
    response = client.get(
        "/coffee/stats?days=30",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
