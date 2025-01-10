"""Flask extensions"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
