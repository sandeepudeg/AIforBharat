# AWS Deployment Checklist

Use this checklist to ensure all steps are completed for AWS deployment and testing.

## Pre-Deployment Setup

### AWS Account & Credentials
- [ ] AWS account created at https://aws.amazon.com
- [ ] IAM user created with programmatic access
- [ ] Access Key ID and Secret Access Key obtained
- [ ] AWS CLI installed (`aws --version` works)
- [ ] AWS credentials configured (`aws configure`)
- [ ] Credentials verified (`aws sts get-caller-identity` works)

### Local Environment
- [ ] Python 3.9+ installed
- [ ] Project dependencies installed (`pip install -r requirements.txt`)
- [ ] boto3 installed (`pip install boto3`)
- [ ] `.env` file created in project root
- [ ] All required environment variables set in `.env`

## AWS Resource Creation

### DynamoDB Tables
- [ ] `forecasts` table created
- [ ] `inventory` table created
- [ ] `anomalies` table created
- [ ] `purchase_orders` table created
- [ ] `suppliers` table created
- [ ] All tables verified with `aws dynamodb list-tables`

### S3 Bucket
- [ ] S3 bucket created
- [ ] Bucket name noted in `.env` as `S3_BUCKET`
- [ ] Versioning enabled on bucket
- [ ] Bucket verified with `aws s3 ls`

### SNS Topic
- [ ] SNS topic created
- [ ] Topic ARN noted in `.env` as `SNS_TOPIC_ARN`
- [ ] Email subscription added to topic
- [ ] Subscription confirmed (check email)
- [ ] Topic verified with `aws sns list-topics`

### IAM Role (for Lambda)
- [ ] IAM role `supply-chain-lambda-role` created
- [ ] AmazonDynamoDBFullAccess policy attached
- [ ] AmazonS3FullAccess policy attached
- [ ] AmazonSNSFullAccess policy attached
- [ ] CloudWatchLogsFullAccess policy attached
- [ ] Role verified with `aws iam get-role`

### RDS Database (Optional)
- [ ] RDS instance created (if using RDS)
- [ ] Database endpoint noted in `.env` as `RDS_HOST`
- [ ] Database credentials set in `.env`
- [ ] Security group allows inbound on port 5432
- [ ] Database schema created (`psql ... -f src/database/schema.sql`)
- [ ] Tables verified with `psql ... -c "\dt"`

## Configuration

### Environment Variables
- [ ] `AWS_REGION` set (e.g., `us-east-1`)
- [ ] `AWS_ACCESS_KEY_ID` set
- [ ] `AWS_SECRET_ACCESS_KEY` set
- [ ] `DYNAMODB_FORECASTS_TABLE` set to `forecasts`
- [ ] `DYNAMODB_INVENTORY_TABLE` set to `inventory`
- [ ] `DYNAMODB_ANOMALIES_TABLE` set to `anomalies`
- [ ] `DYNAMODB_PURCHASE_ORDERS_TABLE` set to `purchase_orders`
- [ ] `DYNAMODB_SUPPLIERS_TABLE` set to `suppliers`
- [ ] `S3_BUCKET` set to bucket name
- [ ] `S3_REGION` set to `us-east-1`
- [ ] `SNS_TOPIC_ARN` set to topic ARN
- [ ] `ENVIRONMENT` set to `production`
- [ ] `LOG_LEVEL` set to `INFO`

### Optional RDS Configuration
- [ ] `RDS_HOST` set (if using RDS)
- [ ] `RDS_PORT` set to `5432` (if using RDS)
- [ ] `RDS_DATABASE` set (if using RDS)
- [ ] `RDS_USER` set (if using RDS)
- [ ] `RDS_PASSWORD` set (if using RDS)

## Testing

### Individual Service Tests
- [ ] DynamoDB test passes: `python test_aws_dynamodb.py`
- [ ] S3 test passes: `python test_aws_s3.py`
- [ ] SNS test passes: `python test_aws_sns.py`
- [ ] RDS test passes: `python test_aws_rds.py` (if using RDS)

### Integration Tests
- [ ] All integration tests pass: `pytest test_aws_integration.py -v`
- [ ] Demand forecasting test passes
- [ ] Inventory optimization test passes
- [ ] Supplier coordination test passes
- [ ] Anomaly detection test passes
- [ ] Report generation test passes
- [ ] End-to-end workflow test passes

### Demo Test
- [ ] Demo runs successfully: `python demo.py`
- [ ] All 6 demonstrations complete without errors
- [ ] Output shows successful agent execution

### Local Tests (Regression)
- [ ] All local tests still pass: `pytest supply-chain-optimizer/tests/ -v`
- [ ] Code coverage maintained at 74%+
- [ ] No new test failures introduced

## Deployment (Optional)

### Lambda Function
- [ ] Lambda function package created
- [ ] Lambda function deployed to AWS
- [ ] Lambda function tested with test event
- [ ] Lambda function logs visible in CloudWatch

