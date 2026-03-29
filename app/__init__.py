from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # 允许所有来源跨域访问
    CORS(app)
    
    # 限制上传文件大小为160MB
    app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024
    
    from app.api import register_blueprints
    register_blueprints(app)
    
    return app
