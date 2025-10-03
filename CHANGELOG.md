# Changelog

All notable changes to the Coffee Tracker API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Structured logging with Python logging module
- Non-root user in Docker container for security
- .dockerignore for optimized Docker builds
- Comprehensive documentation (LICENSE, CHANGELOG, CONTRIBUTING, SECURITY, RUNBOOK)
- Resource limits documentation

### Changed
- Replaced all print() statements with proper logging
- Updated CI/CD configuration to fix GitHub Actions environment error
- Improved error logging with exc_info=True for stack traces

### Fixed
- GitHub Actions environment configuration error (line 88)
- Container security issue (now runs as non-root user)

## [1.0.0] - 2025-10-02

### Added
- FastAPI-based REST API for tracking caffeine and heart rate
- PostgreSQL database support with SQLite fallback
- Redis-backed rate limiting
- Prometheus metrics endpoint
- Comprehensive input validation (caffeine 0-1000mg, heart rate 30-250 BPM)
- Statistical analysis and correlation endpoints
- Bearer token authentication
- CORS and security headers
- Docker Compose orchestration
- Comprehensive test suite (pytest)
- GitHub Actions CI/CD pipeline
- Health check endpoints
- API documentation (Swagger/ReDoc)
- Makefile for common operations

### Security
- API key authentication with constant-time comparison
- Rate limiting per IP/API key
- Input sanitization and validation
- Security headers (CSP, X-Frame-Options, etc.)
- Trusted host middleware

### Documentation
- Comprehensive README with examples
- API documentation via OpenAPI
- Copilot instructions for AI assistants
- Environment configuration examples

[Unreleased]: https://github.com/dny1020/coffee-tracker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/dny1020/coffee-tracker/releases/tag/v1.0.0
