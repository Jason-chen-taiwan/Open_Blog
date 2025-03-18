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

## 🚀 Quick Start Guide

1. 克隆專案並進入目錄：

```bash
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog
```

2. 設置環境變數：

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯環境變數 (可選，使用預設值也可以)
nano .env
```

3. 啟動服務：

```bash
# 使用 Docker Compose 啟動所有服務 (MySQL + Web 應用)
docker compose up -d

# 等待服務就緒（觀察日誌）
docker compose logs -f
```

4. 檢查管理員帳號：

```bash
# 查看管理員帳號資訊
docker compose logs web | grep "Admin Account"
```

5. 訪問應用：

- 網址：http://localhost:5000
- 預設管理員郵箱：admin@example.com
- 密碼：從上一步的日誌中獲取

### 🔧 常用維護指令

```bash
# 查看服務狀態
docker compose ps

# 重新啟動服務
docker compose restart

# 停止服務
docker compose down

# 查看日誌
docker compose logs blog-web    # 查看網站日誌
docker compose logs blog-mysql  # 查看資料庫日誌

# 備份數據庫
docker compose exec blog-mysql mysqldump -u blog_user -p blog_db > backup.sql

# 進入數據庫命令行
docker compose exec blog-mysql mysql -u blog_user -p blog_db
```

### 🆘 故障排除

1. 如果網站無法訪問：

```bash
# 檢查容器狀態
docker compose ps

# 檢查網站日誌
docker compose logs blog-web
```

2. 如果數據庫連接失敗：

```bash
# 檢查數據庫狀態
docker compose logs blog-mysql

# 重啟數據庫
docker compose restart blog-mysql
```

## Installation (not docker)

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

1. Clone and setup:

```bash
# Clone repository
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog
```

2. Configure credentials:

```bash
# Copy example env file
cp .env.example .env

# Generate credentials (optional - can use environment variables instead)
python setup_credentials.py
```

3. Build and start with Docker:

```bash
# Start services with auto-generated admin password
docker compose up -d

# Or start with custom admin password
ADMIN_PASSWORD=your-secure-password docker compose up -d

# Check logs for admin credentials
docker compose logs web | grep "Admin Account"
```

4. Access the application:

- Frontend: http://localhost:5000
- Default admin email: admin@example.com
- Password: Check the docker logs or use your custom password

## Development Setup

1. Install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Setup database:

```bash
# Start MySQL
docker compose up -d mysql

# Initialize database
flask db upgrade
flask init-admin
```

3. Run development server:

```bash
flask run --debug
```

## Deployment Options

### Docker Deployment (Recommended)

1. Configure environment variables (optional):

```bash
# .env file
ADMIN_EMAIL=custom@example.com
ADMIN_PASSWORD=secure-password
MYSQL_PASSWORD=database-password
SECRET_KEY=your-secret-key
```

2. Deploy with Docker Compose:

```bash
# Pull images and build
docker compose pull
docker compose build

# Start services
docker compose up -d

# Check logs
docker compose logs -f
```

3. Management commands:

```bash
# Restart services
docker compose restart

# View logs
docker compose logs web
docker compose logs mysql

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Production Deployment

1. System dependencies:

```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

2. Setup SSL with Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com
```

3. Configure Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. Deploy application:

```bash
# Clone and setup
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog

# Configure environment
cp .env.example .env
nano .env  # Edit environment variables

# Deploy with Docker
docker compose -f docker-compose.prod.yml up -d
```

5. Setup automatic updates:

```bash
# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
cd /path/to/blog
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --build
EOF

chmod +x update.sh

# Add to crontab
echo "0 4 * * * /path/to/update.sh > /var/log/blog-update.log 2>&1" | crontab -
```

### Security Settings

```bash
# Allow only necessary ports
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow 5000
sudo ufw enable
```
