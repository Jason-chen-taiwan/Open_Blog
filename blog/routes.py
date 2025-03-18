import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, send_from_directory, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import db, limiter
from .models import Post, Comment, User, Tag
from .forms import RegistrationForm, LoginForm

# 設定圖片上傳的資料夾與允許的檔案類型
UPLOAD_FOLDER = os.path.join('blog', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 建立 blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/category/<category>')
def home(category=None):
    query = Post.query
    if category:
        query = query.filter_by(category=category)
    posts = query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', 
                           posts=posts, 
                           current_category=category,
                           categories=['Cybersecurity', 'AI', 'Blockchain'])

@bp.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        current_app.logger.info(f"User {current_user.email} accessing post {post_id} (Admin: {current_user.is_administrator})")
    return render_template('post.html', 
                           post=post,
                           categories=['Cybersecurity', 'AI', 'Blockchain'])

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
    if request.method == 'POST':
        try:
            title = request.form['title']
            # 由 Quill 送出的內容已是 HTML
            content = request.form['content']
            category = request.form['category']
            tags = request.form.get('tags', '').split(',')
            
            # 若有上傳封面圖片（非文章內嵌圖片，由 Quill 處理內嵌圖片上傳）
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    image_path = f"uploads/{filename}"
            
            # 內容直接存 HTML，不用轉 Markdown
            html_content = content
            
            # 建立 Post 物件
            post = Post(
                title=title,
                content=content,
                html_content=html_content,
                category=category,
                user_id=current_user.id,
                image_path=image_path
            )
            
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
            return redirect(url_for('main.home'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash('An error occurred while creating the post', 'error')
            return redirect(url_for('main.create'))
    
    return render_template('create.html', categories=['Cybersecurity', 'AI', 'Blockchain'])

@bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_administrator:
        flash('Only administrators can edit posts')
        return redirect(url_for('main.home'))
    current_app.logger.info(f'Post edit attempt by {current_user.email} on post {post_id}')
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        tags = request.form.get('tags', '').split(',')
        
        if not title or not content:
            flash('Title and content are required!')
            return redirect(url_for('main.edit', post_id=post.id))
        
        post.title = title
        post.content = content
        post.html_content = content  # 內容已是 HTML
        post.category = category
        post.updated_at = datetime.utcnow()
        
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
    
    # 將目前標籤轉換成逗號分隔字串
    current_tags = ', '.join([tag.name for tag in post.tags])
    return render_template('edit.html', 
                           post=post, 
                           categories=['Cybersecurity', 'AI', 'Blockchain'],
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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

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
    category = request.args.get('category')
    query = Post.query
    if category:
        query = query.filter_by(category=category)
    posts = query.order_by(Post.created_at.desc()).all()
    posts_data = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'category': post.category,
        'created_at': post.created_at.isoformat(),
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



@bp.route('/uploads/<filename>')
def uploaded_files(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
