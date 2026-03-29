import os
from flask import Blueprint, send_from_directory,jsonify
from app.core.config import BASE_DIR

static_bp = Blueprint('static', __name__)

current_dir = str(BASE_DIR)

# 处理所有静态资源请求（未来打包用）
@static_bp.route('/assets/<filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(current_dir, 'assets'), filename)

@static_bp.route('/health')
def health():
    return jsonify(
                {
                    "code": 200,
                    "msg": None,
                    "data": "ok"
                }), 200

# 处理 favicon.ico 静态资源（未来打包用）
@static_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_dir, 'assets'), 'vite.svg')

@static_bp.route('/vite.svg')
def vite_svg():
    return send_from_directory(os.path.join(current_dir, 'assets'), 'vite.svg')

# （未来打包用）
@static_bp.route('/')
def index():  # put application's code here
    return send_from_directory(current_dir, 'index.html')
