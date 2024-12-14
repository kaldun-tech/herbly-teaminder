# herbly-teaminder
This app helps users make a great cup of loose-leaf tea

## Architecture
This app is meant to run on AWS infrastructure
- Amazon DynamoDB implements the tea database
- Python Flask framework implements the app
- React will be used for the front-end

# Virtual Environment and Dependencies
- Create virtual environment: `python -m venv myenv`
- Activate on Linux: `source myenv/bin/activate`
- On Windows: `myenv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`
- Freeze and write dependencies to file: `pip freeze > requirements.txt`
- Deactivate: `deactivate`

# Run
Execute `python3 app/app.py`
Navigate to `http://127.0.0.1:5000` in your browser

# Pylint
Check code quality: `python -m pylint **/*.py`

# Testing
Run tests: `pytest tests/`
