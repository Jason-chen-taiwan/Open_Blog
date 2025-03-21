FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    dos2unix \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create upload directories and set permissions
RUN mkdir -p blog/static/uploads blog/static/img && \
    chmod -R 755 blog/static/uploads && \
    chmod -R 755 blog/static/img

# Set environment variables
ENV FLASK_APP=blog.app \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# Convert line endings and set permissions
RUN find . -type f -name "*.sh" -exec dos2unix {} \; && \
    find . -type f -name "*.sh" -exec chmod +x {} \; && \
    chmod +x docker-entrypoint.sh && \
    chown -R root:root .

EXPOSE 5000

ENTRYPOINT ["bash", "/app/docker-entrypoint.sh"]
