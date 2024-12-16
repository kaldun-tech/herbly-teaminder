"""Tests for tea routes"""
import pytest
from app.app import create_app
from app.services import tea_service

@pytest.fixture
def app():
    return create_app()

def test_get_teas(app):
    # Test the GET /teas route
    with app.test_client() as client:
        response = client.get('/teas')
        assert response.status_code == 200

def test_post_tea(app):
    # Test the POST /teas route
    with app.test_client() as client:
        data = {'name': 'Test Tea', 'type': 'Black'}
        response = client.post('/teas', json=data)
        assert response.status_code == 201

def test_get_tea(app):
    # Test the GET /teas/<tea_id> route
    with app.test_client() as client:
        tea_id = tea_service.create_tea({'name': 'Test Tea', 'type': 'Black'})
        response = client.get(f'/teas/{tea_id}')
        assert response.status_code == 200

def test_put_tea(app):
    # Test the PUT /teas/<tea_id> route
    with app.test_client() as client:
        tea_id = tea_service.create_tea({'name': 'Test Tea', 'type': 'Black'})
        data = {'name': 'Updated Tea', 'type': 'Green'}
        response = client.put(f'/teas/{tea_id}', json=data)
        assert response.status_code == 200

def test_delete_tea(app):
    # Test the DELETE /teas/<tea_id> route
    with app.test_client() as client:
        tea_id = tea_service.create_tea({'name': 'Test Tea', 'type': 'Black'})
        response = client.delete(f'/teas/{tea_id}')
        assert response.status_code == 204
