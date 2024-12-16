# Runs the TeaMinder App
from flask import Flask
from app.config import config as dev
from app.routes.api import tea_routes

app = Flask(__name__)
app.register_blueprint(tea_routes)

@app.route('/')
def home():
    return 'Herbly TeaMinder'

def create_app():
    # Create the app for development
    app.config.from_object(dev.Config)
    # Add other initialization code here
    return app

if __name__ == '__main__':
    create_app().run()
