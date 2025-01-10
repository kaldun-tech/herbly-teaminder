"""CLI commands for the application"""
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User
from app.models.tea import Tea
from app.security.key_management import (
    rotate_secret_key, get_days_until_rotation,
    KeyRotationError
)

def register_commands(app):
    """Register CLI commands"""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(rotate_key_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    # Import all models to ensure they're registered with SQLAlchemy
    from app.models.user import User
    from app.models.tea import Tea
    
    click.echo('Dropping all tables...')
    db.drop_all()
    click.echo('Creating all tables...')
    db.create_all()
    click.echo('Initialized the database.')

@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user."""
    try:
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            click.echo(f'Error: Username {username} already exists.')
            return
        if User.query.filter_by(email=email).first():
            click.echo(f'Error: Email {email} already exists.')
            return

        # Create admin user
        admin = User(
            username=username,
            email=email,
            is_admin=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Successfully created admin user: {username}')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error creating admin user: {str(e)}')
        raise

@click.command('rotate-key')
@click.option('--force', is_flag=True, help='Force key rotation even if not needed')
@with_appcontext
def rotate_key_command(force):
    """Rotate the secret key"""
    try:
        days_left = get_days_until_rotation()
        if not force and days_left > 0:
            click.echo(f"Key rotation not needed yet. {days_left} days until required rotation.")
            click.echo("Use --force to rotate anyway.")
            return

        old_key, new_key = rotate_secret_key()
        click.echo("Secret key rotated successfully!")
        click.echo(f"New key: {new_key}")
        click.echo("\nMake sure to update your environment variables!")
        
    except KeyRotationError as e:
        click.echo(f"Error rotating key: {e}")
        raise click.Abort()
