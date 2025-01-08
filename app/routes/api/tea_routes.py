"""Routes for Teas"""
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.tea import Tea
from datetime import datetime

def create_tea_routes():
    """Factory function to create tea routes blueprint"""
    tea_routes = Blueprint('tea_routes', __name__)

    def handle_tea_errors(f):
        """Decorator to handle common tea-related errors"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format'}), 400
            except KeyError as e:
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

    def get_tea_or_404(tea_id):
        """Helper function to get a tea or return 404 response"""
        tea = Tea.query.filter_by(id=tea_id, user_id=current_user.id).first()
        if not tea:
            return None, (jsonify({'error': 'Tea not found'}), 404)
        return tea, None

    @tea_routes.route('/api/teas', methods=['GET'])
    @login_required
    def get_teas():
        """Get all teas for the current user"""
        teas = Tea.query.filter_by(user_id=current_user.id).all()
        return jsonify([tea.to_dict() for tea in teas])

    @tea_routes.route('/api/teas', methods=['POST'])
    @login_required
    @handle_tea_errors
    def create_tea():
        """Create a new tea"""
        data = validate_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'steep_time', 'steep_temperature']
        for field in required_fields:
            if field not in data:
                raise KeyError(field)

        # Check if tea with same name already exists for this user
        existing_tea = Tea.query.filter_by(name=data['name'], user_id=current_user.id).first()
        if existing_tea:
            return jsonify({'error': 'Tea with this name already exists'}), 400

        tea = Tea(
            name=data['name'],
            type=data['type'],
            steep_time=data['steep_time'],
            steep_temperature=data['steep_temperature'],
            notes=data.get('notes'),
            user_id=current_user.id
        )
        
        db.session.add(tea)
        db.session.commit()
        
        return jsonify(tea.to_dict()), 201

    @tea_routes.route('/api/teas/<int:tea_id>', methods=['GET'])
    @login_required
    def get_tea(tea_id):
        """Get a specific tea"""
        tea, error = get_tea_or_404(tea_id)
        if error:
            return error
        return jsonify(tea.to_dict())

    @tea_routes.route('/api/teas/<int:tea_id>', methods=['PUT'])
    @login_required
    @handle_tea_errors
    def update_tea(tea_id):
        """Update a tea"""
        tea, error = get_tea_or_404(tea_id)
        if error:
            return error

        data = validate_json()
        
        # Update fields if present in request
        updatable_fields = ['name', 'type', 'steep_time', 'steep_temperature', 'notes']
        for field in updatable_fields:
            if field in data:
                setattr(tea, field, data[field])
        
        db.session.commit()
        return jsonify(tea.to_dict())

    @tea_routes.route('/api/teas/<int:tea_id>', methods=['DELETE'])
    @login_required
    def delete_tea(tea_id):
        """Delete a tea"""
        tea, error = get_tea_or_404(tea_id)
        if error:
            return error

        db.session.delete(tea)
        db.session.commit()
        return '', 204

    @tea_routes.route('/api/teas/<int:tea_id>/steep', methods=['POST'])
    @login_required
    def increment_steep_count(tea_id):
        """Increment the steep count for a tea"""
        tea, error = get_tea_or_404(tea_id)
        if error:
            return error

        tea.steep_count += 1
        db.session.commit()
        return jsonify(tea.to_dict())

    @tea_routes.route('/api/teas/<int:tea_id>/steep', methods=['DELETE'])
    @login_required
    def clear_steep_count(tea_id):
        """Reset the steep count for a tea to 0"""
        tea, error = get_tea_or_404(tea_id)
        if error:
            return error

        tea.steep_count = 0
        db.session.commit()
        return jsonify(tea.to_dict())

    return tea_routes
