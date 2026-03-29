from app.api.file import file_bp
from app.api.account import account_bp
from app.api.publish import publish_bp
from app.api.static import static_bp

def register_blueprints(app):
    app.register_blueprint(file_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(publish_bp)
    app.register_blueprint(static_bp)
