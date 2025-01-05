# Runs the TeaMinder App
import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from app.config.config import Config as app_config
from app.routes.api.tea_routes import create_tea_routes
from app.routes.pages import create_page_routes
from app.routes.auth import bp as auth_bp

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.template_folder = os.path.join(os.path.dirname(__file__), 'templates/html_templates')

    # Initialize security headers
    Talisman(app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
        }
    )

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["20 per day", "5 per hour"],
        storage_uri="memory://"
    )

    # Load default configuration
    app.config.from_object(app_config)

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register blueprints
    with app.app_context():
        app.register_blueprint(create_tea_routes(), url_prefix='/api')
        app.register_blueprint(create_page_routes())
        app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == '__main__':
    create_app().run()
