# Prepare Your Own Supply Chain Data for Knowledge Base

## Overview

Instead of using dummy data, you can upload your own real supply chain data to the Bedrock Knowledge Base.

---

## Data Files Required

You need to create 3 JSON files with your supply chain data:

1. **inventory.json** - Product inventory information
2. **sales_history.json** - Historical sales data
3. **suppliers.json** - Supplier information

---

## File Format

### 1. inventory.json

**Required fields:**
- `sku` (string) - Product SKU/ID
- `current_quantity` (number) - Current stock level
- `reorder_point` (number) - When to reorder

**Optional fields:**
- `product_name` (string)
- `warehouse` (string)
- `lead_time_days` (number)
- `ordering_cost` (number)
- `holding_cost_per_unit` (number)
- `unit_price` (number)
- `category` (string)
- `safety_stock` (number)

**Example:**
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
  },
  {
    "sku": "PROD-002",
    "product_name": "Widget B",
    "current_quantity": 800,
    "reorder_point": 150,
    "warehouse": "WH-002",
    "unit_price": 15.75
  }
]
```

### 2. sales_history.json

**Required fields:**
- `sku` (string) - Product SKU
- `date` (string) - Date in YYYY-MM-DD format
- `quantity` (number) - Quantity sold

**Optional fields:**
- `revenue` (number)
- `warehouse` (string)

**Example:**
```json
[
  {
    "sku": "PROD-001",
    "date": "2025-12-01",
    "quantity": 100,
    "revenue": 1050,
    "warehouse": "WH-001"
  },
  {
    "sku": "PROD-001",
    "date": "2025-11-01",
    "quantity": 105,
    "revenue": 1102.50,
    "warehouse": "WH-001"
  },
  {
    "sku": "PROD-002",
    "date": "2025-12-01",
    "quantity": 80,
    "revenue": 1260,
    "warehouse": "WH-002"
  }
]
```

### 3. suppliers.json

**Required fields:**
- `supplier_id` (string) - Supplier ID
- `name` (string) - Supplier name

**Optional fields:**
- `contact_email` (string)
- `contact_phone` (string)
- `unit_price` (number)
- `reliability_score` (number) - 0 to 1
- `lead_time_days` (number)
- `min_order_quantity` (number)
- `payment_terms` (string)
- `location` (string)
- `rating` (number)

**Example:**
```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Supplies Inc",
    "contact_email": "contact@globalsupplies.com",
    "unit_price": 10.50,
    "reliability_score": 0.95,
    "lead_time_days": 7,
    "min_order_quantity": 100,
    "payment_terms": "Net 30",
    "location": "USA",
    "rating": 4.8
  },
  {
    "supplier_id": "SUPP-002",
    "name": "Asia Trade Partners",
    "unit_price": 9.75,
    "reliability_score": 0.88,
    "lead_time_days": 14,
    "location": "China"
  }
]
```

---

## Step 1: Create Your Data Files

### Option A: From Existing Data

If you have data in Excel, CSV, or database:

1. Export to JSON format
2. Ensure required fields are present
3. Save as `inventory.json`, `sales_history.json`, `suppliers.json`

### Option B: Create Manually

Create JSON files with your data using the format above.

### Option C: Convert from CSV

Use Python to convert CSV to JSON:

```python
import csv
import json

# Convert CSV to JSON
def csv_to_json(csv_file, json_file):
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

# Usage
csv_to_json('inventory.csv', 'inventory.json')
csv_to_json('sales_history.csv', 'sales_history.json')
csv_to_json('suppliers.csv', 'suppliers.json')
```

---

## Step 2: Validate Your Data

### Check File Format

```bash
# Validate JSON syntax
python -m json.tool inventory.json > /dev/null && echo "✓ Valid JSON"
```

### Check Required Fields

```python
import json

# Check inventory
with open('inventory.json') as f:
    data = json.load(f)
    for item in data:
        assert 'sku' in item, "Missing sku"
        assert 'current_quantity' in item, "Missing current_quantity"
        assert 'reorder_point' in item, "Missing reorder_point"
    print("✓ Inventory data valid")

