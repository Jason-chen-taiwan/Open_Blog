from datetime import datetime
from blog import db
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Replace role field
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', admin={self.is_admin or False})"

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def verify_password(self, password):
        """Verify the password hash matches."""
        try:
            return bcrypt.check_password_hash(self.password_hash, password)
        except:
            return False

    @property
    def is_administrator(self):
        """Helper property to check admin status"""
        is_admin = bool(self.is_admin)
        print(f"Checking admin status for {self.email}: {is_admin}")  # Debug log
        return is_admin

# Association table for many-to-many relationship between Post and Tag
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)  # 改為可為空
    category = db.relationship('Category', backref='posts')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy=True))
    image_path = db.Column(db.String(255), nullable=True)
    html_content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Tag {self.name}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.content[:20]}', '{self.created_at}')"
