import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash, current_app, jsonify, g
from flask_login import login_user, logout_user, login_required, current_user
from . import db, limiter
from .models import Post, Comment, User, Tag, Category, Settings
from .forms import RegistrationForm, LoginForm

# 設定圖片上傳的資料夾與允許的檔案類型
UPLOAD_FOLDER = os.path.join('blog', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 建立 blueprint
bp = Blueprint('main', __name__)

@bp.before_request
def load_settings():
    g.ga_tracking_id = Settings.get_setting('ga_tracking_id')

@bp.route('/')
@bp.route('/category/<category_name>')
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

@bp.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        current_app.logger.info(f"User {current_user.email} accessing post {post_id} (Admin: {current_user.is_administrator})")
    return render_template('post.html', 
                           post=post)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_administrator:
        flash('Only administrators can create posts')
        return redirect(url_for('main.home'))

    current_app.logger.info(f'Post creation attempt by {current_user.email}')
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            category_name = request.form['category']
            tags = request.form.get('tags', '').split(',')
            
            # 取得對應的 Category 對象
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                flash('Invalid category selected')
                return render_template('create.html', categories=categories)
            
            # 建立 Post 對象
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
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
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
            
            db.session.add(post)
            db.session.commit()
            
            flash('Post created successfully!')
            return redirect(url_for('main.post', post_id=post.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash('An error occurred while creating the post', 'error')
            return render_template('create.html', categories=categories)
    
    return render_template('create.html', categories=categories)

@bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_administrator:
        flash('Only administrators can edit posts')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            category_name = request.form['category']
            tags = request.form.get('tags', '').split(',')
            
            # 獲取對應的 Category 對象
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                flash('Invalid category selected')
                return redirect(url_for('main.edit', post_id=post.id))
            
            # 更新文章內容
            post.title = title
            post.content = content
            post.html_content = content
            post.category_id = category.id  # 使用 category.id 而不是 category 物件
            post.updated_at = datetime.utcnow()
            
            # 處理圖片上傳 (新增)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    post.image_path = f"uploads/{filename}"
            
            # 更新標籤
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
            return redirect(url_for('main.post', post_id=post.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating post: {str(e)}")
            flash('An error occurred while updating the post', 'error')
            return redirect(url_for('main.edit', post_id=post.id))
    
    # Get request處理
    current_tags = ', '.join([tag.name for tag in post.tags])
    categories = Category.query.order_by(Category.name).all()
    return render_template('edit.html', 
                         post=post,
                         categories=categories,
                         current_tags=current_tags)

@bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    if not current_user.is_administrator:
        flash('Only administrators can delete posts')
        return redirect(url_for('main.home'))
    post = Post.query.get_or_404(post_id)
    current_app.logger.info(f'Post delete attempt by {current_user.email} on post {post_id}')
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!')
    return redirect(url_for('main.home'))

@bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form['content']
    
    if not content:
        flash('Comment content is required!')
        return redirect(url_for('main.post', post_id=post.id))
    
    comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!')
    return redirect(url_for('main.post', post_id=post.id))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 禁用註冊功能
    flash('Registration is disabled. Please contact administrator.', 'error')
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5/minute", error_message="Too many login attempts. Please try again later.")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            current_app.logger.info(f"Successful login for user: {user.email} (Admin: {user.is_administrator})")
            flash('Logged in successfully!')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        current_app.logger.warning(f"Failed login attempt for email: {form.email.data}")
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.home'))

@bp.route('/api/posts')
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
        'is_admin': current_user.is_authenticated and current_user.is_administrator
    } for post in posts]
    return jsonify(posts_data)

# 處理 Quill Editor 的圖片上傳請求
@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        # 將檔案儲存在 <project_root>/static/uploads/
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        # 返回 URL：例如 http://127.0.0.1:5000/static/uploads/filename
        url = url_for('static', filename='uploads/' + filename, _external=True)
        return jsonify({'url': url})
    return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if not current_user.is_administrator:
        flash('Only administrators can manage categories')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            if name:
                category = Category.query.filter_by(name=name).first()
                if category:
                    flash('Category already exists')
                else:
                    category = Category(name=name)
                    db.session.add(category)
                    db.session.commit()
                    flash('Category added successfully')
        elif action == 'delete':
            category_id = request.form.get('category_id')
            if category_id:
                category = Category.query.get_or_404(category_id)
                if category.posts:
                    flash('Cannot delete category with existing posts')
                else:
                    db.session.delete(category)
                    db.session.commit()
                    flash('Category deleted successfully')
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('manage_categories.html', categories=categories)

@bp.route('/admin/settings', methods=['GET', 'POST'])
@bp.route('/admin/settings/<type>', methods=['GET', 'POST'])
@login_required
def settings(type=None):
    if not current_user.is_administrator:
        flash('Only administrators can access settings')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        setting_type = request.form.get('setting_type')
        
        if setting_type == 'ga':
            # Handle Google Analytics settings
            ga_tracking_id = request.form.get('ga_tracking_id', '').strip()
            Settings.set_setting('ga_tracking_id', ga_tracking_id)
            flash('Google Analytics settings updated successfully')
            
        elif setting_type == 'category':
            # Handle category management
            action = request.form.get('action')
            if action == 'add':
                name = request.form.get('name')
                if name:
                    category = Category.query.filter_by(name=name).first()
                    if category:
                        flash('Category already exists')
                    else:
                        category = Category(name=name)
                        db.session.add(category)
                        db.session.commit()
                        flash('Category added successfully')
            elif action == 'delete':
                category_id = request.form.get('category_id')
                if category_id:
                    category = Category.query.get_or_404(category_id)
                    if category.posts:
                        flash('Cannot delete category with existing posts')
                    else:
                        db.session.delete(category)
                        db.session.commit()
                        flash('Category deleted successfully')
    
    # Get current settings for template
    ga_tracking_id = Settings.get_setting('ga_tracking_id', '')
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('settings.html',
                         ga_tracking_id=ga_tracking_id,
                         categories=categories)

# Update existing template context processor
@bp.context_processor
def utility_processor():
    return {
        'ga_tracking_id': getattr(g, 'ga_tracking_id', None)
    }

@bp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
