# GitHub Secrets Setup

To enable CI/CD pipeline, you need to configure these secrets in your GitHub repository.

## Required Secrets

Go to `Settings` → `Secrets and variables` → `Actions` in your GitHub repository and add:

### 1. Production API Key
```
Name: PRODUCTION_API_KEY
Value: your-super-secret-production-api-key-here
Description: API key for production environment
```

### 2. SSH Private Key (if deploying to VPS)
```
Name: SSH_PRIVATE_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
       [your private key content]
       -----END OPENSSH PRIVATE KEY-----
Description: SSH key for server access
```

### 3. Server Configuration (if deploying to VPS)
```
Name: SERVER_HOST
Value: your-server.com
Description: Production server hostname

Name: SERVER_USER
Value: deploy
Description: SSH username for deployment

Name: SERVER_PATH
Value: /var/www/coffee-tracker
Description: Deployment path on server
```

### 4. Notification Webhooks (optional)
```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/...
Description: Slack webhook for deployment notifications

Name: DISCORD_WEBHOOK_URL
Value: https://discord.com/api/webhooks/...
Description: Discord webhook for notifications
```

## Environment-Specific Secrets

### Production Environment
In `Settings` → `Environments` → `production`:
```
API_KEY: your-production-api-key
CORS_ORIGINS: https://your-domain.com,https://www.your-domain.com
ALLOWED_HOSTS: your-domain.com,www.your-domain.com
DATABASE_URL: sqlite:///data/coffee.db (or your production DB)
```

### Staging Environment  
In `Settings` → `Environments` → `staging`:
```
API_KEY: your-staging-api-key
CORS_ORIGINS: https://staging.your-domain.com
ALLOWED_HOSTS: staging.your-domain.com
DATABASE_URL: sqlite:///data/coffee.db
```

## GitHub Container Registry Setup

The pipeline automatically pushes to GitHub Container Registry (ghcr.io). Make sure:

1. **Enable GitHub Packages** in repository settings
2. **Set repository visibility** appropriately:
   - Public repo → images are public
   - Private repo → images are private
3. **GITHUB_TOKEN** is automatically provided (no setup needed)

## Image URLs

After successful build, your images will be available at:
```
ghcr.io/your-username/coffee-tracker:latest
ghcr.io/your-username/coffee-tracker:main-abc123
ghcr.io/your-username/coffee-tracker:develop-xyz789
```

## Manual Testing

Test the CI/CD pipeline:

```bash
# 1. Push to develop branch (triggers staging deployment)
git checkout -b develop
git push origin develop

# 2. Push to main branch (triggers production deployment)  
git checkout main
git merge develop
git push origin main

# 3. Check GitHub Actions tab for pipeline status
# 4. Verify images in Packages section of your repo
```

## Local Testing with GitHub Image

```bash
# Pull and run the built image locally
docker pull ghcr.io/your-username/coffee-tracker:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e API_KEY=test-key \
  -e DATABASE_URL=sqlite:///data/coffee.db \
  ghcr.io/your-username/coffee-tracker:latest
```

## Troubleshooting

### Pipeline Fails at Build Step
- Check Dockerfile syntax
- Verify all requirements.txt dependencies
- Ensure tests pass locally first

### Can't Push to Registry
- Check repository permissions
- Verify GITHUB_TOKEN has package write permissions
- Ensure image name matches repository name

### Deployment Fails
- Verify all secrets are set correctly
- Check server SSH access
- Validate environment file syntax

### Image Pull Fails
- Check image visibility settings
- Verify image tag exists
- Authenticate: `docker login ghcr.io -u username`