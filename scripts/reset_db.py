"""Script to reset the database and verify its integrity."""
import os
import sys
from pathlib import Path
import sqlalchemy.exc

# Standard imports before third-party imports
from app import create_app
from app.extensions import db

def get_instance_path():
    """Get the instance path from the app configuration."""
    app = create_app()
    return app.instance_path

def verify_db_path():
    """Verify database path exists and is writable."""
    instance_path = get_instance_path()
    db_path = Path(instance_path)

    if not db_path.exists():
        try:
            db_path.mkdir(parents=True)
            return True, "Created database directory"
        except PermissionError:
            return False, f"Permission denied creating directory: {db_path}"
        except OSError as e:
            return False, f"Error creating directory: {e}"

    if not os.access(db_path, os.W_OK):
        return False, f"Database directory not writable: {db_path}"

    return True, "Database directory verified"

def verify_db_file():
    """Verify database file exists and is writable."""
    instance_path = get_instance_path()
    db_file = Path(instance_path) / "dev.db"

    if not db_file.exists():
        try:
            # Create an empty file to verify write permissions
            with open(db_file, 'w', encoding='utf-8') as f:
                f.write('')
            return True, "Created database file"
        except PermissionError:
            return False, f"Permission denied creating file: {db_file}"
        except OSError as e:
            return False, f"Error creating file: {e}"

    if not os.access(db_file, os.W_OK):
        return False, f"Database file not writable: {db_file}"

    return True, "Database file verified"

def verify_db_connection():
    """Verify database connection."""
    try:
        app = create_app()
        with app.app_context():
            db.engine.connect()
        return True, "Database connection successful"
    except sqlalchemy.exc.OperationalError as e:
        return False, f"Database connection failed: {e}"
    except Exception as e:  # pylint: disable=broad-except
        return False, f"Unexpected database error: {e}"

def reset_database():
    """Reset the database and verify its integrity."""
    # Step 1: Verify database path
    path_ok, path_msg = verify_db_path()
    if not path_ok:
        print(f"Error: {path_msg}")
        return False

    print(f"Success: {path_msg}")

    # Step 2: Verify database file
    file_ok, file_msg = verify_db_file()
    if not file_ok:
        print(f"Error: {file_msg}")
        return False

    print(f"Success: {file_msg}")

    # Step 3: Verify database connection
    conn_ok, conn_msg = verify_db_connection()
    if not conn_ok:
        print(f"Error: {conn_msg}")
        return False

    print(f"Success: {conn_msg}")

    # Step 4: Reset database
    try:
        app = create_app()
        with app.app_context():
            print("Dropping all tables...")
            db.drop_all()
            print("Creating all tables...")
            db.create_all()
            print("Database reset complete!")
        return True
    except sqlalchemy.exc.OperationalError as e:
        print(f"Database reset failed: {e}")
        return False
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error during reset: {e}")
        return False

if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
