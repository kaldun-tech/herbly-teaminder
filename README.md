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
   
   Copy the template scripts to your home directory:

   ```bash
   # Linux/Mac (~/.aws/set_env.sh)
   mkdir -p ~/.aws
   cp scripts/templates/aws_credentials.sh.template ~/.aws/set_env.sh
   chmod 600 ~/.aws/set_env.sh  # Restrict permissions
   
   # Edit the file with your credentials
   nano ~/.aws/set_env.sh
   
   # Source the file
   source ~/.aws/set_env.sh
   ```

   ```powershell
   # Windows ($HOME\.aws\set_env.ps1)
   New-Item -ItemType Directory -Force -Path "$HOME\.aws"
   Copy-Item scripts\templates\aws_credentials.ps1.template "$HOME\.aws\set_env.ps1"
   
   # Edit the file with your credentials
   notepad $HOME\.aws\set_env.ps1
   
   # Source the file
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
- Template files (safe to commit):
  - `scripts/templates/aws_credentials.sh.template`
  - `scripts/templates/aws_credentials.ps1.template`

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

## Database Setup and Security

### Development Setup (SQLite)

1. **Environment Configuration**:
   ```bash
   # Create and edit .env file (never commit to version control)
   FLASK_APP=app:create_app
   FLASK_ENV=development
   DATABASE_URL=sqlite:///dev.db
   SECRET_KEY=your-dev-secret-key
   ```

2. **Initialize Database**:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file with:
   FLASK_APP=app:create_app
   FLASK_ENV=development
   DATABASE_URL=sqlite:///dev.db
   SECRET_KEY=your-dev-secret-key

   # Initialize database and run migrations
   flask init-db
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade

   # Freeze and write dependencies to file:
   pip freeze > requirements.txt

   # Deactivate environment when done
   deactivate
   ```

### Production Setup (PostgreSQL)

1. **Install PostgreSQL**:
   - Download and install from [postgresql.org](https://www.postgresql.org/download/)
   - Keep track of the superuser (postgres) password during installation

2. **Create Database and User**:
   ```sql
   -- Connect as postgres user
   psql -U postgres

   -- Create database
   CREATE DATABASE teaminder;

   -- Create application user with limited permissions
   CREATE USER teaminder_user WITH PASSWORD 'strong_password';

   -- Grant necessary permissions
   GRANT CONNECT ON DATABASE teaminder TO teaminder_user;
   GRANT USAGE ON SCHEMA public TO teaminder_user;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO teaminder_user;
   GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO teaminder_user;

   -- Set default privileges for future tables
   ALTER DEFAULT PRIVILEGES IN SCHEMA public 
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO teaminder_user;
   ```

3. **Security Configuration**:
   ```bash
   # Production .env (never commit to version control)
   FLASK_ENV=production
   FLASK_APP=app
   DATABASE_URL=postgresql://teaminder_user:strong_password@localhost:5432/teaminder
   SECRET_KEY=your-production-secret-key  # Use a strong random key
   ```

### Database Security Best Practices

1. **Access Control**:
   - Use separate users for development and production
   - Grant minimum necessary permissions
   - Never use the postgres superuser in application code
   - Regularly audit database access

2. **Password Security**:
   - Use strong, unique passwords
   - Store passwords securely (use environment variables)
   - Rotate passwords regularly
   - Never commit passwords to version control

3. **Connection Security**:
   - Use SSL/TLS for database connections
   - Limit database access to specific IP addresses
   - Configure proper firewall rules
   - Monitor and log database access

4. **Backup and Recovery**:
   ```bash
   # Backup database (PostgreSQL)
   pg_dump -U teaminder_user -d teaminder > backup.sql

   # Restore database
   psql -U teaminder_user -d teaminder < backup.sql
   ```

5. **Data Migration**:
   ```bash
   # Create new migration
   flask db migrate -m "Description of changes"

   # Review migration file in migrations/versions/
   # Apply migration
   flask db upgrade

   # Rollback if needed
   flask db downgrade
   ```

### Testing Database

The test configuration uses SQLite in-memory database for fast, isolated tests:
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

### Monitoring and Maintenance

1. **Check Database Status**:
   ```sql
   -- Check active connections
   SELECT * FROM pg_stat_activity;

   -- Check table sizes
   SELECT pg_size_pretty(pg_total_relation_size('table_name'));
   ```

2. **Regular Maintenance**:
   ```sql
   -- Analyze tables for query optimization
   ANALYZE table_name;

   -- Remove bloat and reclaim space
   VACUUM FULL table_name;
   ```

3. **Performance Optimization**:
   - Monitor query performance
   - Create indexes for frequently queried columns
   - Regularly update table statistics
   - Configure connection pooling

## Security Features

### Rate Limiting
The application implements rate limiting to prevent abuse with both Global limits and Endpoint-specific limits (per IP)

### Security Headers
The application uses Flask-Talisman to implement security headers:

- Forces HTTPS connections
- Implements HTTP Strict Transport Security (HSTS)
- Sets secure session cookies
- Implements Content Security Policy (CSP)
- Protects against XSS and CSRF attacks

### Input Validation
- Strict validation on all input fields
- Length limits on text fields
- Type checking for all fields
- Range validation for numeric values

### AWS Security
- Uses AWS IAM roles with least privilege principle
- Implements OIDC (OpenID Connect) for secure, keyless authentication in GitHub Actions
- No long-term credentials stored in GitHub Secrets
- No sensitive information in code or configuration files

### GitHub Actions Security
- Uses OIDC for secure AWS authentication
- Temporary credentials generated for each workflow run
- Better audit trail through AWS CloudTrail
- Follows security best practices for CI/CD

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
