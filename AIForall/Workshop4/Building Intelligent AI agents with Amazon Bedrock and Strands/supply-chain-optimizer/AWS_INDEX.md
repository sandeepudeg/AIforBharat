# AWS Resources Index

Quick navigation guide for all AWS testing and deployment resources.

## Start Here

**New to AWS testing?** Start with one of these:

1. **[AWS_SETUP_SUMMARY.md](AWS_SETUP_SUMMARY.md)** - 5-minute overview
2. **[AWS_TESTING_QUICK_START.md](AWS_TESTING_QUICK_START.md)** - Quick reference
3. **[AWS_TESTING_README.md](AWS_TESTING_README.md)** - Comprehensive guide

## Test Scripts

### Individual Service Tests

| Script | Purpose | Run | Time |
|--------|---------|-----|------|
| [test_aws_dynamodb.py](test_aws_dynamodb.py) | Test DynamoDB connectivity | `python test_aws_dynamodb.py` | 2 min |
| [test_aws_s3.py](test_aws_s3.py) | Test S3 connectivity | `python test_aws_s3.py` | 2 min |
| [test_aws_sns.py](test_aws_sns.py) | Test SNS connectivity | `python test_aws_sns.py` | 2 min |
| [test_aws_rds.py](test_aws_rds.py) | Test RDS connectivity (optional) | `python test_aws_rds.py` | 2 min |

### Integration Tests

| Script | Purpose | Run | Time |
|--------|---------|-----|------|
| [test_aws_integration.py](test_aws_integration.py) | Complete workflow tests | `pytest test_aws_integration.py -v` | 5 min |

## Setup Scripts

### Automated Resource Creation

| Script | Platform | Run | Time |
|--------|----------|-----|------|
| [setup_aws_resources.sh](setup_aws_resources.sh) | macOS/Linux | `./setup_aws_resources.sh` | 5 min |
| [setup_aws_resources.bat](setup_aws_resources.bat) | Windows | `setup_aws_resources.bat` | 5 min |

## Documentation

### Quick References

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [AWS_SETUP_SUMMARY.md](AWS_SETUP_SUMMARY.md) | Quick overview and getting started | 5 min |
| [AWS_TESTING_QUICK_START.md](AWS_TESTING_QUICK_START.md) | Fast setup for experienced users | 10 min |
| [AWS_INDEX.md](AWS_INDEX.md) | This navigation guide | 5 min |

### Comprehensive Guides

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [AWS_TESTING_README.md](AWS_TESTING_README.md) | Complete setup and testing guide | 30 min |
| [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) | Production deployment guide | 45 min |
| [AWS_TESTING_RESOURCES.md](AWS_TESTING_RESOURCES.md) | Overview of all resources | 15 min |

### Checklists

| Document | Purpose | Use When |
|----------|---------|----------|
| [AWS_DEPLOYMENT_CHECKLIST.md](AWS_DEPLOYMENT_CHECKLIST.md) | Deployment verification | Before going to production |

## Quick Start Paths

### Path 1: Quick Testing (30 minutes)

1. Read: [AWS_SETUP_SUMMARY.md](AWS_SETUP_SUMMARY.md) (5 min)
2. Run: `aws configure` (5 min)
3. Run: Setup script (5 min)
4. Run: Test scripts (10 min)
5. Run: `python demo.py` (5 min)

### Path 2: Comprehensive Setup (1 hour)

1. Read: [AWS_TESTING_README.md](AWS_TESTING_README.md) (30 min)
2. Run: `aws configure` (5 min)
3. Run: Setup script (5 min)
4. Run: All tests (15 min)
5. Review: [AWS_DEPLOYMENT_CHECKLIST.md](AWS_DEPLOYMENT_CHECKLIST.md) (5 min)

### Path 3: Production Deployment (2 hours)

1. Read: [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) (45 min)
2. Run: Setup script (5 min)
3. Run: All tests (15 min)
4. Deploy: Lambda functions (30 min)
5. Configure: EventBridge (15 min)
6. Verify: [AWS_DEPLOYMENT_CHECKLIST.md](AWS_DEPLOYMENT_CHECKLIST.md) (30 min)

## Test Execution Guide

### Run All Tests

```bash
# Individual service tests
python test_aws_dynamodb.py
python test_aws_s3.py
python test_aws_sns.py

# Integration tests
pytest test_aws_integration.py -v

# Demo
python demo.py
```

### Run Specific Tests

```bash
# DynamoDB only
python test_aws_dynamodb.py

# S3 only
python test_aws_s3.py

# SNS only
python test_aws_sns.py

# Specific integration test class
pytest test_aws_integration.py::TestDemandForecastingWithAWS -v

# End-to-end workflow only
pytest test_aws_integration.py::TestEndToEndWorkflow -v -s
```

## Troubleshooting Guide

