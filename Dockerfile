FROM python:3.12-alpine

WORKDIR /app

# Install system dependencies including Postgres client libs for psycopg2
RUN apk add --no-cache gcc musl-dev curl libpq postgresql-dev

# Copy requirements first for caching
COPY requirements.txt ./


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/
COPY .env.example ./
# Copy pytest.ini only if exists (handled at build context level)
COPY pytest.ini ./pytest.ini

# Create data directory with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
