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
        return bool(self.is_admin)  # 移除 debug 日誌

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
    slug = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"

    def generate_slug(self):
        """Generate a URL friendly slug from the title."""
        # Convert title to lowercase and replace spaces with hyphens
        base_slug = '-'.join(word.lower() for word in self.title.split() if word.isalnum())
        slug = base_slug
        counter = 1
        
        # Check for existing slugs and add number if needed
        while Post.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug

    def save(self):
        if not self.slug:
            self.slug = self.generate_slug()
        db.session.add(self)
        db.session.commit()

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # 增加長度從30到100
    
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

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_setting(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set_setting(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    @classmethod
    def get_blog_settings(cls):
        """Get all blog settings as a dict"""
        return {
            'blog_name': cls.get_setting('blog_name', 'JasonCrypto\'s Blog'),
            'logo_path': cls.get_setting('logo_path', 'img/logo.png'),
            'ga_tracking_id': cls.get_setting('ga_tracking_id', ''),
            'footer_about': cls.get_setting('footer_about', 'Exploring the intersection of security, AI, and blockchain technology.'),
            'github_url': cls.get_setting('github_url', ''),
            'twitter_url': cls.get_setting('twitter_url', ''),
            'cake_url': cls.get_setting('cake_url', ''),
            'instagram_url': cls.get_setting('instagram_url', ''),
            'email': cls.get_setting('email', '')
        }
