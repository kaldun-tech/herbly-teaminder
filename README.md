# herbly-teaminder
This app helps users make a great cup of loose-leaf tea

## Architecture
This app is meant to run on AWS infrastructure
- Amazon DynamoDB implements the tea database
- Python Flask framework implements the app
- Amazon RDS Postgres implements the user database. Tea database may migrate to RDS in the future

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
