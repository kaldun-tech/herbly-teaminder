"""Flask application factory module"""
import os
from flask import Flask, jsonify
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
from app.routes.api.tea_routes import create_tea_routes
from app.routes.pages import create_page_routes
from app.routes.auth import bp as auth_bp
from app.extensions import db, login_manager, migrate

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    app.static_folder = os.path.join(os.path.dirname(__file__), 'static')

    # Load default configuration
    if config is None:
        config = Config()
    app.config.from_object(config)

    # Load environment specific configuration
    if 'FLASK_CONFIG' in os.environ:
        app.config.from_object(f"app.config.{os.environ['FLASK_CONFIG']}")

    if config:
        app.config.update(config)

    # Set PostgreSQL database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/teaminder')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Initialize security headers except during testing
    if not app.config.get('TESTING', False):
        # Apply security headers to prevent common vulnerabilities
        csp = {
            'default-src': ['\'self\''],
            'script-src': [
                '\'self\'',
                '\'unsafe-inline\'',
                'cdn.jsdelivr.net'
            ],
            'style-src': [
                '\'self\'',
                '\'unsafe-inline\'',
                'cdn.jsdelivr.net'
            ],
            'font-src': [
                '\'self\'',
                'cdn.jsdelivr.net'
            ]
        }
        Talisman(app,
                force_https=app.config.get('FORCE_HTTPS', True),
                strict_transport_security=True,
                session_cookie_secure=True,
                content_security_policy=csp)

        # Initialize rate limiter with reasonable defaults
        Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
        )

    # Register error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors"""
        return jsonify(error="Rate limit exceeded", message=str(e.description)), 429

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return jsonify(error="Not found", message=str(error)), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify(error="Internal server error", message=str(error)), 500

    # Register blueprints
    with app.app_context():
        # Create database tables
        db.create_all()
        
        tea_bp = create_tea_routes()
        app.register_blueprint(tea_bp, url_prefix='/api')
        app.register_blueprint(create_page_routes())
        app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    create_app().run()
