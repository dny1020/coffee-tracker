# Coffee Tracker CI/CD Pipeline Guide

## Overview

This document describes the CI/CD pipeline for the Coffee Tracker API. The pipeline is implemented using GitHub Actions and provides automated testing, security scanning, building, and deployment.

## Pipeline Architecture

```
┌─────────────┐     ┌──────────────────┐
│   Push to   │────▶│  Pull Request    │
│ main/develop│     │   to main        │
└─────────────┘     └──────────────────┘
       │                     │
       ▼                     ▼
┌─────────────────────────────────────┐
│          Parallel Jobs              │
│  ┌──────────┐   ┌────────────────┐ │
│  │  Tests   │   │ Security Scan  │ │
│  └──────────┘   └────────────────┘ │
└─────────────────────────────────────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌────────────────┐
         │  Build Docker  │
         │     Image      │
         └────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Scan Docker   │
         │     Image      │
         └────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
  ┌─────────────┐   ┌─────────────┐
  │   Staging   │   │ Production  │
  │  (develop)  │   │   (main)    │
  └─────────────┘   └─────────────┘
         │                 │
         └────────┬────────┘
                  ▼
         ┌────────────────┐
         │    Notify      │
         └────────────────┘
```

## Jobs Description

### 1. **Test Job** 🧪

**Trigger**: All pushes and PRs  
**Duration**: ~30s  
**Purpose**: Run unit tests with coverage

**Steps**:
- ✅ Checkout code
- ✅ Setup Python 3.11 with pip cache
- ✅ Install dependencies from `requirements.txt`
- ✅ Optional linting with Ruff (non-blocking)
- ✅ Run pytest with coverage
- ✅ Upload coverage to Codecov
- ✅ Generate test summary

**Environment Variables**:
```bash
API_KEY=test-ci-key
SKIP_DB_INIT=1
DATABASE_URL=sqlite:///file:memdb1?mode=memory&cache=shared&uri=true
REDIS_URL=memory://
PYTEST_CURRENT_TEST=true
```

**Key Features**:
- Uses shared-cache SQLite in-memory DB to avoid table isolation issues
- No-op rate limiter in test mode (avoids TestClient threading issues)
- Middleware skips body consumption in tests
- Coverage reports uploaded to Codecov

### 2. **Security Scan Job** 🔒

**Trigger**: All pushes and PRs  
**Duration**: ~1-2 min  
**Purpose**: Scan code for vulnerabilities and secrets

**Steps**:
- ✅ Checkout code
- ✅ Run Trivy filesystem vulnerability scanner
- ✅ Upload results to GitHub Security tab
- ✅ Run TruffleHog secret scanner (non-blocking)

**Severity Levels**: CRITICAL, HIGH

### 3. **Build Job** 🏗️

**Trigger**: Only on push (not PRs)  
**Duration**: ~2-5 min  
**Purpose**: Build and push multi-arch Docker image

**Dependencies**: test + security-scan must pass

**Steps**:
- ✅ Checkout code
- ✅ Setup Docker Buildx for multi-platform builds
- ✅ Login to GitHub Container Registry (ghcr.io)
- ✅ Extract metadata (tags, labels)
- ✅ Build for `linux/amd64` and `linux/arm64`
- ✅ Push to registry with caching

**Image Tags**:
- `main` → `latest`
- `develop` → `develop`
- All branches → `<branch-name>`
- All commits → `<branch>-<sha>`

### 4. **Scan Image Job** 🔍

**Trigger**: Only on push (after build)  
**Duration**: ~1-2 min  
**Purpose**: Scan built Docker image for vulnerabilities

**Steps**:
- ✅ Run Trivy on Docker image
- ✅ Upload results to GitHub Security

### 5. **Deploy Staging** 🚀

**Trigger**: Push to `develop` branch  
**Dependencies**: build + scan-image must pass

**Current Status**: Placeholder (ready for implementation)

**TODO**:
- [ ] Configure GitHub Environment for staging
- [ ] Implement deployment (kubectl/docker-compose/etc.)
- [ ] Add health checks
- [ ] Configure rollback mechanism

### 6. **Deploy Production** 🎯

**Trigger**: Push to `main` branch  
**Dependencies**: build + scan-image must pass

**Current Status**: Placeholder (ready for implementation)

**TODO**:
- [ ] Configure GitHub Environment for production
- [ ] Implement deployment
- [ ] Add post-deployment health checks
- [ ] Configure rollback mechanism
- [ ] Setup monitoring alerts

### 7. **Notify** 📢

**Trigger**: After any deployment (always runs)  
**Purpose**: Send deployment status notifications

**Current Status**: Console logging

**TODO**:
- [ ] Integrate Slack/Discord notifications
- [ ] Send email alerts
- [ ] Update status page

