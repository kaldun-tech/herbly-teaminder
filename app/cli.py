"""CLI commands for the application"""
import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User

def register_commands(app):
    """Register CLI commands"""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')
