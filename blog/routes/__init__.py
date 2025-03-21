from flask import Blueprint

# Import blueprints 
from .auth import auth_bp
from .posts import post_bp
from .admin import admin_bp
from .uploads import upload_bp
from .pages import pages_bp

def init_app(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(upload_bp)
    app.register_blueprint(pages_bp)  # 註冊 pages_bp，不需要 url_prefix
