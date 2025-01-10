"""Test script for API endpoints"""
import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

class APITester:
    """Test API endpoints"""
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        self.admin_user = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123"
        }
        
    def wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        print("Waiting for server to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    print("Server is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        print("Server did not become ready in time")
        return False

    def print_result(self, name, success, response=None):
        """Print test result"""
        if success:
            print(f"✓ {name}")
        else:
            print(f"✗ {name}")
            if response:
                print(f"  Status: {response.status_code}")
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Response: {response.text}")

    def test_register(self):
        """Test user registration"""
        print("\n=== Testing Registration ===")
        
        # Test valid registration
        response = self.session.post(
            f"{self.base_url}/register",
            json=self.test_user
        )
        self.print_result("Register new user", response.status_code == 201, response)

        # Test duplicate registration
        response = self.session.post(
            f"{self.base_url}/register",
            json=self.test_user
        )
        self.print_result("Reject duplicate user", response.status_code == 400, response)

    def test_login(self):
        """Test user login"""
        print("\n=== Testing Login ===")
        
        # Test valid login
        response = self.session.post(
            f"{self.base_url}/login",
            json={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        self.print_result("Login with valid credentials", response.status_code == 200, response)

        # Test invalid password
        response = self.session.post(
            f"{self.base_url}/login",
            json={
                "username": self.test_user["username"],
                "password": "wrongpassword"
            }
        )
        self.print_result("Reject invalid password", response.status_code == 401, response)

    def test_profile(self):
        """Test profile access"""
        print("\n=== Testing Profile ===")
        
        # Login first
        self.session.post(
            f"{self.base_url}/login",
            json={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )

        # Test profile access
        response = self.session.get(f"{self.base_url}/profile")
        self.print_result("Access profile when logged in", response.status_code == 200, response)

    def test_logout(self):
        """Test logout"""
        print("\n=== Testing Logout ===")
        
        response = self.session.get(f"{self.base_url}/logout")
        self.print_result("Logout", response.status_code == 200, response)

        # Verify can't access profile after logout
        response = self.session.get(f"{self.base_url}/profile")
        self.print_result("Cannot access profile after logout", response.status_code == 401, response)

    def run_all_tests(self):
        """Run all tests"""
        if not self.wait_for_server():
            print("Could not connect to server. Make sure it's running with 'flask run'")
            return False

        try:
            self.test_register()
            self.test_login()
            self.test_profile()
            self.test_logout()
            print("\n=== All tests completed! ===")
            return True
        except requests.exceptions.ConnectionError:
            print("\n✗ Error: Could not connect to the server.")
            print("Make sure the Flask server is running (flask run)")
            return False
        except Exception as e:
            print(f"\n✗ Error during tests: {str(e)}")
            return False

def ensure_env_setup():
    """Ensure environment is properly set up"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Ensure .env file exists
    if not os.path.exists('.env'):
        print("Creating .env file...")
        env_content = """FLASK_DEBUG=True
FLASK_APP=app:create_app
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=dev-secret-key-CHANGE-IN-PRODUCTION
"""
        with open('.env', 'w') as f:
            f.write(env_content)

    # Ensure database is initialized
    if not os.path.exists('dev.db'):
        print("Initializing database...")
        subprocess.run(['flask', 'init-db'], check=True)

if __name__ == "__main__":
    print("\nStarting API tests...")
    
    try:
        ensure_env_setup()
        tester = APITester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error during test setup: {str(e)}")
        sys.exit(1)