### Issue: "Unable to locate credentials"
**Solution**: See [AWS_TESTING_README.md](AWS_TESTING_README.md#troubleshooting) - Credentials section

### Issue: "ResourceNotFoundException"
**Solution**: See [AWS_TESTING_README.md](AWS_TESTING_README.md#troubleshooting) - ResourceNotFoundException section

### Issue: "AccessDenied"
**Solution**: See [AWS_TESTING_README.md](AWS_TESTING_README.md#troubleshooting) - AccessDenied section

### Issue: Tests fail but local tests pass
**Solution**: See [AWS_TESTING_README.md](AWS_TESTING_README.md#troubleshooting) - Tests fail section

## AWS Resources Created

### DynamoDB Tables
- `forecasts` - Demand forecasts
- `inventory` - Inventory levels
- `anomalies` - Detected anomalies
- `purchase_orders` - Purchase orders
- `suppliers` - Supplier information

### S3 Bucket
- `supply-chain-reports-XXXXX` - Reports and archives

### SNS Topic
- `supply-chain-alerts` - Alert notifications

### IAM Role
- `supply-chain-lambda-role` - Lambda execution role

## Environment Configuration

### Required Variables
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
DYNAMODB_FORECASTS_TABLE=forecasts
DYNAMODB_INVENTORY_TABLE=inventory
DYNAMODB_ANOMALIES_TABLE=anomalies
DYNAMODB_PURCHASE_ORDERS_TABLE=purchase_orders
DYNAMODB_SUPPLIERS_TABLE=suppliers
S3_BUCKET=supply-chain-reports-XXXXX
S3_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Optional Variables
```bash
RDS_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=supply_chain
RDS_USER=admin
RDS_PASSWORD=your_password
```

## Cost Estimation

| Service | Cost |
|---------|------|
| DynamoDB | $0.25/month |
| S3 | $2.30/month |
| SNS | $0.50/month |
| RDS (optional) | $10/month |
| Lambda (optional) | $0.20/month |
| CloudWatch | $5/month |
| **Total** | **~$18/month** |

## File Organization

```
supply-chain-optimizer/
├── Test Scripts
│   ├── test_aws_dynamodb.py
│   ├── test_aws_s3.py
│   ├── test_aws_sns.py
│   ├── test_aws_rds.py
│   └── test_aws_integration.py
├── Setup Scripts
│   ├── setup_aws_resources.sh
│   └── setup_aws_resources.bat
└── Documentation
    ├── AWS_INDEX.md (this file)
    ├── AWS_SETUP_SUMMARY.md
    ├── AWS_TESTING_QUICK_START.md
    ├── AWS_TESTING_README.md
    ├── AWS_TESTING_RESOURCES.md
    ├── AWS_DEPLOYMENT_GUIDE.md
    └── AWS_DEPLOYMENT_CHECKLIST.md
```

## Quick Commands Reference

```bash
# Setup
aws configure
setup_aws_resources.bat  # Windows
./setup_aws_resources.sh # macOS/Linux

# Test
python test_aws_dynamodb.py
python test_aws_s3.py
python test_aws_sns.py
pytest test_aws_integration.py -v

# Demo
python demo.py

# Monitor
aws logs tail /aws/lambda/supply-chain-optimizer --follow

# List resources
aws dynamodb list-tables --region us-east-1
aws s3 ls
aws sns list-topics --region us-east-1

# Cleanup
aws dynamodb delete-table --table-name forecasts --region us-east-1
aws s3 rb s3://supply-chain-reports-XXXXX --force
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:supply-chain-alerts
```

## Support Resources

### Internal Documentation
- [AWS_TESTING_README.md](AWS_TESTING_README.md) - Comprehensive guide
- [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) - Production deployment
- [AWS_DEPLOYMENT_CHECKLIST.md](AWS_DEPLOYMENT_CHECKLIST.md) - Verification

### External Resources
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
- [SNS Documentation](https://docs.aws.amazon.com/sns/)
- [RDS User Guide](https://docs.aws.amazon.com/rds/)
- [Lambda Documentation](https://docs.aws.amazon.com/lambda/)

## Status

### ✓ Complete
- All test scripts created and ready
- All setup scripts created and ready
- All documentation created and complete
- AWS resources can be created automatically
- Integration tests ready to run
- Demo ready to run with AWS

### Ready for
- AWS testing and validation
- Production deployment
- Monitoring and maintenance
- Cost optimization

## Next Steps

1. **Choose your path** above (Quick Testing, Comprehensive, or Production)
2. **Read the appropriate guide** for your path
3. **Run the setup script** to create AWS resources
4. **Run the tests** to verify connectivity
5. **Run the demo** to see everything working

---

**Created**: December 20, 2025
**Version**: 1.0
**Status**: Complete and Ready for Use

For questions or issues, refer to the troubleshooting sections in [AWS_TESTING_README.md](AWS_TESTING_README.md).
