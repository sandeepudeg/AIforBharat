# Bedrock Knowledge Base Setup Guide

## Overview

This guide walks you through setting up a Bedrock Knowledge Base for the supply chain optimizer.

---

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured
- Python 3.8+
- Supply chain optimizer installed

---

## Step 1: Create Bedrock Knowledge Base

### Option A: Using AWS Console (Recommended)

1. **Go to AWS Console**
   - Navigate to: https://console.aws.amazon.com/bedrock
   - Select your region (e.g., us-east-1)

2. **Create Knowledge Base**
   - Click "Knowledge Bases" in the left menu
   - Click "Create Knowledge Base"
   - Fill in the form:
     - **Name**: `supply-chain-optimizer-kb`
     - **Description**: Supply chain data for optimization
     - **Model**: Claude 3 Sonnet
     - **Storage**: S3 bucket

3. **Configure S3 Storage**
   - Create or select an S3 bucket
   - Bucket name: `supply-chain-kb-data`
   - Region: Same as your Bedrock region

4. **Create Knowledge Base**
   - Click "Create"
   - Wait for creation to complete
   - **Note the Knowledge Base ID** (e.g., `XXXXXXXXXX`)

### Option B: Using AWS CLI

```bash
# Create S3 bucket
aws s3 mb s3://supply-chain-kb-data --region us-east-1

# Create Knowledge Base
aws bedrock create-knowledge-base \
  --name supply-chain-optimizer-kb \
  --description "Supply chain data for optimization" \
  --knowledge-base-configuration \
    storageConfiguration='{
      type=S3,
      s3BucketArn=arn:aws:s3:::supply-chain-kb-data
    }' \
  --region us-east-1
```

---

## Step 2: Prepare Documents

### Option A: Use Setup Script (Easiest)

```bash
# Run the setup wizard
python setup_knowledge_base.py

# Choose option 2: Create sample documents
# This creates JSON files with sample data
```

### Option B: Manual Document Creation

Create these JSON files:

**inventory.json**
```json
[
  {
    "sku": "PROD-001",
    "product_name": "Widget A",
    "current_quantity": 1500,
    "reorder_point": 200,
    "safety_stock": 300,
    "warehouse": "WH-001",
    "lead_time_days": 7,
    "ordering_cost": 50,
    "holding_cost_per_unit": 2,
    "unit_price": 10.50,
    "category": "Electronics"
  }
]
```

**sales_history.json**
```json
[
  {
    "sku": "PROD-001",
    "date": "2025-12-01",
    "quantity": 100,
    "revenue": 1050,
    "warehouse": "WH-001"
  }
]
```

**suppliers.json**
```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Supplies Inc",
    "unit_price": 10.50,
    "reliability_score": 0.95,
    "lead_time_days": 7,
    "min_order_quantity": 100,
    "payment_terms": "Net 30",
    "location": "USA",
    "rating": 4.8
  }
]
```

---

## Step 3: Upload Documents to Knowledge Base

### Option A: Using Setup Script

```bash
# Run the setup wizard
python setup_knowledge_base.py

# Choose option 3: Upload documents to S3
# Enter your S3 bucket name
# Documents will be uploaded automatically
```

### Option B: Using AWS Console

1. Go to your Knowledge Base in AWS Console
2. Click "Upload documents"
3. Select the JSON files
4. Click "Upload"
5. Wait for processing to complete

### Option C: Using AWS CLI

```bash
# Upload to S3
aws s3 cp inventory.json s3://supply-chain-kb-data/supply-chain-data/
aws s3 cp sales_history.json s3://supply-chain-kb-data/supply-chain-data/
aws s3 cp suppliers.json s3://supply-chain-kb-data/supply-chain-data/

# Sync Knowledge Base
aws bedrock sync-knowledge-base \
  --knowledge-base-id XXXXXXXXXX \
  --region us-east-1
```

---

## Step 4: Configure Environment

### Add to .env file

```bash
# Bedrock Knowledge Base
BEDROCK_KB_ID=your_knowledge_base_id

# Example:
# BEDROCK_KB_ID=XXXXXXXXXX
```

### Verify Configuration

```bash
# Check if KB ID is set
echo $BEDROCK_KB_ID

# Should output your KB ID
```

---

## Step 5: Test the Setup

### Test 1: List Knowledge Bases

```bash
python setup_knowledge_base.py

# Choose option 1: List existing knowledge bases
# Should show your KB with status "ACTIVE"
```