# Check sales history
with open('sales_history.json') as f:
    data = json.load(f)
    for item in data:
        assert 'sku' in item, "Missing sku"
        assert 'date' in item, "Missing date"
        assert 'quantity' in item, "Missing quantity"
    print("✓ Sales history valid")

# Check suppliers
with open('suppliers.json') as f:
    data = json.load(f)
    for item in data:
        assert 'supplier_id' in item, "Missing supplier_id"
        assert 'name' in item, "Missing name"
    print("✓ Supplier data valid")
```

---

## Step 3: Upload to Knowledge Base

### Using Upload Script

```bash
python upload_custom_kb_data.py
```

Then:
1. Enter S3 bucket name
2. Enter Knowledge Base ID
3. Enter directory containing your JSON files
4. Script will validate and upload

### Manual Upload

1. Go to AWS Console → Bedrock → Knowledge Bases
2. Select your Knowledge Base
3. Click "Upload documents"
4. Select your JSON files
5. Click "Upload"
6. Wait for processing

---

## Step 4: Configure Environment

Edit `.env` and add:

```bash
BEDROCK_KB_ID=your_knowledge_base_id
```

---

## Step 5: Test

```bash
python supply_chain_orchestrator.py
```

Ask:
```
"Sync data from knowledge base"
```

---

## Data Quality Tips

### 1. Consistency
- Use consistent SKU format across all files
- Use consistent date format (YYYY-MM-DD)
- Use consistent supplier IDs

### 2. Completeness
- Include at least 12 months of sales history
- Include all active products
- Include all active suppliers

### 3. Accuracy
- Verify quantities are correct
- Verify prices are current
- Verify supplier information is up-to-date

### 4. Validation
- Check for missing values
- Check for duplicate entries
- Check for data type consistency

---

## Example: Complete Data Set

### inventory.json
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
    "unit_price": 10.50
  },
  {
    "sku": "PROD-002",
    "product_name": "Widget B",
    "current_quantity": 800,
    "reorder_point": 150,
    "safety_stock": 250,
    "warehouse": "WH-002",
    "lead_time_days": 5,
    "ordering_cost": 40,
    "holding_cost_per_unit": 1.5,
    "unit_price": 15.75
  }
]
```

### sales_history.json
```json
[
  {
    "sku": "PROD-001",
    "date": "2025-12-01",
    "quantity": 100,
    "revenue": 1050
  },
  {
    "sku": "PROD-001",
    "date": "2025-11-01",
    "quantity": 105,
    "revenue": 1102.50
  },
  {
    "sku": "PROD-002",
    "date": "2025-12-01",
    "quantity": 80,
    "revenue": 1260
  }
]
```

### suppliers.json
```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Supplies Inc",
    "unit_price": 10.50,
    "reliability_score": 0.95,
    "lead_time_days": 7
  },
  {
    "supplier_id": "SUPP-002",
    "name": "Asia Trade Partners",
    "unit_price": 9.75,
    "reliability_score": 0.88,
    "lead_time_days": 14
  }
]
```

---

## Troubleshooting

### Issue: "Invalid JSON"
- Check JSON syntax using online validator
- Ensure all strings are quoted
- Ensure all commas are correct

### Issue: "Missing required field"
- Check all items have required fields
- Use the validation script above

### Issue: "Upload failed"
- Check S3 bucket exists
- Check AWS credentials
- Check file size (should be < 100MB)

### Issue: "Data not appearing in KB"
- Wait for KB to process (may take minutes)
- Check S3 bucket has files
- Try syncing KB manually

---

## Next Steps

1. ✅ Prepare your data files
2. ✅ Validate JSON format
3. ✅ Upload using script or console
4. ✅ Set BEDROCK_KB_ID
5. ✅ Run orchestrator
6. ✅ Sync data from KB

---

## Support

For help:
- Check data format guide above
- Run validation script
- Check AWS CloudWatch logs
- Review S3 bucket contents

---

## Summary

You now have:
✅ Data format specifications
✅ Upload script
✅ Validation tools
✅ Example data
✅ Troubleshooting guide

Ready to upload your real data! 🚀
