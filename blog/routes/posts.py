from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, g
from flask_login import current_user, login_required
from blog import db
from blog.models import Post, Comment, Category, Tag, Settings
from datetime import datetime
from werkzeug.utils import secure_filename
import os

post_bp = Blueprint('post', __name__)

# 設定允許的檔案類型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@post_bp.before_request
def load_settings():
    g.ga_tracking_id = Settings.get_setting('ga_tracking_id')

@post_bp.route('/')
@post_bp.route('/category/<category_name>')
def home(category_name=None):
    query = Post.query
    if category_name:
        category = Category.query.filter_by(name=category_name).first_or_404()
        query = query.filter_by(category_id=category.id)
    posts = query.order_by(Post.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('home.html', 
                         posts=posts,
                         categories=categories,
                         current_category=category_name)

@post_bp.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if current_user.is_authenticated:
        current_app.logger.info(f"User {current_user.email} accessing post {post.slug}")
    return render_template('post.html', post=post)

@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_administrator:
        flash('Only administrators can create posts')
        return redirect(url_for('post.home'))

    current_app.logger.info(f'Post creation attempt by {current_user.email}')
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            category_name = request.form['category']
            tags = request.form.get('tags', '').split(',')
            
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                flash('Invalid category selected')
                return render_template('create.html', categories=categories)
            
            post = Post(
                title=title,
                content=content,
                html_content=content,
                category_id=category.id,
                user_id=current_user.id
            )
            
            # 處理圖片上傳
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                    if not os.path.exists(upload_path):
                        os.makedirs(upload_path)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    post.image_path = f"uploads/{filename}"
            
            # 處理標籤
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
            
            # 處理自定義 slug
            custom_slug = request.form.get('slug', '').strip()
            if custom_slug:
                if Post.query.filter_by(slug=custom_slug).first():
                    flash('URL already exists. Please choose another.', 'error')
                    return render_template('create.html', categories=categories)
                post.slug = custom_slug
            else:
                post.slug = post.generate_slug()
            
            db.session.add(post)
            db.session.commit()
            
            flash('Post created successfully!')
            return redirect(url_for('post.post', slug=post.slug))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash('An error occurred while creating the post', 'error')
            return render_template('create.html', categories=categories)
    
    return render_template('create.html', categories=categories)

@post_bp.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not current_user.is_administrator:
        flash('Only administrators can edit posts')
        return redirect(url_for('post.home'))
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            category_name = request.form['category']
            tags = request.form.get('tags', '').split(',')
            
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                flash('Invalid category selected')
                return redirect(url_for('post.edit', slug=post.slug))
            
            post.title = title
            post.content = content
            post.html_content = content
            post.category_id = category.id
            post.updated_at = datetime.utcnow()
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
                    if not os.path.exists(upload_path):
                        os.makedirs(upload_path)
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    post.image_path = f"uploads/{filename}"
            
            post.tags = []
            for tag_name in tags:
                tag_name = tag_name.strip()
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
            
            db.session.commit()
            
            flash('Post updated successfully!')
            return redirect(url_for('post.post', slug=post.slug))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating post: {str(e)}")
            flash('An error occurred while updating the post', 'error')
            return redirect(url_for('post.edit', slug=post.slug))
    
    current_tags = ', '.join([tag.name for tag in post.tags])
    categories = Category.query.order_by(Category.name).all()
    return render_template('edit.html', 
                         post=post,
                         categories=categories,
                         current_tags=current_tags)

@post_bp.route('/delete/<slug>', methods=['POST'])
@login_required
def delete(slug):
    if not current_user.is_administrator:
        flash('Only administrators can delete posts')
        return redirect(url_for('post.home'))
    post = Post.query.filter_by(slug=slug).first_or_404()
    current_app.logger.info(f'Post delete attempt by {current_user.email} on post {post.slug}')
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!')
    return redirect(url_for('post.home'))

@post_bp.route('/comment/<slug>', methods=['POST'])
@login_required
def comment(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    content = request.form['content']
    
    if not content:
        flash('Comment content is required!')
        return redirect(url_for('post.post', slug=post.slug))  # 修改這裡
    
    comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!')
    return redirect(url_for('post.post', slug=post.slug))  # 修改這裡

@post_bp.route('/api/posts')
def get_posts():
    category_name = request.args.get('category')
    query = Post.query
    
    if category_name:
        # 通過 category name 查詢對應的 category
        category = Category.query.filter_by(name=category_name).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    posts = query.order_by(Post.created_at.desc()).all()
    posts_data = [{
        'id': post.id,
        'title': post.title, 
        'content': post.content,
        'category': post.category.name if post.category else None,
        'created_at': post.created_at.isoformat(),
        'image_path': post.image_path,
        'html_content': post.html_content,
        'tags': [{'id': tag.id, 'name': tag.name} for tag in post.tags],
        'is_admin': current_user.is_authenticated and current_user.is_administrator,
        'slug': post.slug  # Add slug field here
    } for post in posts]
    return jsonify(posts_data)