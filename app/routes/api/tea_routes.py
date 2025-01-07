"""Routes for Teas"""
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from app.services.tea_service import TeaService
from app.dao.memory_tea_dao import MemoryTeaDao
from json.decoder import JSONDecodeError

# Create a single instance of the DAO to be shared across requests
tea_dao = MemoryTeaDao()

def create_tea_routes(tea_service=None):
    """Factory function to create tea routes blueprint with optional service injection"""
    tea_routes = Blueprint('tea_routes', __name__)

    def get_service():
        if tea_service is not None:
            return tea_service
        return TeaService(tea_dao)

    def handle_tea_errors(f):
        """Decorator to handle common tea-related errors"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format'}), 400
            except KeyError as e:
                # Check if this is a tea not found error
                if len(args) > 0 and str(e) == f"'{args[0]}'":
                    return jsonify({'error': 'Tea not found'}), 404
                return jsonify({'error': f'Missing required field: {str(e)}'}), 400
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        return wrapper

    def validate_json():
        """Helper function to get and validate JSON data"""
        data = request.get_json()
        if data is None:
            raise JSONDecodeError('Invalid JSON data', '', 0)
        return data

    def get_tea_or_404(name):
        """Helper function to get a tea or return 404 response"""
        try:
            tea = get_service().get_tea_item(name)
            return tea, None
        except KeyError:
            return None, (jsonify({'error': 'Tea not found'}), 404)

    @tea_routes.route('/teas', methods=['GET'])
    @handle_tea_errors
    def get_teas():
        """Get all teas"""
        teas = get_service().get_all_tea_items()
        return jsonify(teas), 200

    @tea_routes.route('/teas/<name>', methods=['GET'])
    @handle_tea_errors
    def get_tea(name):
        """Get a tea by name"""
        tea, error = get_tea_or_404(name)
        if error:
            return error
        return jsonify(tea), 200

    @tea_routes.route('/teas', methods=['POST'])
    @handle_tea_errors
    def create_tea():
        """Create a new tea"""
        tea_item = validate_json()
        created_tea = get_service().create_tea_item(tea_item)
        return jsonify(created_tea), 201

    @tea_routes.route('/teas/<name>', methods=['PUT'])
    @handle_tea_errors
    def update_tea(name):
        """Update a tea"""
        tea_item = validate_json()
        updated_tea = get_service().update_tea_item(name, tea_item)
        return jsonify(updated_tea), 200

    @tea_routes.route('/teas/<name>/steep', methods=['POST'])
    @handle_tea_errors
    def steep_tea(name):
        """Increment steep count"""
        tea = get_service().increment_steep_count(name)
        return jsonify(tea), 200

    @tea_routes.route('/teas/<name>/steep', methods=['DELETE'])
    @handle_tea_errors
    def clear_steep(name):
        """Clear steep count"""
        tea = get_service().clear_steep_count(name)
        return jsonify(tea), 200

    @tea_routes.route('/teas/<name>', methods=['DELETE'])
    @handle_tea_errors
    def delete_tea(name):
        """Delete a tea"""
        get_service().delete_tea_item(name)
        return '', 204

    @tea_routes.route('/defaults', methods=['GET'])
    def get_defaults():
        """Get default values for different tea types"""
        from app.config.tea_defaults import TEA_DEFAULTS
        return jsonify(TEA_DEFAULTS)

    return tea_routes
