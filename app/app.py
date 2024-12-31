# Runs the TeaMinder App
from flask import Flask
from app.config.config import Config as app_config
from app.routes.api.tea_routes import create_tea_routes
from app.routes.pages import create_page_routes

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.template_folder = 'app/templates/html_templates'

    # Load default configuration
    app.config.from_object(app_config)

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register blueprints
    with app.app_context():
        app.register_blueprint(create_tea_routes(), url_prefix='/api')
        app.register_blueprint(create_page_routes())

    return app

if __name__ == '__main__':
    create_app().run()
