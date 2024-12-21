# Runs the TeaMinder App
from flask import Flask
from app.config import config as app_config
from app.routes.api.tea_routes import create_tea_routes

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load default configuration
    app.config.from_object(app_config.Config)

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register blueprints
    app.register_blueprint(create_tea_routes())

    @app.route('/')
    def home():
        return 'Herbly TeaMinder'

    return app

if __name__ == '__main__':
    create_app().run()
