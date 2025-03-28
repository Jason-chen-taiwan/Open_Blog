from flask import Flask, g
import logging  # 新增這行
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = None

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stderr
    )
    app.logger.setLevel(logging.INFO)
    
    # Configure app
    import os
    from urllib.parse import quote_plus

    # Required environment variables
    required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Get secret key from environment variable or use a default one
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database configuration
    DB_USER = os.environ.get('MYSQL_USER')
    DB_PASS = quote_plus(os.environ.get('MYSQL_PASSWORD', ''))
    DB_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    DB_PORT = os.environ.get('MYSQL_PORT', '3306')
    DB_NAME = os.environ.get('MYSQL_DATABASE', 'blog_db')

    # Update SQLAlchemy URI for MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Import all models before initializing migrations
    from .models import User, Post, Comment, Tag
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 修改這裡：從 'main.login' 改為 'auth.login'
    
    # Initialize Flask-Limiter
    global limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["5 per minute"],
        storage_uri="memory://"  # Changed from storage_backend
    )
    
    # Suppress storage warning in development
    app.config['RATELIMIT_STORAGE_URL'] = "memory://"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # 添加全局 before_request
    @app.before_request
    def load_settings():
        from .models import Settings
        g.blog_settings = Settings.get_blog_settings()

    # Register routes
    from .routes import init_app as init_routes
    init_routes(app)
    
    # Initialize database
    with app.app_context():
        from . import models
        db.create_all()
    
    return app
