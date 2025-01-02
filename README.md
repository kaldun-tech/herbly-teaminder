# herbly-teaminder
This app helps users make a great cup of loose-leaf tea

## Architecture
This app is meant to run on AWS infrastructure
- Amazon DynamoDB implements the tea database
- Python Flask framework implements the app
- Amazon RDS Postgres implements the user database. Tea database may migrate to RDS in the future

## Set up AWS Credentials

This application uses AWS DynamoDB as its database. You'll need to set up AWS credentials to run the application. Here's how:

1. Get your AWS credentials:
   - Log into the [AWS Management Console](https://aws.amazon.com/console/)
   - Go to IAM (Identity and Access Management)
   - Create a new user or select an existing one
   - Under "Security credentials", create an access key
   - Save both the Access Key ID and Secret Access Key

2. Set up your credentials using one of these methods:

   a. Using environment variables directly:
   ```bash
   # PowerShell
   $env:AWS_ACCESS_KEY_ID = "your_access_key_id"
   $env:AWS_SECRET_ACCESS_KEY = "your_secret_access_key"

   # Bash
   export AWS_ACCESS_KEY_ID="your_access_key_id"
   export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
   ```

   b. Using the provided scripts:
   ```bash
   # PowerShell
   ./scripts/set_env.ps1

   # Bash
   source ./scripts/set_env.sh
   ```
   
   c. Using a .env file:
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env with your credentials
   # Then the application will automatically load them
   ```

3. Verify your credentials are working:
   ```bash
   # Run the application
   python run.py
   
   # Make a test request
   curl http://localhost:5000/api/teas
   ```

Note: Never commit your actual AWS credentials to version control. The `.env` file and credential scripts are included in `.gitignore`.

# Virtual Environment and Dependencies
- Create virtual environment: `python -m venv myenv`
- Activate on Linux: `source myenv/bin/activate`
- On Windows: `myenv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Freeze and write dependencies to file: `pip freeze > requirements.txt`
- Deactivate: `deactivate`

# Run
- Execute `python manage.py`
- Navigate to `http://127.0.0.1:5000` in your browser

# Deployment
- Starting with AWS Elastic Beanstalk
- Amazon Cognito for user authentication
- Look into using ECS with Fargate at 100+ user scale

# Pylint
Check code quality: `python -m pylint **/*.py`

# Testing
Run tests: `pytest tests/`
