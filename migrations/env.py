import logging
from logging.config import fileConfig

from alembic import context
from app.core.database import db
from app.core.models import *  # Ensure all models are imported for Alembic autogenerate

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

target_metadata = db.Model.metadata  # Use Flask-SQLAlchemy metadata for migrations

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    from sqlalchemy import create_engine
    url = config.get_main_option("sqlalchemy.url")
    print("ALEMBIC URL:", url)
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
