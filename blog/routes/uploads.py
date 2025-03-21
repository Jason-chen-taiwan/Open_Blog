import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, url_for, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

# 設定允許的檔案類型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        url = url_for('static', filename=f'uploads/{filename}', _external=True)
        return jsonify({'url': url})
    return jsonify({'error': 'File type not allowed'}), 400

@upload_bp.route('/uploads/<filename>')
def uploaded_files(filename):
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_path, filename)
