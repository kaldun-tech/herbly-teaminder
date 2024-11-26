# Runs the TeaMinder App
from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app.routes import main as main_blueprint
app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(debug=True)