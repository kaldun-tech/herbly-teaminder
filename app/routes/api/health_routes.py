"""Health check routes"""
from flask import Blueprint, jsonify

health_routes = Blueprint('health', __name__)

@health_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'herbly-teaminder'
    }), 200
