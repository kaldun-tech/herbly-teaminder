"""Pages routes for the application."""
from flask import Blueprint, jsonify

def create_pages_routes():
    """Create pages routes blueprint."""
    pages_bp = Blueprint('pages', __name__)

    @pages_bp.route('/', methods=['GET'])
    def index():
        """Main page."""
        return jsonify({'message': 'Welcome to TeaMinder!'}), 200

    return pages_bp
