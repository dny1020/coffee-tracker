"""Simple but comprehensive tests for heartrate endpoints"""


def test_log_heartrate_valid(client):
    """Test logging valid heart rate entry."""
    response = client.post(
        "/heartrate/",
        json={"bpm": 75, "context": "resting", "notes": "Feeling calm"},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bpm"] == 75


def test_log_heartrate_too_low(client):
    """Test that BPM below 30 is rejected."""
    response = client.post(
        "/heartrate/",
        json={"bpm": 25},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 422


def test_log_heartrate_too_high(client):
    """Test that BPM above 250 is rejected."""
    response = client.post(
        "/heartrate/",
        json={"bpm": 300},
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 422


def test_log_heartrate_without_auth(client):
    """Test that logging without auth fails."""
    response = client.post("/heartrate/", json={"bpm": 75})
    assert response.status_code == 403


def test_get_current_heartrate(client):
    """Test getting current heart rate."""
    response = client.get(
        "/heartrate/current",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200


def test_get_heartrate_logs(client):
    """Test getting heart rate logs."""
    response = client.get(
        "/heartrate/",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_heartrate_stats(client):
    """Test getting heart rate statistics."""
    response = client.get(
        "/heartrate/stats?days=30",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200


def test_get_correlation(client):
    """Test getting caffeine correlation analysis."""
    response = client.get(
        "/heartrate/correlation?hours_after=2",
        headers={"Authorization": "Bearer coffee-addict-secret-key-2025"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "correlations" in data
