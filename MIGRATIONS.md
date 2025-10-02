# Database Migration Guide

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

## Quick Start

### 1. Initialize Alembic (First Time Only)

```bash
# Install Alembic
pip install alembic

# Or use make command
make install-dev

# Initialize Alembic
alembic init migrations
```

### 2. Configure Alembic

Edit `alembic.ini` and update the database URL:

```ini
# Replace this line:
sqlalchemy.url = driver://user:pass@localhost/dbname

# With your database URL (or use env var):
sqlalchemy.url = postgresql+psycopg2://coffee:coffee_password@localhost:5432/coffee_db
```

Or better yet, modify `migrations/env.py` to read from environment:

```python
from app.settings import settings

config.set_main_option('sqlalchemy.url', settings.database_url)
```

### 3. Update env.py for Auto-generation

Edit `migrations/env.py` to import your models:

```python
# Add these imports at the top
from app.models import Base
from app.settings import settings

# Update target_metadata
target_metadata = Base.metadata

# Update run_migrations_online() to use settings
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        pooling=False,
    )
    
    # Override URL from environment
    connectable = create_engine(settings.database_url)
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

## Creating Migrations

### Auto-generate Migration from Model Changes

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user table"

# Or use make command
make migrate
```

### Create Empty Migration (Manual)

```bash
alembic revision -m "Custom migration"
```

## Applying Migrations

### Upgrade to Latest Version

```bash
# Apply all pending migrations
alembic upgrade head

# Or use make command
make upgrade-db
```

### Upgrade to Specific Version

```bash
alembic upgrade <revision_id>
```

### Downgrade

```bash
# Rollback one migration
alembic downgrade -1

# Or use make command
make downgrade-db

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

## Migration History

### View Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

### View Pending Migrations

```bash
alembic history --verbose
```

## Common Migration Scenarios

### Adding a New Column

```python
# migrations/versions/xxx_add_user_column.py
def upgrade():
    op.add_column('coffee_logs', 
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

def downgrade():
    op.drop_column('coffee_logs', 'user_id')
```

### Adding an Index

```python
def upgrade():
    op.create_index(
        'ix_coffee_logs_user_id', 
        'coffee_logs', 
        ['user_id']
    )

def downgrade():
    op.drop_index('ix_coffee_logs_user_id', table_name='coffee_logs')
```

### Adding a Foreign Key

```python
def upgrade():
    op.add_column('coffee_logs', 
        sa.Column('user_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        'fk_coffee_logs_user_id',
        'coffee_logs', 'users',
        ['user_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_coffee_logs_user_id', 'coffee_logs', type_='foreignkey')
    op.drop_column('coffee_logs', 'user_id')
```

### Renaming a Column

```python
def upgrade():
    op.alter_column('coffee_logs', 'coffee_type',
                    new_column_name='beverage_type')

def downgrade():
    op.alter_column('coffee_logs', 'beverage_type',
                    new_column_name='coffee_type')
```

## Production Migration Strategy

### Pre-deployment Checklist

1. **Test migrations on a copy of production data**
```bash
# Dump production data
pg_dump -U coffee coffee_db > prod_backup.sql

# Restore to test database
psql -U coffee coffee_db_test < prod_backup.sql

# Test migration on test database
DATABASE_URL=postgresql://coffee:pass@localhost/coffee_db_test alembic upgrade head
```

2. **Create backup before migration**
```bash
make backup
```

3. **Review migration SQL**
```bash
alembic upgrade head --sql > migration.sql
# Review the SQL before applying
```

### Zero-Downtime Migrations

For production systems requiring zero downtime:

1. **Adding Columns**: Add as nullable first
```python
# Migration 1: Add column as nullable
op.add_column('coffee_logs', sa.Column('new_field', sa.String(), nullable=True))

# Deploy code that handles both null and non-null values

# Migration 2: Populate data
op.execute("UPDATE coffee_logs SET new_field = 'default' WHERE new_field IS NULL")

# Migration 3: Make non-nullable
op.alter_column('coffee_logs', 'new_field', nullable=False)
```

2. **Removing Columns**: Remove from code first, then database
```python
# 1. Deploy code that doesn't use the column
# 2. Wait for deployment
# 3. Then run migration to drop column
op.drop_column('coffee_logs', 'old_field')
```

3. **Renaming Columns**: Use a multi-step process
```python
# Migration 1: Add new column
op.add_column('coffee_logs', sa.Column('new_name', sa.String(), nullable=True))

# Migration 2: Copy data
op.execute("UPDATE coffee_logs SET new_name = old_name")

# Deploy code that reads from new_name but writes to both

# Migration 3: Drop old column
op.drop_column('coffee_logs', 'old_name')
```

## Docker Integration

### Running Migrations in Docker

```bash
# Enter the container
docker-compose exec coffee-tracker sh

# Run migrations
alembic upgrade head

# Exit
exit
```

### Automatic Migrations on Startup

Add to `docker-compose.yml`:

```yaml
coffee-tracker:
  command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

Or create a startup script `start.sh`:

```bash
#!/bin/sh
set -e

# Run migrations
alembic upgrade head

# Start application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
alembic current

# Check history
alembic history

# Stamp database with current version
alembic stamp head
```

### "Can't locate revision identified by"

```bash
# This usually means the migration was deleted
# Stamp the database with an earlier known revision
alembic stamp <last_known_revision>
```

### Merge Conflicts in Migration Files

```bash
# If two developers created migrations, merge them
alembic merge -m "Merge migrations" <rev1> <rev2>
```

### Reset Everything (Development Only)

```bash
# WARNING: This will delete all data!
make clean
make up

# Or manually:
docker-compose down -v
docker-compose up -d

# Database will be recreated with latest schema
```

## Best Practices

1. **Always review auto-generated migrations** - They may not be perfect
2. **Test migrations both up and down** - Ensure rollback works
3. **One logical change per migration** - Easier to understand and rollback
4. **Add comments to complex migrations** - Explain the "why"
5. **Keep migrations small and focused** - Easier to debug
6. **Never edit applied migrations** - Create a new one instead
7. **Back up before production migrations** - Safety first
8. **Use transactions** - Alembic does this by default, don't disable
9. **Version control all migrations** - Commit to git
10. **Document breaking changes** - In migration docstring and CHANGELOG

## Migration Template

```python
"""<Brief description of what this migration does>

Revision ID: <auto-generated>
Revises: <previous_revision>
Create Date: <timestamp>

Notes:
- <Any important notes about this migration>
- <Breaking changes>
- <Required manual steps>
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '<auto-generated>'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None


def upgrade():
    """Apply the migration."""
    # Your upgrade code here
    pass


def downgrade():
    """Rollback the migration."""
    # Your downgrade code here
    pass
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
