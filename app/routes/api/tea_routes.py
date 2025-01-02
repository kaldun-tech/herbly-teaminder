"""Routes for Teas"""
from flask import Blueprint, jsonify, request, current_app
from app.services.tea_service import TeaService
from app.dao.tea_dao import TeaDao
from app.config.tea_defaults import TEA_DEFAULTS

def create_tea_routes(tea_service=None):
    """Factory function to create tea routes blueprint with optional service injection"""
    tea_routes = Blueprint('tea_routes', __name__)

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
    def get_teas():
        """Get all teas"""
        try:
            teas = get_service().get_all_tea_items()
            return jsonify(teas), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>', methods=['GET'])
    def get_tea(name):
        """Get a tea by name"""
        tea, error = get_tea_or_404(name)
        if error:
            return error
        return jsonify(tea), 200

    @tea_routes.route('/teas', methods=['POST'])
    def create_tea():
        """Create a new tea"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            required_fields = ['Name', 'Type']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            tea_item = get_service().create_tea_item(data)
            return jsonify(tea_item), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/teas/<name>', methods=['PUT'])
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
