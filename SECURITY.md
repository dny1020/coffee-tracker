# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the maintainers. You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
- **Full paths of source file(s)** related to the vulnerability
- **Location of the affected source code** (tag/branch/commit or direct URL)
- **Step-by-step instructions to reproduce** the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the vulnerability** and how an attacker might exploit it

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Updates**: We'll keep you informed about the progress
- **Fix Timeline**: We aim to release a fix within 30 days for critical issues
- **Credit**: We'll credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Deployment

### API Key Management

- **Never use the default API key** in production
- Generate a strong, random API key:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Store API keys in environment variables or a secrets management system
- Rotate API keys regularly (every 90 days recommended)

### HTTPS/TLS

- **Always use HTTPS** in production
- Use a reverse proxy (nginx, Caddy) with TLS termination
- Example nginx configuration:
  ```nginx
  server {
      listen 443 ssl http2;
      server_name your-domain.com;
      
      ssl_certificate /path/to/cert.pem;
      ssl_certificate_key /path/to/key.pem;
      
      location / {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

### Database Security

- Use **strong PostgreSQL passwords**
- Don't expose PostgreSQL port (5432) to the internet
- Keep PostgreSQL inside Docker network
- Regular backups with `make backup`
- Enable PostgreSQL SSL for production

### Container Security

- Container runs as **non-root user** (appuser:appuser)
- Keep base images updated
- Scan images for vulnerabilities:
  ```bash
  docker scan ghcr.io/dny1020/coffee-tracker:latest
  ```
- Use minimal base images (Alpine Linux)

### Rate Limiting

- Configured rate limits protect against abuse
- Adjust limits based on your use case in `app/routers/`
- Monitor rate limit hits via Prometheus metrics

### CORS Configuration

- Set `CORS_ORIGINS` to your specific frontend domains
- Don't use `*` (allow all) in production
- Example:
  ```env
  CORS_ORIGINS=https://your-frontend.com,https://app.your-domain.com
  ```

### Input Validation

- All inputs are validated via Pydantic models
- Custom validators enforce medical ranges
- Text fields are sanitized to remove control characters

### Security Headers

Enabled by default:
- `Content-Security-Policy: default-src 'none'`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`

### Monitoring

- Monitor `/health` endpoint for service status
- Set up alerts for:
  - High error rates (>5%)
  - Slow response times (>1s)
  - Database connection failures
  - Redis connection failures
- Review logs regularly for suspicious activity

### Environment Variables

**Never commit these to version control:**
- API_KEY
- DATABASE_URL (with real passwords)
- POSTGRES_PASSWORD
- Any secrets or credentials

**Always use**:
- `.gitignore` to exclude `.env` files
- Secrets management systems (AWS Secrets Manager, Vault, etc.)
- Environment-specific configurations

### Updates and Patching

- Keep dependencies updated
- Monitor GitHub Security Advisories
- Run `pip list --outdated` regularly
- Test updates in staging before production

### Access Control

- Limit who can access production servers
- Use SSH keys, not passwords
- Implement 2FA for GitHub and cloud providers
- Principle of least privilege for all access

### Backup and Recovery

- Regular automated backups (cron job)
- Test restore procedures
- Store backups securely (encrypted, off-site)
- Document disaster recovery process

## Known Security Considerations

### Current Implementation

1. **Authentication**: Single API key (Bearer token)
   - Suitable for personal/small team use
   - Consider OAuth2 for multi-user scenarios

2. **Rate Limiting**: IP + API key based
   - Prevents abuse
   - Can be bypassed by distributed attacks (consider Cloudflare)

3. **Database**: PostgreSQL with psycopg2
   - ORM prevents SQL injection
   - Connection pooling limits resource exhaustion

4. **Logging**: Includes request/response data
   - Review logs for sensitive data exposure
   - Consider log rotation and retention policies

## Security Checklist for Production

- [ ] Changed default API key to strong random value
- [ ] Configured HTTPS/TLS with valid certificate
- [ ] Set CORS_ORIGINS to specific domains (not `*`)
- [ ] Configured ALLOWED_HOSTS appropriately
- [ ] Strong PostgreSQL password
- [ ] PostgreSQL not exposed to internet
- [ ] Regular automated backups configured
- [ ] Monitoring and alerting configured
- [ ] Security headers enabled
- [ ] Container runs as non-root user
- [ ] Dependencies up to date
- [ ] Rate limits configured appropriately
- [ ] Logs reviewed regularly
- [ ] Incident response plan documented

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

## Contact

For security concerns, contact the maintainers directly rather than opening a public issue.

---

**Remember**: Security is an ongoing process, not a one-time setup. Stay vigilant and keep everything updated.
