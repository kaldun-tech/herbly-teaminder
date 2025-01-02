# PowerShell script to set AWS environment variables
# Replace the placeholder values with your actual AWS credentials from the AWS Management Console
# To run: .\set_env.ps1

$env:AWS_ACCESS_KEY_ID = "your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY = "your_secret_access_key"

# Optional: Change the region if you're not using us-east-1
$env:AWS_DEFAULT_REGION = "us-east-1"

Write-Host "AWS environment variables have been set for this session."
Write-Host "Access Key ID: $env:AWS_ACCESS_KEY_ID"
Write-Host "Region: $env:AWS_DEFAULT_REGION"
