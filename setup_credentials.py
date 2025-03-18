import os
import secrets
import string
import yaml

def generate_secret_key():
    """Generate a secure secret key."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def setup_credentials():
    """Setup all necessary credentials."""
    print("Setting up credentials for the blog application...")
    
    # Get MySQL credentials
    mysql_password = input("Enter MySQL password (leave blank for 'yourpassword'): ").strip()
    mysql_password = mysql_password or 'yourpassword'
    
    # Get admin credentials
    admin_email = input("Enter admin email (leave blank for 'admin@example.com'): ").strip()
    admin_email = admin_email or 'admin@example.com'
    
    admin_password = input("Enter admin password (leave blank for 'yourpassword'): ").strip()
    admin_password = admin_password or 'yourpassword'
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Read docker-compose.yml
    with open('docker-compose.yml', 'r') as f:
        docker_compose = yaml.safe_load(f)
    
    # Update MySQL password
    docker_compose['services']['mysql']['environment']['MYSQL_PASSWORD'] = mysql_password
    docker_compose['services']['web']['environment'] = [
        f'MYSQL_HOST=mysql',
        f'MYSQL_USER=blog_user',
        f'MYSQL_PASSWORD={mysql_password}',
        f'MYSQL_DATABASE=blog_db',
        f'SECRET_KEY={secret_key}'
    ]
    
    # Write updated docker-compose.yml
    with open('docker-compose.yml', 'w') as f:
        yaml.dump(docker_compose, f, default_flow_style=False)
    
    # Update create_admin_user.py
    admin_content = f"""from blog import create_app, db

from blog.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='{admin_email}').first()
        if not admin:
            # Create new admin user
            admin = User(email='{admin_email}', is_admin=True)
            admin.set_password('{admin_password}')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            # Update existing user admin role and password
            admin.is_admin = True
            admin.set_password('{admin_password}')
            db.session.commit()
            print("Admin user updated successfully")

if __name__ == '__main__':
    create_admin()
"""
    
    with open('create_admin_user.py', 'w') as f:
        f.write(admin_content)
    
    print("\nCredentials setup completed!")
    print(f"Admin Email: {admin_email}")
    print("Configuration saved to docker-compose.yml and create_admin_user.py")
    print("\nYou can now run:")
    print("1. docker compose up -d")
    print("2. docker compose exec web flask db upgrade")

if __name__ == "__main__":
    setup_credentials()
