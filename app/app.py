# Runs the TeaMinder App
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Herbly TeaMinder'

if __name__ == '__main__':
    app.run(debug=True)
