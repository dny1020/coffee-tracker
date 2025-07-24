FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini ./

# Create data directory
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]