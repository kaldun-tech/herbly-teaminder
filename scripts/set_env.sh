#!/bin/bash
# Bash script to set AWS environment variables
# Replace the placeholder values with your actual AWS credentials from the AWS Management Console
# To run: source ./set_env.sh

export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"

# Optional: Change the region if you're not using us-east-1
export AWS_DEFAULT_REGION="us-east-1"

echo "AWS environment variables have been set for this session."
echo "Access Key ID: $AWS_ACCESS_KEY_ID"
echo "Region: $AWS_DEFAULT_REGION"
