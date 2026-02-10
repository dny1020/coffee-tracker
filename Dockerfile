FROM python:3.12-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Non-root user
RUN adduser -D -u 1001 coffeeuser && \
    mkdir -p /app/data /app/logs && \
    chown -R coffeeuser:coffeeuser /app
USER coffeeuser

EXPOSE 4000
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]
