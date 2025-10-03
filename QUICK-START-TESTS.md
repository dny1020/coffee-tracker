# Quick Start - Testing Guide

## Run Tests Locally

### Basic Test Run
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Watch Mode (auto-rerun on changes)
```bash
pip install pytest-watch
ptw tests/
```

## Environment Variables (Tests)

The following environment variables are automatically set by `tests/conftest.py`:

```bash
DATABASE_URL=sqlite:///file:memdb1?mode=memory&cache=shared&uri=true
REDIS_URL=memory://
API_KEY=test-key-123
PYTEST_CURRENT_TEST=true
SKIP_DB_INIT=1
```

## Common Issues & Fixes

### ❌ Issue: "no such table: coffee_logs"
**Solution**: Ensure you're using the shared-cache SQLite URL (already fixed in conftest.py)

### ❌ Issue: POST requests hang/timeout
**Solution**: Don't consume request body in middleware (already fixed in app/main.py)

### ❌ Issue: Rate limiter causes deadlock
**Solution**: Use NoOpLimiter in test mode (already fixed in app/limiter.py)

## Test Structure

```
tests/
├── conftest.py           # Test configuration & fixtures
├── test_auth.py          # Authentication tests (5 tests)
├── test_coffee.py        # Coffee endpoint tests (3 tests)
└── test_heartrate.py     # Heart rate endpoint tests (3 tests)
```

## Writing New Tests

### Example Test
```python
def test_new_endpoint(client, auth_headers):
    """Test description."""
    response = client.post(
        "/new-endpoint/",
        json={"data": "value"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Available Fixtures
- `client` - TestClient instance (scope: module)
- `auth_headers` - Dict with valid Bearer token

## CI/CD Test Command

The CI/CD pipeline runs:
```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml
```

## Quick Commands

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_coffee.py -v

# Run specific test
pytest tests/test_coffee.py::test_log_coffee_valid -v

# Run with output
pytest tests/ -v -s

# Run failed tests only
pytest tests/ --lf

# Stop on first failure
pytest tests/ -x
```

## Test Coverage Goals

- **Minimum**: 80%
- **Target**: 90%+
- **Current**: Check Codecov dashboard

## Need Help?

- **CI/CD Guide**: `.github/CI-CD-GUIDE.md`
- **Test Fixes**: `TEST-FIXES-SUMMARY.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`

---

**Last Updated**: October 2025  
**Status**: ✅ All tests passing
