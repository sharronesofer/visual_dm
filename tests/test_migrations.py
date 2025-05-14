import os
import pytest
import subprocess
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

ALEMBIC_INI = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'migrations')

# Use test database URL from alembic.ini or environment
TEST_DB_URL = os.environ.get('ALEMBIC_TEST_DB_URL') or \
    'postgresql://postgres:postgres@localhost:5432/visual_dm_test'

@pytest.fixture(scope='module')
def alembic_config():
    cfg = Config(ALEMBIC_INI)
    cfg.set_main_option('script_location', MIGRATIONS_DIR)
    cfg.set_main_option('sqlalchemy.url', TEST_DB_URL)
    return cfg

@pytest.fixture(scope='function')
def clean_database():
    # Drop all tables before each test for isolation
    engine = create_engine(TEST_DB_URL)
    conn = engine.connect()
    trans = conn.begin()
    inspector = inspect(engine)
    for table in inspector.get_table_names():
        conn.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
    trans.commit()
    conn.close()
    engine.dispose()
    yield
    # No teardown needed (test DB is disposable)

@pytest.mark.order(1)
def test_upgrade_all_migrations(alembic_config, clean_database):
    """Test that all Alembic migrations apply cleanly to a fresh database."""
    command.upgrade(alembic_config, 'head')
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert len(tables) > 0, "No tables found after migration upgrade."
    engine.dispose()

@pytest.mark.order(2)
def test_downgrade_last_migration(alembic_config):
    """Test that the last Alembic migration can be rolled back (downgraded)."""
    # Get current head revision
    result = subprocess.run([
        'alembic', '-c', ALEMBIC_INI, 'current', '--verbose'
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"alembic current failed: {result.stderr}"
    lines = result.stdout.splitlines()
    head_line = next((l for l in lines if 'Current revision for' in l), None)
    assert head_line, "Could not determine current revision."
    head_rev = head_line.split()[-1]
    # Downgrade one revision
    command.downgrade(alembic_config, '-1')
    # Optionally, check that tables/columns were removed as expected
    # (This can be extended for specific schema checks)

@pytest.mark.order(3)
def test_upgrade_and_rollback_idempotency(alembic_config, clean_database):
    """Test that upgrade -> downgrade -> upgrade is idempotent."""
    command.upgrade(alembic_config, 'head')
    command.downgrade(alembic_config, '-1')
    command.upgrade(alembic_config, 'head')
    engine = create_engine(TEST_DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert len(tables) > 0, "No tables found after re-upgrade."
    engine.dispose()

# Optionally, add more granular tests for specific migrations, data integrity, etc. 