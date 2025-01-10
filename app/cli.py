"""CLI commands for the application"""
import click
from flask.cli import with_appcontext
from app.extensions import db
from app.security.key_management import (
    rotate_secret_key, get_days_until_rotation,
    KeyRotationError
)

def register_commands(app):
    """Register CLI commands"""
    app.cli.add_command(reset_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(rotate_key_command)

@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Reset the database."""
    if not click.confirm('Are you sure you want to reset the database? This will delete all data!'):
        click.echo('Database reset cancelled.')
        return

    # Import all models to ensure they're registered with SQLAlchemy
    from app.models.user import User  # pylint: disable=import-outside-toplevel
    from app.models.tea import Tea    # pylint: disable=import-outside-toplevel

    click.echo('Dropping all tables...')
    db.drop_all()
    click.echo('Creating all tables...')
    db.create_all()
    click.echo('Database reset complete!')

@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user."""
    # Import User model here to avoid circular imports
    from app.models.user import User  # pylint: disable=import-outside-toplevel

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        click.echo('Error: Username already exists.')
        return

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        click.echo('Error: Email already exists.')
        return

    try:
        admin = User(
            username=username,
            email=email,
            is_active=True,
            is_admin=True
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        click.echo(f'Successfully created admin user: {username}')
    except Exception as e:
        click.echo(f'Error creating admin user: {e}')
        db.session.rollback()

@click.command('rotate-key')
@click.option('--force', is_flag=True, help='Force key rotation even if not due')
@with_appcontext
def rotate_key_command(force):
    """Rotate the application secret key."""
    try:
        days_until_rotation = get_days_until_rotation()
        if days_until_rotation > 0 and not force:
            click.echo(f"Key rotation not due for {days_until_rotation} days.")
            click.echo("Use --force to rotate anyway.")
            return

        _, new_key = rotate_secret_key()
        click.echo("Secret key rotated successfully!")
        click.echo(f"New key: {new_key}")
        click.echo("\nMake sure to update your environment variables!")

    except KeyRotationError as e:
        click.echo(f"Error rotating key: {e}")
        raise click.Abort()
