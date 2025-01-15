"""Initialize Flask app"""
import os
import logging
from flask import Flask, jsonify
from app.extensions import db, migrate, login_manager
from app.security.key_management import validate_secret_key, KeyValidationError
from app.error_handlers import register_error_handlers

def register_models():
    """Import models after db is initialized"""
    from app.models.user import User  # pylint: disable=import-outside-toplevel
    from app.models.tea import Tea    # pylint: disable=import-outside-toplevel
    return User, Tea

def register_blueprints(app):
    """Register all blueprints"""
    from app.routes.auth.auth_routes import create_auth_routes  # pylint: disable=import-outside-toplevel
    from app.routes.api.tea_routes import create_tea_routes    # pylint: disable=import-outside-toplevel
    from app.routes.pages.pages_routes import create_pages_routes   # pylint: disable=import-outside-toplevel
    auth_bp = create_auth_routes()
    tea_bp = create_tea_routes()
    page_bp = create_pages_routes()
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tea_bp)
    app.register_blueprint(page_bp)

def create_app(config=None):
    """Create Flask application."""
    app = Flask(__name__)
    logger = logging.getLogger(__name__)

    # Determine environment
    env = os.environ.get('FLASK_ENV', 'development')
    if config == 'testing':
        env = 'testing'
    elif config == 'production':
        env = 'production'

    # Load configuration
    if config is None:
        config = os.environ.get('FLASK_CONFIG', 'default')
        app.config.from_object(f'config.{config.capitalize()}Config')
    elif isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_object(f'config.{config.capitalize()}Config')

    # Validate secret key
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    try:
        validate_secret_key(secret_key, env)
        app.config['SECRET_KEY'] = secret_key
    except KeyValidationError as e:
        if env == 'production':
            raise  # In production, fail fast
        logger.warning("Secret key validation failed: %s", e)
        app.config['SECRET_KEY'] = secret_key  # Use key anyway in development

    # Set database URI if not already set
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/dev.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Configure unauthorized handler for API routes
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized'}), 401

    # Import and register models
    User, _ = register_models()

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register all blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    # Register CLI commands
    from app.cli import register_commands  # pylint: disable=import-outside-toplevel
    register_commands(app)

    with app.app_context():
        # Create all tables
        db.create_all()

    return app

if __name__ == '__main__':
    create_app().run()
