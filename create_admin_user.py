from blog import create_app, db
from blog.models import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='your_email').first()
        if not admin:
            # Create new admin user
            admin = User(email='your_email', is_admin=True)  
            admin.set_password('yourpassword')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            # Update existing user to admin role if needed
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print("Existing user updated to admin role")
            else:
                print("Admin user already exists")

if __name__ == '__main__':
    create_admin()
