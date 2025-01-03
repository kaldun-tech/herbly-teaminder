# herbly-teaminder
This app helps users make a great cup of loose-leaf tea

## Architecture
This app is meant to run on AWS infrastructure
- Amazon DynamoDB implements the tea database
- Python Flask framework implements the app
- Amazon RDS Postgres implements the user database. Tea database may migrate to RDS in the future

## AWS Credentials and Security

This application uses AWS best practices for security and credentials management:

### Local Development
For local development, you have three options to set up AWS credentials:

1. **Environment Variables** (Recommended for testing):
   
   Create credential scripts in your home directory:

   ```bash
   # Linux/Mac (~/.aws/set_env.sh)
   mkdir -p ~/.aws
   cp scripts/set_env.sh ~/.aws/
   chmod 600 ~/.aws/set_env.sh  # Restrict permissions
   source ~/.aws/set_env.sh
   ```

   ```powershell
   # Windows ($HOME\.aws\set_env.ps1)
   New-Item -ItemType Directory -Force -Path "$HOME\.aws"
   Copy-Item scripts\set_env.ps1 "$HOME\.aws\"
   . $HOME\.aws\set_env.ps1
   ```

2. **AWS CLI Configuration** (Alternative approach):
   ```bash
   aws configure
   # AWS credentials will be stored in ~/.aws/credentials
   ```

3. **.env File** (For project-specific settings):
   ```bash
   cp .env.template .env
   # Edit .env with NON-SENSITIVE environment variables
   # Do not store AWS credentials here
   ```

### Credential File Security
- Store credential files outside the project directory
- Use restricted permissions (600 on Unix systems)
- Never commit credential files to version control
- Keep different credentials for different projects
- Location of credential files:
  - Linux/Mac: `~/.aws/set_env.sh`
  - Windows: `%USERPROFILE%\.aws\set_env.ps1`

### Production Deployment
In production (Elastic Beanstalk), the application uses IAM roles instead of explicit credentials:

1. **IAM Instance Profile**:
   - The application uses `ec2-dynamodb-elasticbeanstalk-instance-profile`
   - This provides secure, automatic access to AWS services
   - No need to set AWS credentials manually

2. **Sensitive Data**:
   If you need to store sensitive data (not AWS credentials):
   - Use Elastic Beanstalk Environment Properties:
     1. Go to EB Console → Your Environment
     2. Configuration → Software
     3. Environment Properties section
     4. Add key-value pairs
   - Values are:
     - Encrypted at rest
     - Not visible in logs
     - Easy to rotate

3. **Security Best Practices**:
   - Never commit credentials to version control
   - Don't store credentials in EC2 user data or .bashrc
   - Use IAM roles and instance profiles
   - Rotate credentials regularly
   - Use least-privilege permissions

### Troubleshooting
If you encounter permission issues:
1. Check IAM role permissions
2. Verify instance profile attachment
3. Check CloudWatch logs for access denied errors

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
