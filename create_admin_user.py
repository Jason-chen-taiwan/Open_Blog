import os
from blog import create_app, db
from blog.models import User
import secrets
import string

def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_admin():
    app = create_app()
    with app.app_context():
        # Get admin credentials from environment variables
        default_admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        default_admin_password = os.environ.get('ADMIN_PASSWORD') or generate_password()
        
        # Check if admin exists
        admin = User.query.filter_by(email=default_admin_email).first()
        if not admin:
            admin = User(email=default_admin_email, is_admin=True)
            admin.set_password(default_admin_password)
            db.session.add(admin)
            db.session.commit()
            print("\n" + "="*50)
            print("ADMIN ACCOUNT CREATED")
            print("="*50)
            print(f"Email: {default_admin_email}")
            print(f"Password: {default_admin_password}")
            print("="*50 + "\n")
        else:
            # Only update password if ADMIN_PASSWORD is explicitly set
            if os.environ.get('ADMIN_PASSWORD'):
                admin.set_password(default_admin_password)
                db.session.commit()
                print("\n" + "="*50)
                print("ADMIN PASSWORD UPDATED")
                print("="*50)
                print(f"Email: {default_admin_email}")
                print(f"Password: {default_admin_password}")
                print("="*50 + "\n")

if __name__ == '__main__':
    create_admin()
