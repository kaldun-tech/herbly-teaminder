import logging
from app.app import create_app

# Set up logging
logging.basicConfig(
    filename='/var/log/flask/application.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

application = create_app()

if __name__ == '__main__':
    application.run()
