#!/usr/bin/env python3
"""
Upload Custom Data to Bedrock Knowledge Base

This script allows you to upload your own supply chain data files
to the Bedrock Knowledge Base instead of using dummy data.
"""

import json
import os
import boto3
from pathlib import Path
from src.config import logger, config


class CustomKBUploader:
    """Upload custom data to Bedrock Knowledge Base."""

    def __init__(self):
        """Initialize AWS clients."""
        self.s3_client = boto3.client(
            's3',
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key
        )
        self.bedrock_client = boto3.client(
            'bedrock',
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key
        )
        logger.info("Custom KB Uploader initialized")

    def validate_json_file(self, filepath):
        """Validate JSON file format."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"✓ Valid JSON: {filepath}")
            return True, data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {str(e)}")
            return False, None
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return False, None

    def validate_inventory_data(self, data):
        """Validate inventory data structure."""
        if not isinstance(data, list):
            logger.error("Inventory data must be a list of items")
            return False
        
        required_fields = ['sku', 'current_quantity', 'reorder_point']
        for item in data:
            for field in required_fields:
                if field not in item:
                    logger.error(f"Missing required field '{field}' in inventory item: {item}")
                    return False
        
        logger.info(f"✓ Valid inventory data: {len(data)} items")
        return True

    def validate_sales_history_data(self, data):
        """Validate sales history data structure."""
        if not isinstance(data, list):
            logger.error("Sales history data must be a list of records")
            return False
        
        required_fields = ['sku', 'date', 'quantity']
        for item in data:
            for field in required_fields:
                if field not in item:
                    logger.error(f"Missing required field '{field}' in sales record: {item}")
                    return False
        
        logger.info(f"✓ Valid sales history data: {len(data)} records")
        return True

    def validate_supplier_data(self, data):
        """Validate supplier data structure."""
        if not isinstance(data, list):
            logger.error("Supplier data must be a list of suppliers")
            return False
        
        required_fields = ['supplier_id', 'name']
        for item in data:
            for field in required_fields:
                if field not in item:
                    logger.error(f"Missing required field '{field}' in supplier: {item}")
                    return False
        
        logger.info(f"✓ Valid supplier data: {len(data)} suppliers")
        return True

    def create_s3_bucket(self, bucket_name):
        """Create S3 bucket with proper region configuration."""
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=bucket_name)
            print(f"   ✓ Bucket exists: {bucket_name}")
            return True
        except:
            pass
        
        try:
            print(f"   Creating bucket: {bucket_name}")
            
            # Create bucket with proper region configuration
            if config.aws.region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                # Other regions need LocationConstraint
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': config.aws.region}
                )
            
            print(f"   ✓ Bucket created: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create bucket: {str(e)}")
            print(f"   ✗ Error creating bucket: {str(e)}")
            return False

    def upload_file_to_s3(self, bucket_name, local_filepath, s3_key):
        """Upload file to S3."""
        try:
            with open(local_filepath, 'r') as f:
                content = f.read()
            
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=content,
                ContentType='application/json'
            )
            logger.info(f"✓ Uploaded to S3: s3://{bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return False

    def sync_knowledge_base(self, kb_id):
        """Sync knowledge base after uploading documents."""
        try:
            print(f"\n🔄 Syncing Knowledge Base: {kb_id}")
            
            response = self.bedrock_client.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId='default'
            )
            
            job_id = response.get('ingestionJobId')
            logger.info(f"✓ Sync started: Job ID {job_id}")
            print(f"   ✓ Sync job started: {job_id}")
            print(f"   ℹ️  This may take a few minutes...")
            
            return True
        except Exception as e:
            logger.warning(f"Could not sync KB (may not be required): {str(e)}")
            print(f"   ℹ️  Note: {str(e)}")
            return False

    def upload_custom_data(self):
        """Upload custom data files."""
        print("\n" + "="*70)
        print("  UPLOAD CUSTOM DATA TO BEDROCK KNOWLEDGE BASE")
        print("="*70)
        
        # Get S3 bucket name
        bucket_name = input("\nEnter S3 bucket name: ").strip()
        if not bucket_name:
            print("✗ Bucket name required")
            return False
        
        # Get KB ID
        kb_id = input("Enter Knowledge Base ID: ").strip()
        if not kb_id:
            print("✗ Knowledge Base ID required")
            return False
        
        # Get data directory
        data_dir = input("Enter directory containing your data files (or press Enter for current dir): ").strip()
        if not data_dir:
            data_dir = "."
        
        if not os.path.isdir(data_dir):
            print(f"✗ Directory not found: {data_dir}")
            return False
        
        print(f"\n📁 Looking for data files in: {data_dir}")
        
        # Create bucket
        print(f"\n🪣 Setting up S3 bucket")
        if not self.create_s3_bucket(bucket_name):
            print("✗ Failed to create/access bucket")
            return False
        
        # Find and upload files
        files_uploaded = 0
        
        # Look for inventory file
        inventory_files = list(Path(data_dir).glob("*inventory*.json"))
        if inventory_files:
            inventory_file = str(inventory_files[0])
            print(f"\n📦 Found inventory file: {inventory_file}")
            
            valid, data = self.validate_json_file(inventory_file)
            if valid and self.validate_inventory_data(data):
                s3_key = f"supply-chain-data/inventory.json"
                if self.upload_file_to_s3(bucket_name, inventory_file, s3_key):
                    files_uploaded += 1
            else:
                print("   ✗ Validation failed")
        else:
            print("\n⚠️  No inventory file found (looking for *inventory*.json)")
        
        # Look for sales history file
        sales_files = list(Path(data_dir).glob("*sales*.json"))
        if sales_files:
            sales_file = str(sales_files[0])
            print(f"\n📊 Found sales history file: {sales_file}")
            
            valid, data = self.validate_json_file(sales_file)
            if valid and self.validate_sales_history_data(data):
                s3_key = f"supply-chain-data/sales_history.json"
                if self.upload_file_to_s3(bucket_name, sales_file, s3_key):
                    files_uploaded += 1
            else:
                print("   ✗ Validation failed")
        else:
            print("\n⚠️  No sales history file found (looking for *sales*.json)")
        
        # Look for supplier file
        supplier_files = list(Path(data_dir).glob("*supplier*.json"))
        if supplier_files:
            supplier_file = str(supplier_files[0])
            print(f"\n🏭 Found supplier file: {supplier_file}")
            
            valid, data = self.validate_json_file(supplier_file)
            if valid and self.validate_supplier_data(data):
                s3_key = f"supply-chain-data/suppliers.json"
                if self.upload_file_to_s3(bucket_name, supplier_file, s3_key):
                    files_uploaded += 1
            else:
                print("   ✗ Validation failed")
        else:
            print("\n⚠️  No supplier file found (looking for *supplier*.json)")
        
        # Summary
        print("\n" + "="*70)
        print(f"✓ Uploaded {files_uploaded} file(s)")
        print("="*70)
        
        if files_uploaded > 0:
            # Sync KB
            sync = input("\nSync Knowledge Base now? (y/n): ").strip().lower()
            if sync == 'y':
                self.sync_knowledge_base(kb_id)
            
            print("\n✅ Upload complete!")
            print("\nNext steps:")
            print("  1. Wait for KB to process documents (may take a few minutes)")
            print("  2. Set BEDROCK_KB_ID in .env")
            print("  3. Run: python supply_chain_orchestrator.py")
            print("  4. Ask: 'Sync data from knowledge base'")
            
            return True
        else:
            print("\n✗ No files uploaded")
            return False

    def print_data_format_guide(self):
        """Print data format guide."""
        print("\n" + "="*70)
        print("  DATA FORMAT GUIDE")
        print("="*70)
        
        print("\n📦 INVENTORY DATA (inventory.json)")
        print("Required fields:")
        print("  - sku (string): Product SKU")
        print("  - current_quantity (number): Current stock")
        print("  - reorder_point (number): Reorder threshold")
        print("\nOptional fields:")
        print("  - product_name, warehouse, lead_time_days, etc.")
        
        print("\n📊 SALES HISTORY (sales_history.json)")
        print("Required fields:")
        print("  - sku (string): Product SKU")
        print("  - date (string): Date in YYYY-MM-DD format")
        print("  - quantity (number): Quantity sold")
        print("\nOptional fields:")
        print("  - revenue, warehouse, etc.")
        
        print("\n🏭 SUPPLIERS (suppliers.json)")
        print("Required fields:")
        print("  - supplier_id (string): Supplier ID")
        print("  - name (string): Supplier name")
        print("\nOptional fields:")
        print("  - unit_price, reliability_score, lead_time_days, etc.")
        
        print("\n" + "="*70)

    def run_wizard(self):
        """Run interactive wizard."""
        print("\n" + "="*70)
        print("  CUSTOM DATA UPLOAD WIZARD")
        print("="*70)
        
        while True:
            print("\n📋 What would you like to do?")
            print("   1. Upload custom data files")
            print("   2. View data format guide")
            print("   3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                self.upload_custom_data()
            elif choice == '2':
                self.print_data_format_guide()
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("   ✗ Invalid choice")


def main():
    """Main entry point."""
    uploader = CustomKBUploader()
    uploader.run_wizard()


if __name__ == "__main__":
    main()
