#!/bin/bash

# AWS Setup Script for Agentic AI Application
# This script creates necessary IAM roles and policies for the application

set -e

# Configuration
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="agentic-ai-role"
POLICY_NAME="agentic-ai-policy"
GITHUB_ORG="your-org"
GITHUB_REPO="your-repo"
REGION="us-east-1"

echo "Setting up AWS infrastructure for Agentic AI..."
echo "Account ID: $ACCOUNT_ID"
echo "Role Name: $ROLE_NAME"
echo "Region: $REGION"

# Create S3 bucket for deployments
echo "Creating S3 bucket for deployments..."
BUCKET_NAME="agentic-ai-deployment-$ACCOUNT_ID"
aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION" \
    2>/dev/null || echo "Bucket already exists"

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

echo "S3 bucket created: $BUCKET_NAME"

# Create IAM role
echo "Creating IAM role..."
TRUST_POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::$ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:$GITHUB_ORG/$GITHUB_REPO:*"
                }
            }
        }
    ]
}
EOF
)

aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document "$TRUST_POLICY" \
    2>/dev/null || echo "Role already exists"

# Attach policy to role
echo "Creating and attaching policy..."
POLICY_DOCUMENT=$(cat <<'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockInvoke",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        },
        {
            "Sid": "S3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::agentic-ai-deployment-*",
                "arn:aws:s3:::agentic-ai-deployment-*/*"
            ]
        },
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/agentic-ai/*"
        }
    ]
}
EOF
)

aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document "$POLICY_DOCUMENT"

echo "IAM role and policy created successfully"

# Create Secrets Manager secrets (optional)
echo "Creating secrets in AWS Secrets Manager..."
aws secretsmanager create-secret \
    --name agentic-ai/bedrock-model-id \
    --secret-string "anthropic.claude-3-5-sonnet-20241022-v2:0" \
    --region "$REGION" \
    2>/dev/null || echo "Secret already exists"

echo "Setup complete!"
echo "Role ARN: arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
echo "S3 Bucket: $BUCKET_NAME"
echo ""
echo "Add the following to your GitHub Secrets:"
echo "AWS_ROLE_ARN=arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"
echo "AWS_REGION=$REGION"
echo "DEPLOYMENT_BUCKET=$BUCKET_NAME"
