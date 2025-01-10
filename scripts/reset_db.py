"""Database reset and verification script"""
import os
import sys
import shutil
import sqlite3
import sqlalchemy.exc
from pathlib import Path
import sqlalchemy

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tea import Tea

def get_db_path():
    """Get absolute path to database"""
    # Use Flask's instance path for database
    instance_path = os.path.join(project_root, 'instance')
    return os.path.join(instance_path, 'dev.db')

def ensure_db_directory():
    """Ensure database directory exists and is writable"""
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(db_dir, exist_ok=True)
        print(f"✓ Created directory {db_dir}")
        
        # Check if directory is writable
        test_file = os.path.join(db_dir, '.test_write')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✓ Directory {db_dir} is writable")
        except (IOError, OSError) as e:
            print(f"✗ Directory {db_dir} is not writable: {e}")
            return False
            
        return True
    except OSError as e:
        print(f"✗ Failed to create directory {db_dir}: {e}")
        return False

def clean_database_files():
    """Remove all database-related files"""
    db_path = get_db_path()
    journal_path = f"{db_path}-journal"
    
    for file_path in [db_path, journal_path]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Removed {file_path}")
            except Exception as e:
                print(f"✗ Failed to remove {file_path}: {e}")

def verify_database(conn):
    """Verify database tables and schema"""
    db_path = get_db_path()
    print(f"\nChecking database at: {db_path}")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"✗ Database file does not exist at: {db_path}")
        return False
        
    # Check file size
    size = os.path.getsize(db_path)
    print(f"Database file size: {size} bytes")
    
    if size == 0:
        print("✗ Database file is empty")
        return False
    
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    print(f"Found tables in database: {tables}")
    
    required_tables = {'users', 'teas'}
    
    if not required_tables.issubset(tables):
        missing = required_tables - tables
        print(f"✗ Missing tables: {missing}")
        return False
            
    # Verify users table schema
    cursor.execute("PRAGMA table_info(users);")
    columns = {row[1] for row in cursor.fetchall()}
    required_columns = {
        'id', 'username', 'email', 'password_hash',
        'created_at', 'is_active', 'is_admin'
    }
    
    if not required_columns.issubset(columns):
        missing = required_columns - columns
        print(f"✗ Missing columns in users table: {missing}")
        return False
            
    print("✓ Database schema verification passed")
    return True
        
def reset_database():
    """Reset the database"""
    os.chdir(project_root)
    db_path = get_db_path()
    
    print("\n=== Resetting Database ===\n")
    
    # Ensure database directory exists and is writable
    if not ensure_db_directory():
        return False
    
    # Clean up existing files
    print("Cleaning up existing files...")
    clean_database_files()
    
    # Create app context
    try:
        app = create_app()
    except ImportError as e:
        print(f"✗ Failed to import required modules: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to create Flask app: {e}")
        return False
    
    # Set database URI using absolute path
    db_uri = f'sqlite:///{db_path}'
    print(f"Using database URI: {db_uri}")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    
    with app.app_context():
        print("\nInitializing database tables...")
        try:
            # Print all models that will be created
            print("\nRegistered models:")
            for table in db.metadata.tables:
                print(f"- {table}")
            
            # Get engine and check its URL
            engine = db.get_engine()
            print(f"SQLAlchemy engine URL: {engine.url}")
            
            db.drop_all()
            print("✓ Dropped all tables")
            
            # Create tables
            db.create_all()
            print("✓ Created all tables")
            
            # Print created tables
            inspector = db.inspect(engine)
            print("\nCreated tables:")
            for table in inspector.get_table_names():
                print(f"- {table}")
                columns = inspector.get_columns(table)
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            
            # Force a write to create the database file
            db.session.execute(sqlalchemy.text('SELECT 1'))
            db.session.commit()
            print("✓ Committed changes")
            
            # Verify file exists and has content
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"\nDatabase file created at: {db_path}")
                print(f"Database file size: {size} bytes")
            else:
                print(f"✗ Database file was not created at: {db_path}")
                return False
                
        except ImportError as e:
            print(f"✗ Failed to import required models: {e}")
            return False
        except sqlalchemy.exc.OperationalError as e:
            print(f"✗ Database operation failed: {e}")
            return False
        except sqlalchemy.exc.SQLAlchemyError as e:
            print(f"✗ SQLAlchemy error: {e}")
            return False
        except OSError as e:
            print(f"✗ File system error: {e}")
            return False
            
    try:
        # Connect to database for verification
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"✗ Failed to connect to database for verification: {e}")
        return False
    
    try:
        # Verify database
        print("\nVerifying database schema...")
        if not verify_database(conn):
            print("✗ Database verification failed")
            return False
    except sqlite3.Error as e:
        print(f"✗ Database verification error: {e}")
        return False
    finally:
        conn.close()
        
    print("\n✓ Database reset and verification completed successfully!")
    return True

if __name__ == "__main__":
    if reset_database():
        print("\nYou can now create an admin user with:")
        print("flask create-admin")
    else:
        sys.exit(1)
