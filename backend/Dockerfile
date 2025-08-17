# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Azure Speech SDK
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=application.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app


# Use gunicorn for production with thread-based workers to support SSE streaming
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--worker-class", "gthread", "--threads", "8", "--timeout", "120", "application:app"]