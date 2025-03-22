from flask import Blueprint, render_template, g
from blog.models import Settings

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/about')
def about():
    return render_template('about.html')

@pages_bp.context_processor
def utility_processor():
    return {'blog_settings': getattr(g, 'blog_settings', Settings.get_blog_settings())}