## Test Configuration

### Fixed Issues (Oct 2025)

1. ✅ **SQLite In-Memory Database Isolation**
   - Changed from `sqlite:///:memory:` to shared cache URI
   - Tables now persist across connections

2. ✅ **POST Request Body Consumption**
   - Middleware no longer consumes request body
   - Checks `Content-Length` header instead

3. ✅ **Rate Limiter Threading**
   - Implemented `NoOpLimiter` for test mode
   - Avoids TestClient deadlocks

4. ✅ **SlowAPI Middleware**
   - Conditionally skipped in test mode
   - Prevents threading conflicts

### Running Tests Locally

**Basic tests**:
```bash
pytest tests/ -v
```

**With coverage** (like CI):
```bash
export API_KEY=test-ci-key
export SKIP_DB_INIT=1
export DATABASE_URL="sqlite:///file:memdb1?mode=memory&cache=shared&uri=true"
export REDIS_URL="memory://"
export PYTEST_CURRENT_TEST=true

pytest tests/ -v --cov=app --cov-report=term-missing
```

**Quick test**:
```bash
make test
```

## Secrets Configuration

### Required Secrets

#### Repository Secrets:
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions

#### Optional (for deployment):
- `PRODUCTION_API_KEY` - API key for production deployment
- `STAGING_API_KEY` - API key for staging deployment
- `CODECOV_TOKEN` - For Codecov integration (optional)

### Setting Secrets

1. Go to Repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Save

## Monitoring & Alerts

### GitHub Security Tab
- View Trivy scan results
- Track vulnerabilities over time
- Get automated security alerts

### Codecov
- Track test coverage trends
- Enforce coverage thresholds
- View coverage reports on PRs

### Workflow Status
- Check Actions tab for run history
- View logs for debugging
- Monitor job durations

## Branch Strategy

### Branches

- **`main`** - Production branch
  - Triggers: test → security → build → scan → deploy-production
  - Protected branch with required status checks

- **`develop`** - Staging branch
  - Triggers: test → security → build → scan → deploy-staging
  - Integration branch for features

- **Feature branches**
  - Triggers: test + security only (no build/deploy)
  - PR required to merge to develop

### Workflow

```
feature/new-feature → PR → develop → PR → main
     ↓                      ↓               ↓
   Tests                 Staging        Production
```

## Performance

### Current Metrics

| Job | Duration | Cacheable |
|-----|----------|-----------|
| Test | ~30s | ✅ pip cache |
| Security Scan | ~1-2min | ❌ |
| Build | ~2-5min | ✅ Docker cache |
| Scan Image | ~1-2min | ❌ |

### Optimization Tips

1. **Pip Cache**: Enabled via `cache: 'pip'`
2. **Docker Cache**: Uses GitHub Actions cache
3. **Parallel Jobs**: Tests and security run in parallel
4. **Skip on Draft**: Add `if: github.event.pull_request.draft == false` to skip draft PRs

## Troubleshooting

### Tests Fail in CI but Pass Locally

1. Check environment variables match
2. Verify Python version (CI uses 3.11)
3. Check for missing dependencies in `requirements.txt`
4. Review test logs in Actions tab

### Docker Build Fails

1. Check Dockerfile syntax
2. Verify base image is accessible
3. Check for networking issues
4. Review build logs for specific errors

### Security Scan False Positives

1. Review Trivy results in Security tab
2. Add exceptions to `.trivyignore` if needed
3. Update vulnerable dependencies

### Coverage Drops Below Threshold

1. Add tests for new code
2. Review coverage report in Codecov
3. Check for untested edge cases

## Best Practices

✅ **DO**:
- Run tests locally before pushing
- Keep test coverage above 80%
- Fix security vulnerabilities promptly
- Tag releases semantically (v1.0.0)
- Write descriptive commit messages

❌ **DON'T**:
- Push directly to main (use PRs)
- Commit secrets or API keys
- Ignore security scan warnings
- Skip tests on "working" features
- Disable required status checks

## Future Enhancements

### Planned Features

- [ ] Integration tests with real PostgreSQL
- [ ] Load testing with Locust
- [ ] API contract testing
- [ ] Automated changelog generation
- [ ] Semantic versioning automation
- [ ] Blue/green deployments
- [ ] Canary releases
- [ ] Automated rollbacks
- [ ] Performance benchmarking
- [ ] Dependency update automation (Dependabot)

## Support

For issues with the CI/CD pipeline:
1. Check workflow logs in Actions tab
2. Review this guide
3. Check recent commits for changes
4. Open an issue with workflow run link

---

**Last Updated**: October 2025  
**Pipeline Version**: 2.0  
**Status**: ✅ Production Ready
