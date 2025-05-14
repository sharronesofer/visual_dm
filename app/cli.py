import click
from flask.cli import with_appcontext
from app.db_init import init_db

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with basic data."""
    init_db()
    click.echo('Initialized the database with basic data.') 