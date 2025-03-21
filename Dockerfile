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

# Set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    dos2unix /usr/local/bin/docker-entrypoint.sh

# Download and set up wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh && \
    dos2unix /usr/local/bin/wait-for-it.sh

EXPOSE 5000

# Change ENTRYPOINT to use the script from /usr/local/bin
ENTRYPOINT ["docker-entrypoint.sh"]
