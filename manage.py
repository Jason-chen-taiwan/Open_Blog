from flask.cli import FlaskGroup
from blog import create_app, db
from blog.models import User, Post, Comment, Tag
from create_admin_user import create_admin

cli = FlaskGroup(create_app=create_app)

@cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Initialized the database.')

@cli.command("init-admin")
def init_admin():
    """Initialize admin account with random password."""
    create_admin()

if __name__ == "__main__":
    cli()
