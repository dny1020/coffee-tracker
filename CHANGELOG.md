# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-01

### Added
- **Database Migrations**: Added Alembic support for schema migrations
  - Created comprehensive MIGRATIONS.md guide
  - Added Makefile targets for migration management (`make migrate`, `make upgrade-db`, `make downgrade-db`)
  
- **Database Performance**:
  - Added composite indexes for coffee and heartrate tables
  - Indexed frequently queried columns (timestamp, bpm, context, coffee_type, caffeine_mg)
  - Added descending timestamp indexes for performance
  
- **Comprehensive Test Suite**:
  - Added `test_coffee.py` with 20+ coffee endpoint tests
  - Added `test_heartrate.py` with 20+ heartrate endpoint tests
  - Added `test_auth.py` for authentication and rate limiting tests
  - Tests cover validation, authentication, CRUD operations, and edge cases
  
- **Pagination Support**:
  - Added `offset` parameter to coffee logs endpoint
  - Added `offset` parameter to heartrate logs endpoint
  - Supports efficient pagination through large datasets
  
- **Makefile**: Added comprehensive build automation
  - Development commands: `make dev`, `make install-dev`
  - Testing commands: `make test`, `make test-docker`
  - Database commands: `make backup`, `make upgrade-db`
  - Production checks: `make prod-check`
  - Code quality: `make format`, `make lint`
  
- **Enhanced Health Check**:
  - Now checks PostgreSQL vs SQLite database type
  - Verifies Redis connection status
  - Returns detailed status for each component
  - Indicates degraded status when database is unhealthy
  
- **Security Documentation**:
  - Created comprehensive SECURITY.md
  - Security best practices for deployment
  - Vulnerability reporting guidelines
  - Compliance notes (HIPAA, GDPR)
  - Production security checklist
  
- **Configurable Settings**:
  - Made caffeine limits configurable (`max_caffeine_mg`, `recommended_daily_caffeine_mg`)
  - Made heart rate limits configurable (`min_heart_rate_bpm`, `max_heart_rate_bpm`)
  - Settings now affect validation and responses
  
- **Input Sanitization**:
  - Added control character removal from notes fields
  - Strips leading/trailing whitespace
  - Removes null bytes from user input
  
- **Dependencies**:
  - Added `alembic==1.13.1` for database migrations
  - Added `bleach==6.1.0` for HTML sanitization

### Changed
- **Docker Base Image**: Upgraded from Python 3.11 to Python 3.12-alpine
  - Addresses security vulnerabilities
  - Improved performance and compatibility
  
- **Database Connection Pooling**: 
  - Explicitly configured for production use
  - Pool size: 10, max overflow: 20
  - Added connection recycling (1 hour)
  - Improved reliability with `pool_pre_ping`
  
- **Error Handling**:
  - Metrics errors now logged instead of silently ignored
  - Better debugging capabilities
  - Warning emojis for visibility
  
- **Validation**:
  - Caffeine and heart rate limits now use configurable settings
  - More descriptive error messages
  - Dynamic validation based on configuration

### Fixed
- **Lint Errors**: Removed unused variables and imports
- **Type Safety**: Improved type hints throughout codebase
- **Documentation**: Fixed README references to Makefile commands

### Security
- **Enhanced Authentication**: Constant-time API key comparison already implemented
- **Input Validation**: Improved sanitization of user inputs
- **Request Limits**: Proper enforcement of request body size limits
- **Headers**: Security headers properly configured
- **Connection Security**: Database connections properly pooled and recycled

## [1.0.0] - 2025-07-23

### Added
- Initial release of Coffee Tracker API
- FastAPI-based REST API
- PostgreSQL and SQLite database support
- Redis-backed rate limiting
- API key authentication
- Coffee consumption tracking
- Heart rate tracking
- Caffeine-heart rate correlation analysis
- Prometheus metrics
- Docker and docker-compose deployment
- Comprehensive README documentation
- Input validation (caffeine: 0-1000mg, heart rate: 30-250 BPM)
- CORS and security middleware
- Timezone-aware timestamps
- Weekly and daily statistics
- Health check endpoint

### Security
- API key authentication with Bearer tokens
- Rate limiting per IP + API key
- Input validation with Pydantic
- CORS protection
- Trusted host validation
- Security headers (X-Frame-Options, CSP, etc.)
- Request size limits (1MB default)

## [Unreleased]

### Planned
- [ ] User authentication and multi-user support (JWT tokens)
- [ ] Data export functionality (CSV, JSON)
- [ ] Data deletion endpoints (GDPR compliance)
- [ ] Email notifications for high caffeine intake
- [ ] Mobile app integration
- [ ] Webhooks for third-party integrations
- [ ] Advanced analytics and visualizations
- [ ] Machine learning predictions
- [ ] Backup automation with scheduled tasks
- [ ] Audit logging for compliance
- [ ] Role-based access control (RBAC)
- [ ] API versioning (v2 endpoints)

### Considering
- GraphQL API alongside REST
- WebSocket support for real-time updates
- Integration with fitness trackers
- Social features (sharing, challenges)
- Custom dashboards
- Mobile push notifications
- Slack/Discord bot integration

## Migration Guide

### Upgrading from 1.0.0 to 1.1.0

1. **Update Docker Image**:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

2. **Install New Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Alembic** (if using migrations):
   ```bash
   make init-alembic
   # Follow MIGRATIONS.md guide to configure
   ```

4. **Run Tests**:
   ```bash
   make test
   ```

5. **No Breaking Changes**: All existing API endpoints remain compatible

### Configuration Changes
- No required configuration changes
- New optional settings available:
  - `MAX_CAFFEINE_MG` (default: 1000)
  - `RECOMMENDED_DAILY_CAFFEINE_MG` (default: 400)
  - `MIN_HEART_RATE_BPM` (default: 30)
  - `MAX_HEART_RATE_BPM` (default: 250)

## Version History

- **1.1.0** (2025-10-01): Major improvements - tests, migrations, performance
- **1.0.0** (2025-07-23): Initial release

---

**Note**: This project follows semantic versioning:
- MAJOR version for incompatible API changes
- MINOR version for added functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes
