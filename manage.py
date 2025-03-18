from flask.cli import FlaskGroup
from blog import create_app, db
from blog.models import User, Post, Comment, Tag

cli = FlaskGroup(create_app=create_app)

@cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Initialized the database.')

@cli.command("create-admin")
def create_admin():
    """Create admin user"""
    admin = User.query.filter_by(email='zwasd5123@gmail.com').first()
    if not admin:
        admin = User(email='zwasd5123@gmail.com', is_admin=True)
        admin.set_password('jas0nA1b10g')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        print("Admin user already exists")

if __name__ == "__main__":
    cli()
