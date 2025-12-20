@echo off
REM AWS Resource Setup Script for Supply Chain Optimizer (Windows)
REM This script creates all necessary AWS resources for testing and deployment

setlocal enabledelayedexpansion

REM Configuration
set REGION=us-east-1
set ENVIRONMENT=development

echo.
echo ========================================
echo AWS Resource Setup for Supply Chain Optimizer
echo ========================================
echo.
echo Region: %REGION%
echo Environment: %ENVIRONMENT%
echo.

REM Check AWS CLI is installed
aws --version >nul 2>&1
if errorlevel 1 (
    echo Error: AWS CLI is not installed
    echo Install from: https://aws.amazon.com/cli/
    exit /b 1
)

REM Check AWS credentials are configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo Error: AWS credentials not configured
    echo Run: aws configure
    exit /b 1
)

echo Creating DynamoDB tables...
echo.

REM Create Forecasts table
echo Creating forecasts table...
aws dynamodb create-table ^
  --table-name forecasts ^
  --attribute-definitions AttributeName=forecast_id,AttributeType=S ^
  --key-schema AttributeName=forecast_id,KeyType=HASH ^
  --billing-mode PAY_PER_REQUEST ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Table may already exist)

REM Create Inventory table
echo Creating inventory table...
aws dynamodb create-table ^
  --table-name inventory ^
  --attribute-definitions AttributeName=inventory_id,AttributeType=S ^
  --key-schema AttributeName=inventory_id,KeyType=HASH ^
  --billing-mode PAY_PER_REQUEST ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Table may already exist)

REM Create Anomalies table
echo Creating anomalies table...
aws dynamodb create-table ^
  --table-name anomalies ^
  --attribute-definitions AttributeName=anomaly_id,AttributeType=S ^
  --key-schema AttributeName=anomaly_id,KeyType=HASH ^
  --billing-mode PAY_PER_REQUEST ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Table may already exist)

REM Create Purchase Orders table
echo Creating purchase_orders table...
aws dynamodb create-table ^
  --table-name purchase_orders ^
  --attribute-definitions AttributeName=po_id,AttributeType=S ^
  --key-schema AttributeName=po_id,KeyType=HASH ^
  --billing-mode PAY_PER_REQUEST ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Table may already exist)

REM Create Suppliers table
echo Creating suppliers table...
aws dynamodb create-table ^
  --table-name suppliers ^
  --attribute-definitions AttributeName=supplier_id,AttributeType=S ^
  --key-schema AttributeName=supplier_id,KeyType=HASH ^
  --billing-mode PAY_PER_REQUEST ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Table may already exist)

echo [OK] DynamoDB tables created
echo.

REM Create S3 bucket
echo Creating S3 bucket...
for /f "tokens=*" %%a in ('powershell -Command "Get-Date -UFormat %%s"') do set TIMESTAMP=%%a
set BUCKET_NAME=supply-chain-reports-%TIMESTAMP%

aws s3 mb s3://%BUCKET_NAME% --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Bucket may already exist)

REM Enable versioning
aws s3api put-bucket-versioning ^
  --bucket %BUCKET_NAME% ^
  --versioning-configuration Status=Enabled ^
  --region %REGION% >nul 2>&1
if errorlevel 1 echo   (Versioning may already be enabled)

echo [OK] S3 bucket created: %BUCKET_NAME%
echo.

REM Create SNS topic
echo Creating SNS topic...
for /f "tokens=*" %%a in ('aws sns create-topic --name supply-chain-alerts --region %REGION% --query TopicArn --output text') do set TOPIC_ARN=%%a

echo [OK] SNS topic created: %TOPIC_ARN%
echo.

REM Create IAM role for Lambda
echo Creating IAM role for Lambda...
set ROLE_NAME=supply-chain-lambda-role

aws iam get-role --role-name %ROLE_NAME% >nul 2>&1
if errorlevel 1 (
    aws iam create-role ^
      --role-name %ROLE_NAME% ^
      --assume-role-policy-document "{\"Version\": \"2012-10-17\", \"Statement\": [{\"Effect\": \"Allow\", \"Principal\": {\"Service\": \"lambda.amazonaws.com\"}, \"Action\": \"sts:AssumeRole\"}]}" >nul 2>&1
    
    aws iam attach-role-policy ^
      --role-name %ROLE_NAME% ^
      --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess >nul 2>&1
    
    aws iam attach-role-policy ^
      --role-name %ROLE_NAME% ^
      --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess >nul 2>&1
    
    aws iam attach-role-policy ^
      --role-name %ROLE_NAME% ^
      --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess >nul 2>&1
    
    aws iam attach-role-policy ^
      --role-name %ROLE_NAME% ^
      --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess >nul 2>&1
) else (
    echo   (Role already exists)
)

echo [OK] IAM role created: %ROLE_NAME%
echo.

REM Summary
echo ========================================
echo AWS Resources Created Successfully!
echo ========================================
echo.
echo DynamoDB Tables:
echo   - forecasts
echo   - inventory
echo   - anomalies
echo   - purchase_orders
echo   - suppliers
echo.
echo S3 Bucket:
echo   - %BUCKET_NAME%
echo.
echo SNS Topic:
echo   - %TOPIC_ARN%
echo.
echo IAM Role:
echo   - %ROLE_NAME%
echo.
echo Next steps:
echo 1. Update .env file with:
echo    S3_BUCKET=%BUCKET_NAME%
echo    SNS_TOPIC_ARN=%TOPIC_ARN%
echo.
echo 2. Run tests:
echo    python test_aws_dynamodb.py
echo    python test_aws_s3.py
echo    python test_aws_sns.py
echo.
echo 3. Run integration tests:
echo    pytest test_aws_integration.py -v
echo.

endlocal
