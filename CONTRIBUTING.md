# Contributing to Coffee Tracker API

First off, thank you for considering contributing to Coffee Tracker! It's people like you that make this project better.

## Code of Conduct

This project and everyone participating in it is governed by basic principles of respect and professionalism. By participating, you are expected to uphold this standard.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (API requests, curl commands, etc.)
- **Describe the behavior you observed** and what you expected
- **Include logs** from the application
- **Environment details** (OS, Docker version, Python version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any similar features** in other APIs if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding conventions** (see below)
3. **Write tests** for your changes
4. **Ensure all tests pass** (`make test`)
5. **Update documentation** as needed
6. **Write clear commit messages**

#### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md under the [Unreleased] section
3. Ensure your code follows the project's coding standards
4. Run the full test suite and ensure it passes
5. Request review from maintainers

## Coding Conventions

### Python Style

- **Follow PEP 8** with these specifics:
  - Use **snake_case** for variables and functions
  - Use **PascalCase** for classes
  - Maximum line length: 100 characters (120 for comments)
  
- **Type hints are required** on all functions:
  ```python
  def log_coffee(coffee: CoffeeCreate, db: Session = Depends(get_db)) -> CoffeeResponse:
      ...
  ```

- **Use Pydantic models** for request/response validation

- **Add docstrings** to all public functions, classes, and modules:
  ```python
  def calculate_correlation(hours_after: int) -> dict:
      """Calculate caffeine-heart rate correlation.
      
      Args:
          hours_after: Number of hours after coffee to analyze
          
      Returns:
          Dictionary containing correlation statistics
      """
  ```

### API Conventions

- **RESTful endpoints**: Use proper HTTP verbs (GET, POST, PUT, DELETE)
- **snake_case for endpoints**: `/coffee/today` not `/coffeeToday`
- **Consistent error responses**: Use FastAPI's HTTPException
- **Rate limiting**: Add appropriate limits to new endpoints
- **Authentication**: Protect data endpoints with `Depends(verify_api_key)`

### Testing

- **Write tests** for all new features and bug fixes
- **Test file naming**: `test_*.py` in the `tests/` directory
- **Use fixtures**: Defined in `conftest.py`
- **Test coverage**: Aim for >80% coverage on new code

Example test:
```python
def test_new_feature(client, auth_headers):
    """Test description of what this validates."""
    response = client.post(
        "/endpoint/",
        json={"field": "value"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["field"] == "expected"
```

### Logging

- **Use the logging module**, not print():
  ```python
  import logging
  logger = logging.getLogger(__name__)
  
  logger.info("User action completed", extra={"user_id": 123})
  logger.error("Operation failed", exc_info=True)
  ```

- **Log levels**:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Warning messages for potentially harmful situations
  - `ERROR`: Error messages for failures
  - `CRITICAL`: Critical errors that may cause shutdown

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Example:
```
Add caffeine correlation endpoint

- Implement statistical analysis for caffeine-heart rate correlation
- Add configurable time window via query parameter
- Include comprehensive tests

Closes #42
```

### Branch Naming

- **Feature branches**: `feature/short-description`
- **Bug fixes**: `fix/issue-description`
- **Documentation**: `docs/what-changed`
- **Refactoring**: `refactor/component-name`

## Project Structure

When adding new features, follow the existing structure:

```
app/
├── main.py              # FastAPI app, middleware
├── settings.py          # Configuration
├── database.py          # Database setup
├── models.py            # SQLAlchemy models
├── auth.py              # Authentication
├── limiter.py           # Rate limiting
└── routers/
    ├── coffee.py        # Coffee endpoints
    └── heartrate.py     # Heart rate endpoints
```

## Development Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/coffee-tracker.git
   cd coffee-tracker
   ```

2. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Start services**:
   ```bash
   make up
   ```

4. **Run tests**:
   ```bash
   make test
   ```

5. **Check logs**:
   ```bash
   make logs
   ```

## Running Tests Locally

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_coffee.py -v

# Run with coverage
pytest --cov=app tests/ -v

# Run in Docker
make test-docker
```

## Documentation Changes

- Update README.md for user-facing changes
- Update API documentation (docstrings) for code changes
- Update .github/copilot-instructions.md for architectural changes
- Add examples to README for new endpoints

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for contributing! ☕
