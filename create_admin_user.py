import os
import sys
from blog import create_app, db
from blog.models import User
import secrets
import string

def generate_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_admin():
    try:
        app = create_app()
        with app.app_context():
            # Get admin credentials from environment variables
            default_admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            default_admin_password = os.environ.get('ADMIN_PASSWORD') or generate_password()
            
            # 確保輸出到 stderr
            def log_message(msg):
                print(msg, file=sys.stderr, flush=True)
            
            log_message("\n" + "="*50)
            log_message("ADMIN ACCOUNT INFORMATION")
            log_message("="*50)
            
            # Check if admin exists
            admin = User.query.filter_by(email=default_admin_email).first()
            if not admin:
                admin = User(email=default_admin_email, is_admin=True)
                admin.set_password(default_admin_password)
                db.session.add(admin)
                db.session.commit()
                log_message("NEW ADMIN ACCOUNT CREATED")
            else:
                if os.environ.get('ADMIN_PASSWORD'):
                    admin.set_password(default_admin_password)
                    db.session.commit()
                    log_message("ADMIN PASSWORD UPDATED")
                else:
                    # 即使帳號存在也重置密碼
                    new_password = generate_password()
                    admin.set_password(new_password)
                    db.session.commit()
                    default_admin_password = new_password
                    log_message("ADMIN PASSWORD RESET")

            # 總是顯示憑據
            log_message("Current Admin Credentials:")
            log_message(f"Email: {default_admin_email}")
            log_message(f"Password: {default_admin_password}")
            log_message("="*50 + "\n")
            
            return True
    except Exception as e:
        print(f"Error creating admin: {str(e)}", file=sys.stderr, flush=True)
        return False

if __name__ == '__main__':
    success = create_admin()
    if not success:
        sys.exit(1)
