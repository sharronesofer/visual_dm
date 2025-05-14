import pytest
from app import create_app

def test_app_factory():
    app = create_app()
    assert app is not None
    assert app.config['SQLALCHEMY_DATABASE_URI']
    assert hasattr(app, 'logger')

    with app.test_client() as client:
        response = client.get('/')
        # Root may not exist, but should not error
        assert response.status_code in (200, 404)
        response = client.get('/nonexistent')
        assert response.status_code == 404
        assert b'Not found' in response.data 