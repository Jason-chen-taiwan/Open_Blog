import click
from flask.cli import with_appcontext
from . import db, create_app
from .models import User, Post, Comment, Tag
from create_admin_user import create_admin  # 新增這一行

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

@click.command('init-admin')  # 新增這個命令
@with_appcontext
def init_admin_command():
    """Initialize admin account."""
    create_admin()
    
def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_admin_command)  # 註冊新命令
