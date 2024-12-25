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
        try:
            tea = tea_service.get_tea_item(name)
            return tea, None
        except KeyError:
            return None, (jsonify({'error': 'Tea not found'}), 404)

    @tea_routes.route('/tea', methods=['GET'])
    def get_teas():
        """Get all teas"""
        try:
            teas = tea_service.get_all_tea_items()
            return jsonify(teas), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/tea/<name>', methods=['GET'])
    def get_tea(name):
        """Get a tea by name"""
        tea, error = get_tea_or_404(name)
        if error:
            return error
        return jsonify(tea), 200

    @tea_routes.route('/tea', methods=['POST'])
    def create_tea():
        """Create a new tea"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['Name', 'Type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            # Create tea item
            tea_item = tea_service.create_tea_item(data)
            return jsonify(tea_item), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/tea/<name>', methods=['DELETE'])
    def delete_tea(name):
        """Delete a tea"""
        try:
            tea_service.delete_tea_item(name)
            return '', 204
        except KeyError:
            return jsonify({'error': 'Tea not found'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    @tea_routes.route('/tea/<name>/increment', methods=['POST'])
    def increment_steep_count(name):
        """Increment steep count for a tea"""
        try:
            tea_service.increment_steep_count(name)
            tea = tea_service.get_tea_item(name)
            return jsonify(tea), 200
        except KeyError:
            return jsonify({'error': 'Tea not found'}), 404
        except ValueError as e:
            return jsonify({'error': str(e)}), 500

    return tea_routes
