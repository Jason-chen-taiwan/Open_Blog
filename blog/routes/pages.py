from flask import Blueprint, render_template, g
from blog.models import Settings

pages_bp = Blueprint('pages', __name__)  # 不需要 url_prefix

@pages_bp.before_request
def load_settings():
    g.ga_tracking_id = Settings.get_setting('ga_tracking_id')

@pages_bp.route('/about')  # 直接使用根路徑
def about():
    return render_template('about.html')

@pages_bp.context_processor  # 添加上下文處理器
def utility_processor():
    return {'ga_tracking_id': getattr(g, 'ga_tracking_id', None)}
