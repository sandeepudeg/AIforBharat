# Custom Data Upload Guide

## 🎯 Overview

You can now upload your own real supply chain data to the Bedrock Knowledge Base instead of using dummy data.

---

## 📋 What You Need

### 3 JSON Files with Your Data:

1. **inventory.json** - Your product inventory
2. **sales_history.json** - Your sales records
3. **suppliers.json** - Your supplier information

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Prepare Your Data

Create 3 JSON files with your supply chain data:

```bash
# Create your data files
# inventory.json
# sales_history.json
# suppliers.json
```

See `PREPARE_YOUR_DATA.md` for detailed format specifications.

### Step 2: Upload Using Script

```bash
python upload_custom_kb_data.py
```

Then:
1. Enter S3 bucket name
2. Enter Knowledge Base ID
3. Enter directory with your JSON files
4. Script validates and uploads

### Step 3: Configure

Edit `.env`:
```bash
BEDROCK_KB_ID=your_kb_id
```

### Step 4: Test

```bash
python supply_chain_orchestrator.py
# Ask: "Sync data from knowledge base"
```

---

## 📁 File Formats

### inventory.json

**Required:**
- `sku` - Product ID
- `current_quantity` - Stock level
- `reorder_point` - Reorder threshold

**Optional:**
- `product_name`, `warehouse`, `unit_price`, etc.

```json
[
  {
    "sku": "PROD-001",
    "product_name": "Widget A",
    "current_quantity": 1500,
    "reorder_point": 200,
    "unit_price": 10.50
  }
]
```

### sales_history.json

**Required:**
- `sku` - Product ID
- `date` - Date (YYYY-MM-DD)
- `quantity` - Quantity sold

**Optional:**
- `revenue`, `warehouse`, etc.

```json
[
  {
    "sku": "PROD-001",
    "date": "2025-12-01",
    "quantity": 100,
    "revenue": 1050
  }
]
```

### suppliers.json

**Required:**
- `supplier_id` - Supplier ID
- `name` - Supplier name

**Optional:**
- `unit_price`, `reliability_score`, `lead_time_days`, etc.

```json
[
  {
    "supplier_id": "SUPP-001",
    "name": "Global Supplies Inc",
    "unit_price": 10.50,
    "reliability_score": 0.95
  }
]
```

---

## 🔧 Upload Script Features

### Interactive Menu

```
1. Upload custom data files
2. View data format guide
3. Exit
```

### Automatic Validation

- ✅ Checks JSON syntax
- ✅ Validates required fields
- ✅ Verifies data structure
- ✅ Reports errors clearly

### Automatic Upload

- ✅ Creates S3 bucket if needed
- ✅ Uploads to correct location
- ✅ Syncs Knowledge Base
- ✅ Provides status updates

---

## 📊 Data Preparation

### From Excel/CSV

```python
import csv
import json

def csv_to_json(csv_file, json_file):
    data = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)

# Convert your files
csv_to_json('inventory.csv', 'inventory.json')
csv_to_json('sales_history.csv', 'sales_history.json')
csv_to_json('suppliers.csv', 'suppliers.json')
```

### From Database

```python
import json
import sqlite3

# Query database and export to JSON
conn = sqlite3.connect('supply_chain.db')
cursor = conn.cursor()

# Get inventory
cursor.execute('SELECT * FROM inventory')
inventory = [dict(zip([col[0] for col in cursor.description], row)) 
             for row in cursor.fetchall()]

with open('inventory.json', 'w') as f:
    json.dump(inventory, f, indent=2)
```

---

## ✅ Validation Checklist

Before uploading, verify:

- [ ] All JSON files are valid JSON
- [ ] All required fields are present
- [ ] Data types are correct (numbers, strings, dates)
- [ ] SKUs are consistent across files
- [ ] Dates are in YYYY-MM-DD format
- [ ] No duplicate entries
- [ ] At least 12 months of sales history
- [ ] All active products included
- [ ] All active suppliers included

---

## 🧪 Testing

### Test 1: Validate JSON

```bash
python -m json.tool inventory.json > /dev/null && echo "✓ Valid"
```

### Test 2: Check Required Fields

```python
import json

with open('inventory.json') as f:
    data = json.load(f)
    for item in data:
        assert 'sku' in item
        assert 'current_quantity' in item
        assert 'reorder_point' in item
print("✓ All required fields present")
```

### Test 3: Upload and Sync

```bash
python upload_custom_kb_data.py
# Follow prompts
```

### Test 4: Verify in Orchestrator

```bash
python supply_chain_orchestrator.py
# Ask: "Sync data from knowledge base"
# Should retrieve your data
```

---

## 🐛 Troubleshooting

### "Invalid JSON"
- Use online JSON validator
- Check quotes and commas
- Ensure proper formatting

### "Missing required field"
- Check all items have required fields
- Use validation script above
- See format guide in `PREPARE_YOUR_DATA.md`

### "Upload failed"
- Check S3 bucket exists
- Check AWS credentials
- Check file size < 100MB

### "Data not in KB"
- Wait for KB to process (may take minutes)
- Check S3 bucket has files
- Try syncing KB manually

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `PREPARE_YOUR_DATA.md` | Detailed data format guide |
| `upload_custom_kb_data.py` | Upload script |
| `CUSTOM_DATA_UPLOAD_GUIDE.md` | This file |

---

## 🎯 Workflow

```
Your Data (Excel, CSV, DB)
    ↓
Convert to JSON
    ↓
Validate Format
    ↓
Run Upload Script
    ↓
S3 Upload
    ↓
KB Sync
    ↓
Set BEDROCK_KB_ID
    ↓
Run Orchestrator
    ↓
Sync from KB
    ↓
DynamoDB Storage
    ↓
Use Agent Tools
```

---

## 💡 Tips

1. **Start Small** - Test with a few products first
2. **Validate Early** - Check data before uploading
3. **Use Consistent IDs** - Same SKU format everywhere
4. **Include History** - At least 12 months of sales
5. **Update Regularly** - Keep KB data current

---

## 🚀 Next Steps

1. ✅ Prepare your data files
2. ✅ Validate JSON format
3. ✅ Run upload script
4. ✅ Set BEDROCK_KB_ID
5. ✅ Test with orchestrator
6. ✅ Start optimizing!

---

## Summary

You now have:
✅ Custom data upload script
✅ Data format specifications
✅ Validation tools
✅ Conversion examples
✅ Troubleshooting guide

**Ready to upload your real data!** 🎉

```bash
python upload_custom_kb_data.py
```