### Test 2: Run Orchestrator

```bash
python supply_chain_orchestrator.py

# Ask: "Sync data from knowledge base"
# Should retrieve and store data in DynamoDB
```

### Test 3: Verify Data in DynamoDB

```bash
# Check inventory table
aws dynamodb scan --table-name inventory

# Should show products from KB
```

---

## Troubleshooting

### Issue: "Knowledge Base not found"

**Solution**:
1. Verify KB ID is correct
2. Check KB status is "ACTIVE"
3. Verify region matches

```bash
# List KBs to find correct ID
aws bedrock list-knowledge-bases --region us-east-1
```

### Issue: "No documents found in knowledge base"

**Solution**:
1. Verify documents were uploaded
2. Check S3 bucket has documents
3. Sync knowledge base

```bash
# List S3 objects
aws s3 ls s3://supply-chain-kb-data/supply-chain-data/

# Sync KB
aws bedrock sync-knowledge-base \
  --knowledge-base-id XXXXXXXXXX \
  --region us-east-1
```

### Issue: "Access denied" error

**Solution**:
1. Check AWS credentials in .env
2. Verify IAM permissions
3. Check region configuration

Required IAM permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "s3:*",
        "dynamodb:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Issue: "Bedrock model not available"

**Solution**:
1. Check region supports Bedrock
2. Verify model is available
3. Check service quotas

Supported regions:
- us-east-1
- us-west-2
- eu-west-1
- ap-southeast-1

---

## Document Format Requirements

### Inventory Documents

**Required fields**:
- `sku` (string) - Product SKU
- `current_quantity` (number) - Current stock level
- `reorder_point` (number) - Reorder threshold

**Optional fields**:
- `product_name` (string)
- `warehouse` (string)
- `lead_time_days` (number)
- `ordering_cost` (number)
- `holding_cost_per_unit` (number)
- `unit_price` (number)

### Sales History Documents

**Required fields**:
- `sku` (string) - Product SKU
- `date` (string) - Date in YYYY-MM-DD format
- `quantity` (number) - Quantity sold

**Optional fields**:
- `revenue` (number)
- `warehouse` (string)

### Supplier Documents

**Required fields**:
- `supplier_id` (string) - Supplier ID
- `name` (string) - Supplier name

**Optional fields**:
- `unit_price` (number)
- `reliability_score` (number) - 0-1
- `lead_time_days` (number)
- `min_order_quantity` (number)
- `payment_terms` (string)
- `location` (string)
- `rating` (number)

---

## Workflow

```
1. Create Knowledge Base
   ↓
2. Prepare Documents (JSON)
   ↓
3. Upload to S3
   ↓
4. Sync Knowledge Base
   ↓
5. Set BEDROCK_KB_ID
   ↓
6. Run Orchestrator
   ↓
7. Ask to sync data
   ↓
8. Data stored in DynamoDB
   ↓
9. Use agent tools
```

---

## Quick Commands

### Create KB
```bash
python setup_knowledge_base.py
# Choose option 1 to list existing KBs
```

### Create Documents
```bash
python setup_knowledge_base.py
# Choose option 2 to create sample documents
```

### Upload Documents
```bash
python setup_knowledge_base.py
# Choose option 3 to upload to S3
```

### List KBs
```bash
aws bedrock list-knowledge-bases --region us-east-1
```

### Sync KB
```bash
aws bedrock sync-knowledge-base \
  --knowledge-base-id XXXXXXXXXX \
  --region us-east-1
```

### Test Setup
```bash
python supply_chain_orchestrator.py
# Ask: "Sync data from knowledge base"
```

---

## Next Steps

1. ✅ Create Bedrock Knowledge Base
2. ✅ Prepare documents
3. ✅ Upload to S3
4. ✅ Set BEDROCK_KB_ID
5. ✅ Run orchestrator
6. ✅ Sync data from KB
7. ✅ Use agent tools

---

## Support

For issues:
1. Check troubleshooting section
2. Verify AWS credentials
3. Check KB status in console
4. Review CloudWatch logs
5. Check S3 bucket contents

---

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Knowledge Base API Reference](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)

---

## Summary

You now have:
- ✅ Bedrock Knowledge Base created
- ✅ Sample documents prepared
- ✅ Documents uploaded to S3
- ✅ Environment configured
- ✅ Ready to sync data

Start using the supply chain optimizer!

```bash
python supply_chain_orchestrator.py
```

Ask: "Sync data from knowledge base"
