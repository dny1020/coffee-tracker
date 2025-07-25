FROM python:3.13-alpine

WORKDIR /app

# Instalar dependencias del sistema, incluyendo curl
RUN apk add --no-cache gcc musl-dev curl

# Copiar requirements primero para caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copiar código
COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini ./

# Crear directorio de datos con permisos adecuados
RUN mkdir -p /app/data && chmod 755 /app/data

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app

# Ejecutar con uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
