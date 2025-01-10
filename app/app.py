"""Flask application factory"""
import os
from flask import Flask
from app.extensions import db, migrate, login_manager
from app.models import User, Tea
from app.routes.auth import create_auth_routes
from app.cli import register_commands
from app.security.key_management import validate_secret_key, KeyValidationError

def create_app(config=None):
    """Create Flask application."""
    app = Flask(__name__)
    
    # Determine environment
    env = os.environ.get('FLASK_ENV', 'development')
    if config == 'testing':
        env = 'testing'
    elif config == 'production':
        env = 'production'

    # Load the appropriate configuration
    if config is None:
        config = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(f'config.{config.capitalize()}Config')

    # Validate secret key
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    try:
        validate_secret_key(secret_key, env)
        app.config['SECRET_KEY'] = secret_key
    except KeyValidationError as e:
        if env == 'production':
            raise  # In production, fail fast
        else:
            app.logger.warning(f"Secret key validation failed: {e}")
            app.config['SECRET_KEY'] = secret_key  # Use key anyway in development

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    auth_bp = create_auth_routes()
    app.register_blueprint(auth_bp)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    # Register CLI commands
    register_commands(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    create_app().run()
