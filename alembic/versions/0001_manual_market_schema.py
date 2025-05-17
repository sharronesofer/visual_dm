"""
Manual migration to create the initial market data schema using SQLAlchemy's create_all().
This is a one-time bootstrap migration due to Alembic autogeneration issues in this environment.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from backend.app.models.base import Base
from backend.app.models import market  # Ensures all models are registered

def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind) 