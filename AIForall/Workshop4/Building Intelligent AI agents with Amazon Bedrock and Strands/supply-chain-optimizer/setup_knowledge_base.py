#!/usr/bin/env python3
"""
Setup Bedrock Knowledge Base for Supply Chain Optimizer

This script helps you create and configure a Bedrock Knowledge Base
with sample supply chain data.
"""

import json
import boto3
import os
from datetime import datetime
from src.config import logger, config


class KnowledgeBaseSetup:
    """Setup Bedrock Knowledge Base."""

    def __init__(self):
        """Initialize AWS clients."""
        self.bedrock_client = boto3.client(
            'bedrock',
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key
        )
        self.s3_client = boto3.client(
            's3',
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key
        )
        logger.info("Knowledge Base Setup initialized")

    def create_sample_documents(self):
        """Create sample supply chain documents."""
        documents = {
            'inventory.json': [
                {
                    'sku': 'PROD-001',
                    'product_name': 'Widget A',
                    'current_quantity': 1500,
                    'reorder_point': 200,
                    'safety_stock': 300,
                    'warehouse': 'WH-001',
                    'lead_time_days': 7,
                    'ordering_cost': 50,
                    'holding_cost_per_unit': 2,
                    'unit_price': 10.50,
                    'category': 'Electronics',
                    'last_updated': datetime.now().isoformat(),
                },
                {
                    'sku': 'PROD-002',
                    'product_name': 'Widget B',
                    'current_quantity': 800,
                    'reorder_point': 150,
                    'safety_stock': 250,
                    'warehouse': 'WH-002',
                    'lead_time_days': 5,
                    'ordering_cost': 40,
                    'holding_cost_per_unit': 1.5,
                    'unit_price': 15.75,
                    'category': 'Electronics',
                    'last_updated': datetime.now().isoformat(),
                },
                {
                    'sku': 'PROD-003',
                    'product_name': 'Gadget X',
                    'current_quantity': 2000,
                    'reorder_point': 300,
                    'safety_stock': 400,
                    'warehouse': 'WH-001',
                    'lead_time_days': 10,
                    'ordering_cost': 60,
                    'holding_cost_per_unit': 3,
                    'unit_price': 25.00,
                    'category': 'Hardware',
                    'last_updated': datetime.now().isoformat(),
                },
            ],
            'sales_history.json': [
                {
                    'sku': 'PROD-001',
                    'date': '2025-12-01',
                    'quantity': 100,
                    'revenue': 1050,
                    'warehouse': 'WH-001',
                },
                {
                    'sku': 'PROD-001',
                    'date': '2025-11-01',
                    'quantity': 105,
                    'revenue': 1102.50,
                    'warehouse': 'WH-001',
                },
                {
                    'sku': 'PROD-001',
                    'date': '2025-10-01',
                    'quantity': 110,
                    'revenue': 1155,
                    'warehouse': 'WH-001',
                },
                {
                    'sku': 'PROD-002',
                    'date': '2025-12-01',
                    'quantity': 80,
                    'revenue': 1260,
                    'warehouse': 'WH-002',
                },
                {
                    'sku': 'PROD-002',
                    'date': '2025-11-01',
                    'quantity': 85,
                    'revenue': 1338.75,
                    'warehouse': 'WH-002',
                },
                {
                    'sku': 'PROD-003',
                    'date': '2025-12-01',
                    'quantity': 50,
                    'revenue': 1250,
                    'warehouse': 'WH-001',
                },
            ],
            'suppliers.json': [
                {
                    'supplier_id': 'SUPP-001',
                    'name': 'Global Supplies Inc',
                    'contact_email': 'contact@globalsupplies.com',
                    'contact_phone': '+1-555-0101',
                    'unit_price': 10.50,
                    'reliability_score': 0.95,
                    'lead_time_days': 7,
                    'min_order_quantity': 100,
                    'payment_terms': 'Net 30',
                    'location': 'USA',
                    'rating': 4.8,
                },
                {
                    'supplier_id': 'SUPP-002',
                    'name': 'Asia Trade Partners',
                    'contact_email': 'sales@asiatrade.com',
                    'contact_phone': '+86-10-1234-5678',
                    'unit_price': 9.75,
                    'reliability_score': 0.88,
                    'lead_time_days': 14,
                    'min_order_quantity': 500,
                    'payment_terms': 'Net 45',
                    'location': 'China',
                    'rating': 4.5,
                },
                {
                    'supplier_id': 'SUPP-003',
                    'name': 'European Distributors',
                    'contact_email': 'info@eudist.eu',
                    'contact_phone': '+49-30-1234-5678',
                    'unit_price': 11.25,
                    'reliability_score': 0.92,
                    'lead_time_days': 5,
                    'min_order_quantity': 200,
                    'payment_terms': 'Net 30',
                    'location': 'Germany',
                    'rating': 4.7,
                },
            ],
        }
        return documents

    def upload_documents_to_s3(self, bucket_name, documents):
        """Upload documents to S3 for Knowledge Base."""
        try:
            print(f"\n📤 Uploading documents to S3 bucket: {bucket_name}")
            
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                print(f"   ✓ Bucket exists: {bucket_name}")
            except:
                print(f"   Creating bucket: {bucket_name}")
                self.s3_client.create_bucket(Bucket=bucket_name)
                print(f"   ✓ Bucket created: {bucket_name}")
            
            # Upload documents
            for filename, content in documents.items():
                key = f"supply-chain-data/{filename}"
                body = json.dumps(content, indent=2, default=str)
                
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=body,
                    ContentType='application/json'
                )
                print(f"   ✓ Uploaded: {key}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to upload documents to S3: {str(e)}")
            print(f"   ✗ Error: {str(e)}")
            return False

    def list_knowledge_bases(self):
        """List existing knowledge bases."""
        try:
            print("\n📚 Existing Knowledge Bases:")
            
            response = self.bedrock_client.list_knowledge_bases()
            
            if not response.get('knowledgeBaseSummaries'):
                print("   No knowledge bases found")
                return []
            
            kbs = []
            for kb in response['knowledgeBaseSummaries']:
                kb_id = kb['knowledgeBaseId']
                kb_name = kb['name']
                kb_status = kb['status']
                kbs.append({
                    'id': kb_id,
                    'name': kb_name,
                    'status': kb_status
                })
                print(f"   • {kb_name} (ID: {kb_id}, Status: {kb_status})")
            
            return kbs
        except Exception as e:
            logger.error(f"Failed to list knowledge bases: {str(e)}")
            print(f"   ✗ Error: {str(e)}")
            return []

    def print_setup_instructions(self):
        """Print setup instructions."""
        print("\n" + "="*70)
        print("  BEDROCK KNOWLEDGE BASE SETUP INSTRUCTIONS")
        print("="*70)
        
        print("\n📋 STEP 1: Create Knowledge Base in AWS Console")
        print("   1. Go to AWS Console → Bedrock → Knowledge Bases")
        print("   2. Click 'Create Knowledge Base'")
        print("   3. Configure:")
        print("      - Name: supply-chain-optimizer-kb")
        print("      - Model: Claude 3 Sonnet")
        print("      - Storage: S3 bucket")
        print("   4. Note the Knowledge Base ID")
        
        print("\n📤 STEP 2: Upload Documents")
        print("   Option A: Use this script")
        print("      - Run: python setup_knowledge_base.py")
        print("      - Choose option to upload documents")
        print("")
        print("   Option B: Manual upload")
        print("      - Go to Knowledge Base in AWS Console")
        print("      - Upload the JSON files:")
        print("         • inventory.json")
        print("         • sales_history.json")
        print("         • suppliers.json")
        
        print("\n🔧 STEP 3: Configure Environment")
        print("   Add to .env file:")
        print("      BEDROCK_KB_ID=your_knowledge_base_id")
        
        print("\n✅ STEP 4: Verify Setup")
        print("   Run: python supply_chain_orchestrator.py")
        print("   Ask: 'Sync data from knowledge base'")
        
        print("\n" + "="*70)

    def run_setup_wizard(self):
        """Run interactive setup wizard."""
        print("\n" + "="*70)
        print("  BEDROCK KNOWLEDGE BASE SETUP WIZARD")
        print("="*70)
        
        while True:
            print("\n📋 What would you like to do?")
            print("   1. List existing knowledge bases")
            print("   2. Create sample documents")
            print("   3. Upload documents to S3")
            print("   4. View setup instructions")
            print("   5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self.list_knowledge_bases()
            
            elif choice == '2':
                print("\n📄 Creating sample documents...")
                documents = self.create_sample_documents()
                print(f"   ✓ Created {len(documents)} document types:")
                for filename in documents.keys():
                    print(f"      • {filename}")
                
                # Save to local files
                for filename, content in documents.items():
                    filepath = f"sample_kb_documents/{filename}"
                    os.makedirs("sample_kb_documents", exist_ok=True)
                    with open(filepath, 'w') as f:
                        json.dump(content, f, indent=2, default=str)
                    print(f"   ✓ Saved: {filepath}")
            
            elif choice == '3':
                bucket_name = input("\nEnter S3 bucket name: ").strip()
                if bucket_name:
                    documents = self.create_sample_documents()
                    self.upload_documents_to_s3(bucket_name, documents)
            
            elif choice == '4':
                self.print_setup_instructions()
            
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("   ✗ Invalid choice. Please try again.")


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("  SUPPLY CHAIN OPTIMIZER - KNOWLEDGE BASE SETUP")
    print("="*70)
    
    setup = KnowledgeBaseSetup()
    setup.run_setup_wizard()


if __name__ == "__main__":
    main()
