"""Setup script for development environment"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and print output"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        print(f"✓ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {command}:")
        print(e.stderr)
        return False

def setup_environment():
    """Set up development environment"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("\n=== Setting up development environment ===\n")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python version {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("\n--- Creating virtual environment ---")
        if not run_command("python -m venv venv"):
            sys.exit(1)

    # Activate virtual environment
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"

    # Install dependencies
    print("\n--- Installing dependencies ---")
    pip_command = f"{activate_script} && python -m pip install -r requirements.txt"
    if not run_command(pip_command):
        sys.exit(1)

    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        print("\n--- Creating .env file ---")
        env_content = """FLASK_DEBUG=True
FLASK_APP=app:create_app
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key-CHANGE-IN-PRODUCTION
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✓ Created .env file")

    # Initialize database
    print("\n--- Setting up database ---")
    db_commands = [
        f"{activate_script} && flask init-db",
        f"{activate_script} && flask db upgrade"
    ]
    for cmd in db_commands:
        if not run_command(cmd):
            sys.exit(1)

    # Create test admin user
    print("\n--- Creating test admin user ---")
    admin_command = f"{activate_script} && flask create-admin --username admin --email admin@example.com --password admin123"
    if not run_command(admin_command):
        sys.exit(1)

    print("\n=== Setup completed successfully! ===\n")
    print("You can now:")
    print("1. Activate the virtual environment:")
    print("   - Windows: .\\venv\\Scripts\\activate")
    print("   - Linux/Mac: source venv/bin/activate")
    print("2. Run the development server:")
    print("   flask run")
    print("3. Run the test script:")
    print("   python scripts/test.py")

if __name__ == "__main__":
    setup_environment()