### EventBridge Scheduling
- [ ] EventBridge rule created for daily execution
- [ ] Lambda function added as target
- [ ] Rule enabled and tested
- [ ] Execution history visible in EventBridge

### CloudWatch Monitoring
- [ ] CloudWatch dashboard created
- [ ] Key metrics configured
- [ ] Alarms configured for critical metrics
- [ ] Log groups created for Lambda
- [ ] Log retention set to 30 days

## Monitoring & Maintenance

### CloudWatch Logs
- [ ] Lambda logs accessible: `aws logs tail /aws/lambda/supply-chain-optimizer`
- [ ] No error messages in logs
- [ ] Performance metrics within expected ranges

### AWS Resources
- [ ] DynamoDB tables have data
- [ ] S3 bucket contains reports
- [ ] SNS topic has active subscriptions
- [ ] Lambda function executes on schedule

### Cost Monitoring
- [ ] AWS Billing dashboard reviewed
- [ ] Estimated monthly cost within budget (~$18)
- [ ] Cost alerts configured
- [ ] Unused resources identified and removed

## Security

### Credentials
- [ ] AWS credentials stored securely (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] No credentials in git history
- [ ] Access keys rotated regularly

### Permissions
- [ ] IAM policies follow least privilege principle
- [ ] Only required permissions granted
- [ ] No wildcard (*) permissions used
- [ ] Regular access review scheduled

### Encryption
- [ ] S3 bucket encryption enabled (optional)
- [ ] RDS encryption enabled (if using RDS)
- [ ] DynamoDB encryption enabled (optional)
- [ ] SNS encryption enabled (optional)

### Backups
- [ ] RDS automated backups enabled (if using RDS)
- [ ] S3 versioning enabled
- [ ] Backup retention policy set
- [ ] Backup restoration tested

## Documentation

### Setup Documentation
- [ ] AWS_TESTING_README.md reviewed
- [ ] AWS_TESTING_QUICK_START.md reviewed
- [ ] AWS_DEPLOYMENT_GUIDE.md reviewed
- [ ] AWS_DEPLOYMENT_CHECKLIST.md (this file) completed

### Runbooks
- [ ] Troubleshooting guide reviewed
- [ ] Common issues documented
- [ ] Resolution steps documented
- [ ] Support contacts documented

### Team Documentation
- [ ] Team trained on AWS setup
- [ ] Team trained on testing procedures
- [ ] Team trained on monitoring
- [ ] Team trained on troubleshooting

## Post-Deployment

### Verification
- [ ] All tests passing in AWS environment
- [ ] Demo runs successfully with AWS services
- [ ] Agents execute correctly with AWS data
- [ ] Alerts and notifications working

### Performance
- [ ] Response times acceptable
- [ ] No timeout errors
- [ ] No throttling errors
- [ ] Resource utilization within limits

### Monitoring
- [ ] CloudWatch dashboards active
- [ ] Alarms configured and tested
- [ ] Log aggregation working
- [ ] Metrics collection working

### Maintenance Schedule
- [ ] Daily: Review CloudWatch logs
- [ ] Weekly: Check AWS costs
- [ ] Monthly: Review performance metrics
- [ ] Quarterly: Security audit
- [ ] Annually: Disaster recovery test

## Rollback Plan

### If Issues Occur
- [ ] Identify root cause
- [ ] Check CloudWatch logs
- [ ] Verify AWS credentials
- [ ] Verify environment variables
- [ ] Check AWS resource status
- [ ] Review recent changes
- [ ] Rollback to previous version if needed

### Rollback Steps
- [ ] Stop Lambda execution
- [ ] Disable EventBridge rule
- [ ] Revert to previous Lambda version
- [ ] Verify local tests still pass
- [ ] Re-enable after fix

## Sign-Off

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] All documentation reviewed
- [ ] Team trained and ready
- [ ] Deployment approved by: ________________
- [ ] Date: ________________

## Notes

Use this section to document any issues, workarounds, or special configurations:

```
[Add notes here]
```

## Quick Reference

### Setup Commands
```bash
# Configure AWS
aws configure

# Create resources
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux

# Test services
python test_aws_dynamodb.py
python test_aws_s3.py
python test_aws_sns.py

# Run integration tests
pytest test_aws_integration.py -v

# Run demo
python demo.py
```

### Verification Commands
```bash
# Check credentials
aws sts get-caller-identity

# List resources
aws dynamodb list-tables --region us-east-1
aws s3 ls
aws sns list-topics --region us-east-1

# View logs
aws logs tail /aws/lambda/supply-chain-optimizer --follow

# Check costs
aws ce get-cost-and-usage --time-period Start=2025-12-01,End=2025-12-31 --granularity MONTHLY --metrics BlendedCost
```

### Cleanup Commands
```bash
# Delete resources
aws dynamodb delete-table --table-name forecasts --region us-east-1
aws s3 rb s3://supply-chain-reports-XXXXX --force
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
aws iam delete-role --role-name supply-chain-lambda-role
```

---

**Last Updated**: December 20, 2025
**Version**: 1.0
**Status**: Ready for Deployment
