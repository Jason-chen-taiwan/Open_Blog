import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, current_app
from flask_login import login_required, current_user
from blog import db
from blog.models import Category, Settings

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def handle_file_upload(file, directory):
    """Helper function to handle file uploads"""
    if file and file.filename:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        upload_path = os.path.join(current_app.root_path, 'static', directory)
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return f'{directory}/{filename}'
    return None

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_bp.route('/settings/<type>', methods=['GET', 'POST'])
@login_required
def settings(type=None):
    if not current_user.is_administrator:
        flash('Only administrators can access settings')
        return redirect(url_for('post.home'))
        
    if request.method == 'POST':
        setting_type = request.form.get('setting_type')
        
        if setting_type == 'blog_info':
            # 處理 blog 名稱
            blog_name = request.form.get('blog_name', '').strip()
            if blog_name:
                Settings.set_setting('blog_name', blog_name)
            
            # 處理 logo 上傳
            if 'logo' in request.files:
                file = request.files['logo']
                logo_path = handle_file_upload(file, 'img')
                if logo_path:
                    Settings.set_setting('logo_path', logo_path)
            
            flash('Blog settings updated successfully')
            return redirect(url_for('admin.settings'))
            
        elif setting_type == 'ga':
            ga_tracking_id = request.form.get('ga_tracking_id', '').strip()
            Settings.set_setting('ga_tracking_id', ga_tracking_id)
            flash('Google Analytics settings updated successfully')
            return redirect(url_for('admin.settings'))
            
        elif setting_type == 'category':
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
                return redirect(url_for('admin.settings'))
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
                return redirect(url_for('admin.settings'))
                
        elif setting_type == 'footer':
            # 更新頁尾 About 文字
            footer_about = request.form.get('footer_about', '').strip()
            if footer_about:
                Settings.set_setting('footer_about', footer_about)
            
            # 更新聯繫方式和社交媒體連結
            email = request.form.get('email', '').strip()
            Settings.set_setting('email', email)
            
            for platform in ['github', 'twitter', 'cake', 'instagram']:
                url = request.form.get(f'{platform}_url', '').strip()
                Settings.set_setting(f'{platform}_url', url)
            
            flash('Footer settings updated successfully')
            return redirect(url_for('admin.settings'))
    
    # GET request handling
    blog_settings = Settings.get_blog_settings()
    return render_template('settings.html',
                         blog_name=blog_settings['blog_name'],
                         logo_path=blog_settings['logo_path'],
                         ga_tracking_id=blog_settings['ga_tracking_id'],
                         footer_about=blog_settings['footer_about'],
                         github_url=blog_settings['github_url'],
                         twitter_url=blog_settings['twitter_url'],
                         cake_url=blog_settings['cake_url'],
                         instagram_url=blog_settings['instagram_url'],
                         email=blog_settings['email'],
                         categories=Category.query.order_by(Category.name).all())
