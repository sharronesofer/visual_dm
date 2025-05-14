import pytest
from app import create_app
from app.extensions import db
from app.models.base import UUIDMixin
import uuid
from sqlalchemy import String

@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        yield app

def test_db_connection(app):
    # Try to execute a simple query
    result = db.session.execute('SELECT 1').scalar()
    assert result == 1 

class TempUUIDModel(UUIDMixin, db.Model):
    __tablename__ = 'temp_uuid_model'
    name = db.Column(String(50))

@pytest.fixture
def uuid_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_uuid_model_crud(uuid_app):
    obj = TempUUIDModel(name='test')
    db.session.add(obj)
    db.session.commit()
    fetched = TempUUIDModel.query.filter_by(name='test').first()
    assert fetched is not None
    assert isinstance(fetched.id, uuid.UUID) 