# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features

### Authentication
- **API Key Authentication**: All data endpoints require Bearer token authentication
- **Constant-time Comparison**: API keys are compared using HMAC to prevent timing attacks
- **Key Hashing**: API keys are hashed using SHA-256 before comparison

### Input Validation
- **Caffeine Limits**: 0-1000mg range validation (configurable)
- **Heart Rate Limits**: 30-250 BPM range validation (configurable)
- **Text Length Limits**: Notes (1000 chars), Coffee Type (100 chars), Context (50 chars)
- **Input Sanitization**: Control characters and null bytes are removed from text inputs
- **Request Size Limits**: Maximum request body size of 1MB (configurable)

### Rate Limiting
- **Redis-backed**: Persistent rate limiting across container restarts
- **Per-IP + API Key**: Rate limits are applied per IP address and API key combination
- **Configurable Limits**: Different limits for different endpoint types
  - General endpoints: 30 requests/minute
  - Health check: 60 requests/minute
  - Coffee logging: 100 requests/hour
  - Heart rate logging: 200 requests/hour

### Network Security
- **CORS Protection**: Configurable allowed origins
- **Trusted Host Validation**: Prevents host header attacks
- **Security Headers**: 
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 0
  - Referrer-Policy: no-referrer
  - Content-Security-Policy: default-src 'none'

### Database Security
- **Connection Pooling**: Configured with pool_pre_ping for reliability
- **Pool Limits**: 10 base connections, 20 max overflow
- **Connection Recycling**: Connections recycled after 1 hour
- **Prepared Statements**: SQLAlchemy ORM prevents SQL injection

### Monitoring & Logging
- **Request IDs**: Every request gets a unique identifier for tracking
- **Access Logging**: All requests logged with method, path, status, duration
- **Error Logging**: Detailed error logging for debugging
- **Prometheus Metrics**: Instrumentation for monitoring system health

## Security Best Practices for Deployment

### 1. API Key Management
- [ ] Change the default API key immediately
- [ ] Use strong, randomly generated keys (32+ characters)
- [ ] Store API keys in secure secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Rotate API keys regularly (recommended: every 90 days)
- [ ] Never commit API keys to version control

### 2. HTTPS/TLS
- [ ] Deploy behind a reverse proxy (nginx, Caddy, Traefik)
- [ ] Enable HTTPS with valid TLS certificates (Let's Encrypt)
- [ ] Use TLS 1.2 or higher
- [ ] Configure HSTS headers in reverse proxy

### 3. Database Security
- [ ] Use strong database passwords
- [ ] Restrict database network access (bind to localhost or private network)
- [ ] Enable PostgreSQL SSL connections in production
- [ ] Regular database backups with encryption
- [ ] Keep database software updated

### 4. Container Security
- [ ] Run containers as non-root user
- [ ] Keep base images updated (currently Python 3.12-alpine)
- [ ] Scan images for vulnerabilities regularly
- [ ] Use read-only filesystem where possible
- [ ] Limit container resources (CPU, memory)

### 5. Network Security
- [ ] Configure firewall rules (only expose necessary ports)
- [ ] Use private networks for inter-service communication
- [ ] Configure CORS origins to match your frontend domain
- [ ] Disable metrics endpoint or require authentication
- [ ] Use VPN or IP whitelisting for admin access

### 6. Monitoring & Alerting
- [ ] Set up log aggregation (ELK, Loki, CloudWatch)
- [ ] Monitor authentication failures
- [ ] Alert on rate limit violations
- [ ] Track unusual traffic patterns
- [ ] Monitor database performance and errors

## Reporting a Vulnerability

If you discover a security vulnerability, please email security@your-domain.com.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### Response Timeline:
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

## Known Security Considerations

### Current Limitations:
1. **Single API Key**: Currently uses a single API key for all users. For multi-user scenarios, consider implementing JWT tokens or OAuth2.

2. **No Rate Limit Bypass**: Admin users cannot bypass rate limits. Consider implementing different rate limit tiers if needed.

3. **Metrics Endpoint**: The `/metrics` endpoint can be secured with API key but is not public by default. Set `METRICS_PUBLIC=true` only if running in a trusted network.

4. **No Audit Logging**: Currently no audit trail for data modifications. Consider implementing audit logging for compliance requirements.

5. **No Encryption at Rest**: Database data is not encrypted at rest by default. Enable database encryption if handling sensitive health data.

## Security Updates

### Version 1.0.0 (October 2025)
- ✅ Initial security implementation
- ✅ API key authentication with constant-time comparison
- ✅ Input validation and sanitization
- ✅ Rate limiting with Redis
- ✅ Security headers
- ✅ Connection pooling with recycling
- ✅ Database indexes for performance
- ✅ Request size limits

## Compliance Notes

### HIPAA Compliance:
This application is **NOT HIPAA compliant** out of the box. If handling Protected Health Information (PHI), additional measures are required:
- Encryption at rest and in transit
- Audit logging with immutable logs
- User authentication and authorization
- Business Associate Agreements (BAA)
- Access controls and user management

### GDPR Compliance:
For GDPR compliance, implement:
- Data deletion endpoints
- User consent management
- Data export functionality
- Privacy policy and terms of service
- Data retention policies

## Security Checklist for Production

```bash
# Run the production readiness check
make prod-check

# Verify all security configurations
- [ ] API key changed from default
- [ ] HTTPS enabled with valid certificate
- [ ] Database password changed
- [ ] Redis password set (if exposed)
- [ ] CORS origins configured correctly
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up
- [ ] Container running as non-root
- [ ] Firewall rules configured
- [ ] VPN or IP whitelisting for admin access
```

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/security.html)
