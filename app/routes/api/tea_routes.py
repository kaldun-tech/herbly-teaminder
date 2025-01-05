"""Routes for Teas"""
from flask import Blueprint, jsonify, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.tea_service import TeaService
from app.dao.tea_dao import TeaDao
from app.config.tea_defaults import TEA_DEFAULTS

def create_tea_routes(tea_service=None):
    """Factory function to create tea routes blueprint with optional service injection"""
    tea_routes = Blueprint('tea_routes', __name__)
    
    limiter = Limiter(key_func=get_remote_address, app=tea_routes)

    def get_service():
        if tea_service is not None:
            return tea_service

        # Only access current_app when the route is actually called
        config = current_app.config
        tea_dao = TeaDao(
            region_name=config.get('AWS_REGION', 'us-east-1'),
            table_name=config.get('DYNAMODB_TABLE_NAME', 'teas')
        )
        return TeaService(tea_dao)

    def get_tea_or_404(name):
        """Helper function to get a tea or return 404 response"""
        try:
            tea = get_service().get_tea_item(name)
            return tea, None
        except KeyError:
            return None, (jsonify({'error': 'Tea not found'}), 404)

    @tea_routes.route('/teas', methods=['GET'])
    @limiter.limit("5/minute")
    def get_teas():
        """Get all teas"""
        try:
            teas = get_service().get_all_tea_items()
            return jsonify(teas), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>', methods=['GET'])
    @limiter.limit("30/minute")
    def get_tea(name):
        """Get a tea by name"""
        tea, error = get_tea_or_404(name)
        if error:
            return error
        return jsonify(tea), 200

    @tea_routes.route('/teas', methods=['POST'])
    @limiter.limit("5/minute")
    def create_tea():
        """Create a new tea"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Validate required fields
            required_fields = ['Name', 'Type']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
                if not isinstance(data[field], str):
                    return jsonify({'error': f'{field} must be a string'}), 400
                if len(data[field]) > 100:  # Limit field length
                    return jsonify({'error': f'{field} must be less than 100 characters'}), 400

            # Validate numeric fields
            if 'SteepTemperatureFahrenheit' in data:
                temp = data['SteepTemperatureFahrenheit']
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 212:
                    return jsonify({'error': 'Invalid steep temperature'}), 400

            if 'SteepTimeMinutes' in data:
                time = data['SteepTimeMinutes']
                if not isinstance(time, (int, float)) or time < 0 or time > 60:
                    return jsonify({'error': 'Invalid steep time'}), 400

            tea_item = get_service().create_tea_item(data)
            return jsonify(tea_item), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>', methods=['PUT'])
    @limiter.limit("5/minute")
    def update_tea(name):
        """Update a tea"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            tea_item = get_service().update_tea_item(name, data)
            return jsonify(tea_item), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>', methods=['DELETE'])
    @limiter.limit("5/minute")
    def delete_tea(name):
        """Delete a tea"""
        try:
            get_service().delete_tea_item(name)
            return '', 204
        except KeyError:
            return jsonify({'error': 'Tea not found'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>/steep', methods=['POST'])
    @limiter.limit("5/minute")
    def increment_steep_count(name):
        """Increment steep count for a tea"""
        try:
            service = get_service()
            tea = service.increment_steep_count(name)
            return jsonify(tea), 200
        except KeyError:
            return jsonify({'error': 'Tea not found'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>/clear', methods=['POST'])
    @limiter.limit("5/minute")
    def clear_steep_count(name):
        """Clear steep count for a tea"""
        try:
            get_service().clear_steep_count(name)
            return '', 200
        except KeyError:
            return jsonify({'error': 'Tea not found'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/defaults', methods=['GET'])
    def get_tea_defaults():
        """Get default values for different tea types"""
        return jsonify(TEA_DEFAULTS)

    return tea_routes
