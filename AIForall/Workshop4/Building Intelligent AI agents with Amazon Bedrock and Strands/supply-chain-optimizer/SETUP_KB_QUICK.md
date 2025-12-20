# Quick Bedrock Knowledge Base Setup (5 Minutes)

## 🚀 Fastest Way to Get Started

### Step 1: Create Knowledge Base (AWS Console)

1. Go to: https://console.aws.amazon.com/bedrock
2. Click "Knowledge Bases" → "Create Knowledge Base"
3. Fill in:
   - **Name**: `supply-chain-optimizer-kb`
   - **Model**: Claude 3 Sonnet
   - **Storage**: Create new S3 bucket
4. Click "Create"
5. **Copy the Knowledge Base ID** (you'll need this)

### Step 2: Generate Sample Documents

```bash
python setup_knowledge_base.py
```

Choose option 2: "Create sample documents"

This creates:
- `sample_kb_documents/inventory.json`
- `sample_kb_documents/sales_history.json`
- `sample_kb_documents/suppliers.json`

### Step 3: Upload Documents

```bash
python setup_knowledge_base.py
```

Choose option 3: "Upload documents to S3"

Enter your S3 bucket name when prompted.

### Step 4: Configure Environment

Edit `.env` file and add:

```bash
BEDROCK_KB_ID=your_knowledge_base_id
```

Replace `your_knowledge_base_id` with the ID from Step 1.

### Step 5: Test It!

```bash
python supply_chain_orchestrator.py
```

Then ask:
```
"Sync data from knowledge base"
```

---

## ✅ Done!

Your Knowledge Base is now configured and ready to use.

---

## 🆘 Troubleshooting

### Can't find Knowledge Base ID?

```bash
aws bedrock list-knowledge-bases --region us-east-1
```

Look for your KB in the output.

### Documents not uploading?

1. Check S3 bucket exists
2. Check AWS credentials in .env
3. Try uploading manually in AWS Console

### Still not working?

See `BEDROCK_KB_SETUP_GUIDE.md` for detailed troubleshooting.

---

## 📚 Full Documentation

For complete setup guide: `BEDROCK_KB_SETUP_GUIDE.md`

---

## 🎉 You're Ready!

```bash
python supply_chain_orchestrator.py
```

Enjoy optimizing your supply chain! 🚀
