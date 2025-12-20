# How to Run Tests

## Run All Tests

```bash
pytest tests/ -v
```

## Run Specific Test File

```bash
pytest tests/test_demand_forecasting_agent.py -v
```

## Run Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

## Run Property-Based Tests Only

```bash
pytest tests/ -k "property" -v
```

## Run Integration Tests

```bash
pytest tests/test_aws_integration.py -v
```

## Run AWS Service Tests

```bash
# Test DynamoDB
python test_aws_dynamodb.py

# Test S3
python test_aws_s3.py

# Test SNS
python test_aws_sns.py

# Test RDS
python test_aws_rds.py
```

## Run the Main Workflow with AWS Services

```bash
python run_with_aws_services.py
```

## Run the Demo (with dummy data)

```bash
python demo.py
```

## Common Issues

### Error: "No module named 'src'"
Make sure you're in the project root directory:
```bash
cd supply-chain-optimizer
```

### Error: "ModuleNotFoundError"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Error: "NameError: name 'null' is not defined"
Don't run `python -m src.test` - that file doesn't exist.
Use the commands above instead.

## Test Results

Expected output:
```
======================== 669 passed in 15.23s ========================
```

All tests should pass with 74% code coverage.
