"""Heart rate endpoint tests."""


def test_log_heartrate_valid(client, auth_headers):
    """Test logging valid heart rate."""
    response = client.post(
        "/heartrate/",
        json={"bpm": 75, "context": "resting"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["bpm"] == 75


def test_log_heartrate_invalid(client, auth_headers):
    """Test invalid heart rate."""
    response = client.post(
        "/heartrate/",
        json={"bpm": 25},  # Too low
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_current_heartrate(client, auth_headers):
    """Test getting current heart rate."""
    response = client.get("/heartrate/current", headers=auth_headers)
    assert response.status_code == 200
