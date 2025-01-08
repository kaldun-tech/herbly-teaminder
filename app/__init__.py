"""Flask application factory"""
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.extensions import db
from app.cli import register_commands

def create_app(config_object=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Load config
    if config_object is None:
        # Default to development config
        from config import DevelopmentConfig
        config_object = DevelopmentConfig
    
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_routes.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Register CLI commands
    register_commands(app)

    with app.app_context():
        # Import routes
        from app.routes.api.tea_routes import create_tea_routes
        from app.routes.auth.auth_routes import create_auth_routes

        # Register blueprints
        app.register_blueprint(create_tea_routes())
        app.register_blueprint(create_auth_routes())

        return app