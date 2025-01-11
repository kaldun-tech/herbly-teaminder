"""API test script for the Herbly TeaMinder application."""
import os
import sys
import time
import subprocess
from pathlib import Path
import requests
from requests.exceptions import RequestException, Timeout

# Constants
REQUEST_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

def wait_for_server(url, max_attempts=30, delay=1):
    """Wait for server to be ready."""
    print(f"Waiting for server at {url}")
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                print("Server is ready!")
                return True
            print(f"Server not ready (status {response.status_code}), retrying...")
        except (RequestException, Timeout) as err:
            print(f"Error connecting to server (attempt {attempt + 1}/{max_attempts}): {err}")
        time.sleep(delay)
    return False

def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=REQUEST_TIMEOUT)
        is_success = response.status_code == 200
        print(f"Health check {'succeeded' if is_success else 'failed'}")
        return is_success
    except (RequestException, Timeout) as err:
        print(f"Health check failed: {err}")
        return False

def test_user_registration(base_url, username, email, password):
    """Test user registration endpoint."""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        is_success = response.status_code == 201
        print(f"User registration {'succeeded' if is_success else 'failed'}")
        return is_success
    except (RequestException, Timeout) as err:
        print(f"User registration failed: {err}")
        return False

def test_user_login(base_url, username, password):
    """Test user login endpoint."""
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        is_success = response.status_code == 200
        print(f"User login {'succeeded' if is_success else 'failed'}")
        return is_success
    except (RequestException, Timeout) as err:
        print(f"User login failed: {err}")
        return False

def run_flask_server():
    """Run the Flask server in a subprocess."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        env = os.environ.copy()
        env["FLASK_APP"] = "app"
        env["FLASK_ENV"] = "development"

        # Start Flask server
        with subprocess.Popen(
            ["flask", "run"],
            cwd=str(project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as server:
            # Wait a bit for server to start
            time.sleep(2)
            return server
    except subprocess.SubprocessError as err:
        print(f"Failed to start Flask server: {err}")
        return None

def stop_flask_server(server):
    """Stop the Flask server subprocess."""
    if server:
        try:
            server.terminate()
            stdout, stderr = server.communicate(timeout=5)
            with open("flask_server.log", "w", encoding="utf-8") as log_file:
                log_file.write("=== STDOUT ===\n")
                log_file.write(stdout.decode())
                log_file.write("\n=== STDERR ===\n")
                log_file.write(stderr.decode())
        except subprocess.TimeoutExpired:
            server.kill()
            print("Had to force kill Flask server")

def main():
    """Main test function."""
    base_url = "http://localhost:5000"
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

    # Start server
    server = run_flask_server()
    if not server:
        print("Failed to start server")
        return False

    try:
        # Wait for server to be ready
        if not wait_for_server(f"{base_url}/health"):
            print("Server failed to start")
            return False

        # Run tests
        tests = [
            lambda: test_health_endpoint(base_url),
            lambda: test_user_registration(base_url, **test_user),
            lambda: test_user_login(base_url, test_user["username"], test_user["password"])
        ]

        test_results = all(test() for test in tests)
        print(f"\nAll tests {'passed' if test_results else 'failed'}!")
        return test_results

    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return False
    finally:
        stop_flask_server(server)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
