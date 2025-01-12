"""Routes package."""
from flask import Flask
from app.routes.auth import create_auth_routes
from app.routes.pages import create_pages_routes

def register_blueprints(app: Flask):
    """Register all blueprints."""
    # Register auth blueprint
    auth_bp = create_auth_routes()
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register pages blueprint
    pages_bp = create_pages_routes()
    app.register_blueprint(pages_bp, url_prefix='')