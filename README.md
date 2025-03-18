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

1. Clone the repository

```bash
git clone https://github.com/Jason-chen-taiwan/blog.git
cd blog
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

## MySQL Setup

### Option 1: Using Docker (Recommended)

1. Install Docker from [https://www.docker.com/](https://www.docker.com/)

2. Run MySQL container:

```bash
docker run --name mysql-blog \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=blog_db \
  -e MYSQL_USER=blog_user \
  -e MYSQL_PASSWORD=your_password \
  -p 3306:3306 \
  -d mysql:8.0
```

3. Check container status:

```bash
docker ps
```

4. Access MySQL shell (optional):

```bash
docker exec -it mysql-blog mysql -u blog_user -p
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
