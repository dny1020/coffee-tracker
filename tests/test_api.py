"""
Coffee Tracker API - Comprehensive Test Suite

Tests all major functionality:
- Authentication & Authorization
- Coffee logging endpoints
- Heart rate tracking endpoints
- Public endpoints (health, docs)
- Input validation
"""


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication."""

    def test_health_endpoint(self, client):
        """Health check should be publicly accessible."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["alive", "degraded"]

    def test_root_endpoint(self, client):
        """Root endpoint should be publicly accessible."""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "api_endpoints" in data

    def test_info_endpoint(self, client):
        """API info should be publicly accessible."""
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert "api_name" in data
        assert "endpoints" in data


class TestAuthentication:
    """Test authentication and authorization."""

    def test_protected_endpoint_requires_auth(self, client):
        """Protected endpoints should reject requests without auth."""
        response = client.get("/api/v1/coffee/today")
        assert response.status_code == 403

    def test_invalid_api_key_rejected(self, client):
        """Invalid API keys should be rejected."""
        headers = {"Authorization": "Bearer invalid-key-12345"}
        response = client.get("/api/v1/coffee/today", headers=headers)
        assert response.status_code == 401

    def test_valid_api_key_accepted(self, client, auth_headers):
        """Valid API key should grant access."""
        response = client.get("/api/v1/coffee/today", headers=auth_headers)
        assert response.status_code == 200


class TestCoffeeEndpoints:
    """Test coffee logging and analytics endpoints."""

    def test_log_coffee_valid(self, client, auth_headers):
        """Should successfully log valid coffee entry."""
        response = client.post(
            "/api/v1/coffee/",
            json={
                "caffeine_mg": 95,
                "coffee_type": "espresso",
                "notes": "morning boost"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["caffeine_mg"] == 95
        assert data["coffee_type"] == "espresso"

    def test_log_coffee_invalid_negative(self, client, auth_headers):
        """Should reject negative caffeine values."""
        response = client.post(
            "/api/v1/coffee/",
            json={"caffeine_mg": -10},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_log_coffee_invalid_too_high(self, client, auth_headers):
        """Should reject caffeine over 1000mg."""
        response = client.post(
            "/api/v1/coffee/",
            json={"caffeine_mg": 1500},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_get_today_caffeine(self, client, auth_headers):
        """Should return today's caffeine total."""
        response = client.get("/api/v1/coffee/today", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_caffeine_mg" in data
        assert "addiction_level" in data

    def test_get_coffee_stats(self, client, auth_headers):
        """Should return coffee statistics."""
        response = client.get("/api/v1/coffee/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_coffees" in data


class TestHeartRateEndpoints:
    """Test heart rate logging and analysis endpoints."""

    def test_log_heartrate_valid(self, client, auth_headers):
        """Should successfully log valid heart rate."""
        response = client.post(
            "/api/v1/heartrate/",
            json={
                "bpm": 75,
                "context": "resting",
                "notes": "before coffee"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bpm"] == 75
        assert data["context"] == "resting"

    def test_log_heartrate_invalid_too_low(self, client, auth_headers):
        """Should reject heart rate below 30 BPM."""
        response = client.post(
            "/api/v1/heartrate/",
            json={"bpm": 25},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_log_heartrate_invalid_too_high(self, client, auth_headers):
        """Should reject heart rate above 250 BPM."""
        response = client.post(
            "/api/v1/heartrate/",
            json={"bpm": 300},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_get_current_heartrate(self, client, auth_headers):
        """Should return current/latest heart rate."""
        response = client.get("/api/v1/heartrate/current", headers=auth_headers)
        assert response.status_code == 200

    def test_get_heartrate_stats(self, client, auth_headers):
        """Should return heart rate statistics."""
        response = client.get("/api/v1/heartrate/stats", headers=auth_headers)
        assert response.status_code == 200


class TestValidation:
    """Test input validation across all endpoints."""

    def test_coffee_type_max_length(self, client, auth_headers):
        """Should enforce coffee_type max length of 100 chars."""
        long_type = "a" * 101
        response = client.post(
            "/api/v1/coffee/",
            json={"caffeine_mg": 95, "coffee_type": long_type},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_notes_max_length(self, client, auth_headers):
        """Should enforce notes max length of 1000 chars."""
        long_notes = "a" * 1001
        response = client.post(
            "/api/v1/coffee/",
            json={"caffeine_mg": 95, "notes": long_notes},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_context_max_length(self, client, auth_headers):
        """Should enforce context max length of 50 chars."""
        long_context = "a" * 51
        response = client.post(
            "/api/v1/heartrate/",
            json={"bpm": 75, "context": long_context},
            headers=auth_headers
        )
        assert response.status_code == 422


class TestMetrics:
    """Test metrics and monitoring endpoints."""

    def test_metrics_endpoint_accessible(self, client):
        """Metrics endpoint should be accessible (if METRICS_PUBLIC=true)."""
        response = client.get("/metrics")
        # Should either return metrics (200) or require auth (401)
        assert response.status_code in [200, 401]

    def test_metrics_versioned_endpoint(self, client):
        """Versioned metrics endpoint should work."""
        response = client.get("/api/v1/metrics")
        # Should either return metrics (200) or require auth (401)
        assert response.status_code in [200, 401]
