import logging
from app.app import create_app

# Set up logging
logging.basicConfig(
    filename='/var/log/flask/application.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

application = create_app()

# Health check endpoint
@application.route('/api/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    application.run()
