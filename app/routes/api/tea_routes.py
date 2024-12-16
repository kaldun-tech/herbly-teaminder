"""Routes for Teas"""
from venv import create

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from app.factory import create_app
from app.models.tea import Tea

app = create_app()
tea_routes = Blueprint('tea_routes', __name__)

@tea_routes.route('/teas', methods=['GET'])
def get_teas():
    """Render the HTML for the table and input fields using the tea list data"""
    teas = Tea.query.all()
    return render_template('teas.html', teas=teas)

@tea_routes.route('/teas', methods=['POST'])
def add_tea(name, tea_type, temperature, steep_time, steep_count):
    """Handle form submission to add a new tea record"""
    name = request.form['name']
    tea_type = request.form['type']
    temperature = request.form['temperature']
    steep_time = request.form['steep_time']
    steep_count = request.form['steep_count']
    # Add the new tea record to the database
    tea = Tea(name, tea_type, temperature, steep_time, steep_count)
    db.session.add(tea)
    db.session.commit()
    return redirect(url_for('teas'))

@tea_routes.route('/teas/<int:tea_id>/edit', methods=['GET', 'POST'])
def edit_tea(tea_id):
    tea = Tea.query.get(tea_id)
    if request.method == 'POST':
        # Handle form submission to edit a tea record
        tea.name = request.form['name']
        tea.type = request.form['type']
        tea.temperature = request.form['temperature']
        tea.steep_time = request.form['steep_time']
        tea.steep_count = request.form['steep_count']
        db.session.commit()
        return redirect(url_for('teas'))
    else:
        # Render the HTML for the edit form
        return render_template('edit_tea.html', tea=tea)

@tea_routes.route('/teas/<int:tea_id>/delete', methods=['POST'])
def delete_tea(tea_id):
    tea = Tea.query.get(tea_id)
    db.session.delete(tea)
    db.session.commit()
    return redirect(url_for('teas'))
