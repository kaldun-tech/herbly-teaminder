"""Builds the app"""
from flask import Flask
from app.routes.api import tea_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(tea_routes)
    return app
