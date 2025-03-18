import click
from flask.cli import with_appcontext
from . import db, create_app
from .models import User, Post, Comment, Tag

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db_command)
