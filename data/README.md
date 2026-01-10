# Data Directory

This directory contains persistent data for all services using **local bind mounts** instead of Docker named volumes.

## Why Local Bind Mounts?

✅ **Data survives** `docker-compose down -v`  
✅ **Easy backups** - just copy the `data/` folder  
✅ **Visible files** - inspect data without Docker commands  
✅ **Portable** - works across different systems  

## Directory Structure

```
data/
├── postgres/      # PostgreSQL database files
└── redis/         # Redis persistence (AOF/RDB files)
```

## Permissions

Some services require specific user IDs:
- **PostgreSQL**: UID 999, GID 999 (postgres user)
- **Redis**: UID 999, GID 999 (redis user)

**IMPORTANT**: After creating the directories, you MUST set the correct permissions:

```bash
sudo chown -R 999:999 data/postgres
sudo chown -R 999:999 data/redis
```

If you encounter permission errors, run the commands above.

## Backup

### Quick Backup
```bash
# From project root
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### Restore from Backup
```bash
# Stop services first
docker-compose down

# Extract backup
tar -xzf backup-20251016.tar.gz

# Restart services
docker-compose up -d
```

## Migration from Docker Volumes

If you previously used Docker named volumes, migrate with:

```bash
# Stop services (keeps volumes)
docker-compose down

# Create directories
mkdir -p data/postgres data/redis

# Copy data from Docker volumes
docker run --rm -v coffee-tracker_pg_data:/source -v $(pwd)/data/postgres:/dest alpine sh -c "cp -a /source/. /dest/"
docker run --rm -v coffee-tracker_redis_data:/source -v $(pwd)/data/redis:/dest alpine sh -c "cp -a /source/. /dest/"

# Fix permissions
sudo chown -R 999:999 data/postgres
sudo chown -R 999:999 data/redis

# Start services
docker-compose up -d
```

## Important Notes

⚠️ **Do NOT commit data files to git** - they are ignored in `.gitignore`  
⚠️ **Backup regularly** - especially before major upgrades  

## Cleanup

To start fresh (⚠️ DELETES ALL DATA):
```bash
docker-compose down
rm -rf data/postgres/* data/redis/*
docker-compose up -d
```
