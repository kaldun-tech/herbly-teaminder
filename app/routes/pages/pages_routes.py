"""Pages routes for the application."""
from flask import Blueprint, jsonify

def create_pages_routes():
    """Create pages routes blueprint."""
    pages_bp = Blueprint('pages', __name__)

    @pages_bp.route('/', methods=['GET'])
    def index():
        """Main page endpoint."""
        return jsonify({
            'message': 'Welcome to TeaMinder!',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': '/auth/register',
                    'login': '/auth/login',
                    'logout': '/auth/logout',
                    'profile': '/auth/profile'
                },
                'teas': {
                    'list': '/api/teas',
                    'create': '/api/teas',
                    'get': '/api/teas/<id>',
                    'update': '/api/teas/<id>',
                    'delete': '/api/teas/<id>',
                    'increment_steep': '/api/teas/<id>/increment',
                    'clear_steep': '/api/teas/<id>/clear'
                }
            }
        }), 200

    @pages_bp.route('/about', methods=['GET'])
    def about():
        """About page endpoint."""
        return jsonify({
            'name': 'TeaMinder',
            'description': 'A tea steeping timer and tracking application',
            'features': [
                'Track your tea collection',
                'Set steeping timers',
                'Record steeping history',
                'Manage multiple tea types'
            ],
            'version': '1.0.0',
            'contact': 'support@teaminder.example.com'
        }), 200

    return pages_bp
