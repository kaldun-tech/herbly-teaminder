# Runs the TeaMinder App
import os
from flask import Flask, jsonify
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config.default import Config as app_config
from app.routes.api.tea_routes import create_tea_routes
from app.routes.pages import create_page_routes
from app.routes.auth import bp as auth_bp

"""Flask application factory"""
def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.template_folder = os.path.join(os.path.dirname(__file__), 'templates/html_templates')

    # Load default configuration
    app.config.from_object(app_config)

    # Load environment specific configuration
    if 'FLASK_CONFIG' in os.environ:
        app.config.from_object(f"app.config.{os.environ['FLASK_CONFIG']}")

    if config:
        app.config.update(config)

    # Initialize security headers except during testing
    if not app.config.get('TESTING', False):
        # Apply security headers to prevent common vulnerabilities
        Talisman(app,
                force_https=app.config.get('FORCE_HTTPS', True),
                strict_transport_security=True,
                session_cookie_secure=True)

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
        tea_bp = create_tea_routes()
        app.register_blueprint(tea_bp, url_prefix='/api')
        app.register_blueprint(create_page_routes())
        app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    create_app().run()
