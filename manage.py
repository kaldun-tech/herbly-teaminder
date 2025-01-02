"""
This script runs the application using a development server.
The development server is run using the `flask` command and
is configured to use the `development` configuration.
"""
from app.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
