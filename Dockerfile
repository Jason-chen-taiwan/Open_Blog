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

# Download wait-for-it script and set permissions
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh && \
    dos2unix /wait-for-it.sh

# Convert line endings and set permissions for entrypoint
RUN dos2unix docker-entrypoint.sh && \
    chmod +x docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
