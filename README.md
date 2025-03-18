# JasonCrypto's Blog

A Flask-based blog system focused on cybersecurity, AI, and blockchain technology.

## Features

- 🔐 User Authentication & Authorization
- 📝 Rich Text Editor with Image Upload
- 🏷️ Tag and Category System
- 🌓 Light/Dark Theme Toggle
- 📱 Responsive Design
- 💾 MySQL Database Support
- 🔒 CSRF Protection
- 🚫 Rate Limiting
- 🖼️ Image Upload & Management

## Technology Stack

- **Backend**: Flask
- **Database**: MySQL
- **Frontend**: Bootstrap 5, Quill.js
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Rate Limiting**: Flask-Limiter

## Installation

### Linux Environment

1. System dependencies

docker install(ubuntu):https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config

# CentOS/RHEL
sudo dnf update
sudo dnf install -y python3-devel mysql-devel gcc
```

2. Clone repository and setup

```bash
# Clone repository
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Deployment (Linux)

1. Create docker-compose.yml:

```yaml
version: "3.8"
services:
  mysql:
    image: mysql:8.0
    container_name: blog-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: blog_db
      MYSQL_USER: blog_user
      MYSQL_PASSWORD: your_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  web:
    build: .
    container_name: blog-web
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_USER=blog_user
      - MYSQL_PASSWORD=your_password
      - MYSQL_DATABASE=blog_db
    ports:
      - "5000:5000"
    volumes:
      - ./blog/static/uploads:/app/blog/static/uploads
    depends_on:
      - mysql
    restart: unless-stopped

volumes:
  mysql_data:
```

2. Create Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config && \
    pip install -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .
CMD ["flask", "run", "--host=0.0.0.0"]
```

3. Deploy with Docker Compose:

```bash
# Build and start containers
docker compose up -d

# Initialize database
docker compose exec web flask db upgrade
docker compose exec web python create_admin_user.py

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Production Deployment (Linux)

1. Install and configure Nginx:

```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/blog
```

2. Nginx configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/your/blog/static;
    }
}
```

3. Setup Gunicorn service:

```bash
sudo vim /etc/systemd/system/blog.service
```

```ini
[Unit]
Description=Blog Gunicorn Daemon
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/blog
Environment="PATH=/path/to/blog/venv/bin"
ExecStart=/path/to/blog/venv/bin/gunicorn --workers 3 --bind unix:blog.sock -m 007 blog:app

[Install]
WantedBy=multi-user.target
```

4. Start services:

```bash
sudo systemctl start blog
sudo systemctl enable blog
sudo systemctl restart nginx
```

## MySQL Setup

### Option 1: Using Docker (Recommended)

1. Install Docker from [https://www.docker.com/](https://www.docker.com/)

2. Pull MySQL image:

```bash
docker pull mysql:8.0
```

3. Run MySQL container:

```bash
docker run --name mysql-blog \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=blog_db \
  -e MYSQL_USER=blog_user \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 \
  -d mysql:8.0
```

4. Check container status:

```bash
# Check if container is running
docker ps

# View container logs if needed
docker logs mysql-blog
```

5. Access MySQL shell (optional):

```bash
docker exec -it mysql-blog mysql -u blog_user -p
```

6. Stop and start container:

```bash
# Stop container
docker stop mysql-blog

# Start container
docker start mysql-blog
```

### Option 2: Local Installation

1. Download MySQL from [https://dev.mysql.com/downloads/](https://dev.mysql.com/downloads/)
2. Install MySQL Server and MySQL Workbench
3. Create database and user:

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'blog_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'localhost';
FLUSH PRIVILEGES;
```

5. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database credentials and secret key(CSRF) or you can dynamic create
```

6. Initialize database

```bash
flask db upgrade
python create_admin_user.py
```

7. Run the application

```bash
flask run
```

### Deployment Options

1. Using Docker (Recommended):

```bash
# Build and run with Docker Compose
docker-compose up -d

# Initialize database
docker-compose exec web flask db upgrade
docker-compose exec web python create_admin_user.py
```

2. Direct System Installation:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 3 blog:app
```

## Quick Start

1. System requirements:

```bash
# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```

2. Clone and setup:

```bash
# Clone repository
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog

# Setup credentials (MySQL password, admin account, etc.)
python setup_credentials.py
```

3. Start the application:

```bash
# Build and start containers
docker-compose up -d

# Wait for MySQL to be ready (check logs)
docker-compose logs mysql

# Initialize database and create admin
docker-compose exec web flask db upgrade
docker-compose exec web python create_admin_user.py
```

4. Access the application:

- Visit http://localhost:5000
- Login with the admin credentials you set during setup

### Security Settings

```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow 5000
sudo ufw enable
```
