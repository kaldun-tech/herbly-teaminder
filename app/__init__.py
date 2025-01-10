"""Initialize Flask app"""
from flask import Flask
from app.extensions import db, migrate, login_manager

def create_app(config_object=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Load the default configuration
    if config_object is None:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object(config_object)

    # Set database URI if not already set
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import models after db is initialized to avoid circular imports
    from app.models.user import User
    from app.models.tea import Tea
    
    # Register blueprints
    from app.routes.auth.auth_routes import create_auth_routes
    from app.routes.api.tea_routes import create_tea_routes
    from app.routes.pages import create_page_routes
    
    auth_bp = create_auth_routes()
    tea_bp = create_tea_routes()
    page_bp = create_page_routes()
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tea_bp)
    app.register_blueprint(page_bp)

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)

    with app.app_context():
        # Create all tables
        db.create_all()

    return app