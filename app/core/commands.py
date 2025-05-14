"""
CLI commands module.
Handles all Flask CLI commands for the application.
"""

import click
from flask.cli import with_appcontext
from app.core.database import db
from app.core.utils.seed import seed_database
from app.core.utils.auth_utils import create_admin_user
import logging

logger = logging.getLogger(__name__)

@click.command('init-db')
@with_appcontext
def init_db():
    """Initialize the database."""
    try:
        logger.info("Initializing database...")
        db.create_all()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise click.ClickException(f"Database initialization failed: {str(e)}")

@click.command('seed-db')
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    try:
        logger.info("Seeding database...")
        seed_database()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Failed to seed database: {str(e)}")
        raise click.ClickException(f"Database seeding failed: {str(e)}")

@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin(username: str, email: str, password: str):
    """Create an admin user."""
    try:
        logger.info("Creating admin user...")
        create_admin_user(username, email, password)
        logger.info("Admin user created successfully")
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        raise click.ClickException(f"Admin user creation failed: {str(e)}")

@click.command('run-tests')
@click.option('--coverage/--no-coverage', default=False, help='Run tests with coverage')
@with_appcontext
def run_tests(coverage: bool):
    """Run the test suite."""
    try:
        import pytest
        
        logger.info("Running tests...")
        args = []
        if coverage:
            args.extend(['--cov=app', '--cov-report=term-missing'])
        
        exit_code = pytest.main(args)
        if exit_code != 0:
            raise Exception("Tests failed")
            
        logger.info("Tests completed successfully")
    except Exception as e:
        logger.error(f"Failed to run tests: {str(e)}")
        raise click.ClickException(f"Test execution failed: {str(e)}") 