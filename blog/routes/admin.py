from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from blog import db
from blog.models import Category, Settings

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_bp.route('/settings/<type>', methods=['GET', 'POST'])
@login_required
def settings(type=None):
    if not current_user.is_administrator:
        flash('Only administrators can access settings')
        return redirect(url_for('post.home'))
        
    if request.method == 'POST':
        setting_type = request.form.get('setting_type')
        
        if setting_type == 'ga':
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
    
    # GET request handling
    ga_tracking_id = Settings.get_setting('ga_tracking_id', '')
    categories = Category.query.order_by(Category.name).all()
    return render_template('settings.html',
                         ga_tracking_id=ga_tracking_id,
                         categories=categories)
