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
COPY .env.example ./

# Create non-root user for security
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Create data directory with proper permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 4000

# Environment variables
ENV PYTHONPATH=/app

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
