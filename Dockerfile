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

# Create upload directories
RUN mkdir -p blog/static/uploads blog/static/img

# Set environment variables
ENV FLASK_APP=blog.app
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Add wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it

# Convert line endings and set permissions
RUN dos2unix /usr/local/bin/wait-for-it && \
    dos2unix docker-entrypoint.sh && \
    chmod +x /usr/local/bin/wait-for-it && \
    chmod +x docker-entrypoint.sh

# Change the command to use wait script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-", "blog.app:app"]
