"""AWS Elastic Beanstalk application entry point"""
from app.app import create_app

# Create the Flask application
application = create_app()

# Health check endpoint
@application.route('/api/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    application.run()
