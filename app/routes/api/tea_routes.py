"""Routes for Teas"""
from flask import Blueprint, jsonify, request, current_app
from app.services.tea_service import TeaService
from app.dao.tea_dao import TeaDao

def create_tea_routes(tea_service=None):
    """Factory function to create tea routes blueprint with optional service injection"""
    tea_routes = Blueprint('tea_routes', __name__)

    # Initialize service if not injected (production mode)
    if tea_service is None:
        config = current_app.config
        tea_dao = TeaDao(
            region_name=config.get('AWS_REGION', 'us-west-2'),
            table_name=config.get('DYNAMODB_TABLE_NAME', 'teas')
        )
        tea_service = TeaService(tea_dao)

    def get_tea_or_404(name):
        """Helper function to get a tea or return 404 response"""
        tea = tea_service.get_tea_item(name)
        if not tea:
            return None, (jsonify({'error': 'Tea not found'}), 404)
        return tea, None

    @tea_routes.route('/teas', methods=['GET'])
    def get_teas():
        """Get all teas"""
        teas = tea_service.get_teas()
        return jsonify(teas), 200

    @tea_routes.route('/teas/<name>', methods=['GET'])
    def get_tea(name):
        """Get a tea by name"""
        tea, error = get_tea_or_404(name)
        if error:
            return error
        return jsonify(tea), 200

    @tea_routes.route('/teas', methods=['POST'])
    def create_tea():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['name', 'tea_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if tea already exists
        tea, _ = get_tea_or_404(data['name'])
        if tea:
            return jsonify({'error': 'Tea already exists'}), 409

        # Create tea item dictionary
        tea_item = {
            'Name': data['name'],
            'Type': data['tea_type'],
            'SteepTimeSeconds': data.get('steep_time', 0),
            'SteepTemperatureFahrenheit': data.get('steep_temperature', 0),
            'SteepCount': data.get('steep_count', 0)
        }

        tea_service.create_tea_item(tea_item)
        return jsonify({'message': 'Tea created successfully'}), 201

    @tea_routes.route('/teas/<name>', methods=['PUT'])
    def update_tea(name):
        """Update a tea by name"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Ensure tea exists
        existing_tea, error = get_tea_or_404(name)
        if error:
            return error

        # Ensure name in URL matches name in data
        if 'name' in data and data['name'] != name:
            return jsonify({'error': 'Tea name in URL must match tea name in data'}), 400

        # Update tea item
        tea_item = {
            'Name': name,
            'Type': data.get('tea_type', existing_tea['Type']),
            'SteepTimeSeconds': data.get('steep_time', existing_tea['SteepTimeSeconds']),
            'SteepTemperatureFahrenheit': data.get('steep_temperature', existing_tea['SteepTemperatureFahrenheit']),
            'SteepCount': data.get('steep_count', existing_tea['SteepCount'])
        }

        tea_service.update_tea_item(tea_item)
        return jsonify({'message': 'Tea updated successfully'}), 200

    @tea_routes.route('/teas/<name>', methods=['DELETE'])
    def delete_tea(name):   
        """Delete a tea by name"""
        # Ensure tea exists
        _, error = get_tea_or_404(name)
        if error:
            return error

        tea_service.delete_tea_item(name)
        return jsonify({'message': 'Tea deleted successfully'}), 200

    @tea_routes.route('/teas/<name>/steep', methods=['POST'])
    def increment_steep(name):
        """Increment the steep count for a tea"""
        _, error = get_tea_or_404(name)
        if error:
            return error

        tea_service.increment_steep_count(name)
        return jsonify({'message': 'Steep count incremented'}), 200

    @tea_routes.route('/teas/<name>/steep', methods=['DELETE'])
    def clear_steep(name):
        """Clear the steep count for a tea"""
        _, error = get_tea_or_404(name)
        if error:
            return error

        tea_service.clear_steep_count(name)
        return jsonify({'message': 'Steep count cleared'}), 200

    return tea_routes
