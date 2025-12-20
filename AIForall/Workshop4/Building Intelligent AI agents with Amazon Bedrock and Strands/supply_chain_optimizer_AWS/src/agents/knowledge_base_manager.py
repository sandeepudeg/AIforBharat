"""
Knowledge Base Manager for Supply Chain Optimizer

Manages interaction with Bedrock Knowledge Base for data ingestion and retrieval.
Stores retrieved data in DynamoDB for persistence.
"""

import json
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.config import logger, config
from src.aws.clients import get_dynamodb_resource


class KnowledgeBaseManager:
    """Manages Bedrock Knowledge Base operations and DynamoDB storage."""

    def __init__(self, knowledge_base_id: str):
        """
        Initialize Knowledge Base Manager.
        
        Args:
            knowledge_base_id: Bedrock Knowledge Base ID
        """
        self.knowledge_base_id = knowledge_base_id
        self.bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key
        )
        self.dynamodb = get_dynamodb_resource()
        logger.info(f"Knowledge Base Manager initialized with KB ID: {knowledge_base_id}")

    def retrieve_from_knowledge_base(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve information from Bedrock Knowledge Base.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of retrieved documents
        """
        try:
            logger.info(f"Retrieving from knowledge base: {query}")
            
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                },
                text=query
            )
            
            results = response.get('retrievalResults', [])
            logger.info(f"Retrieved {len(results)} results from knowledge base")
            
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve from knowledge base: {str(e)}")
            return []

    def ingest_inventory_data(self, inventory_data: List[Dict[str, Any]]) -> bool:
        """
        Ingest inventory data into DynamoDB from knowledge base.
        
        Args:
            inventory_data: List of inventory items
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Ingesting {len(inventory_data)} inventory items")
            
            table = self.dynamodb.Table('inventory')
            
            for item in inventory_data:
                # Ensure required fields
                if 'sku' not in item:
                    logger.warning(f"Skipping item without SKU: {item}")
                    continue
                
                # Add metadata
                item['ingested_date'] = datetime.now().isoformat()
                item['source'] = 'knowledge_base'
                
                # Save to DynamoDB
                table.put_item(Item=item)
                logger.info(f"Ingested inventory item: {item.get('sku')}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to ingest inventory data: {str(e)}")
            return False

    def ingest_sales_history(self, sales_data: List[Dict[str, Any]]) -> bool:
        """
        Ingest sales history data into DynamoDB.
        
        Args:
            sales_data: List of sales records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Ingesting {len(sales_data)} sales records")
            
            table = self.dynamodb.Table('sales_history')
            
            for item in sales_data:
                # Ensure required fields
                if 'sku' not in item or 'date' not in item:
                    logger.warning(f"Skipping sales record without SKU or date: {item}")
                    continue
                
                # Add metadata
                item['ingested_date'] = datetime.now().isoformat()
                item['source'] = 'knowledge_base'
                
                # Save to DynamoDB
                table.put_item(Item=item)
                logger.info(f"Ingested sales record: {item.get('sku')} on {item.get('date')}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to ingest sales history: {str(e)}")
            return False

    def ingest_supplier_data(self, supplier_data: List[Dict[str, Any]]) -> bool:
        """
        Ingest supplier data into DynamoDB.
        
        Args:
            supplier_data: List of supplier records
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Ingesting {len(supplier_data)} supplier records")
            
            table = self.dynamodb.Table('suppliers')
            
            for item in supplier_data:
                # Ensure required fields
                if 'supplier_id' not in item:
                    logger.warning(f"Skipping supplier without ID: {item}")
                    continue
                
                # Add metadata
                item['ingested_date'] = datetime.now().isoformat()
                item['source'] = 'knowledge_base'
                
                # Save to DynamoDB
                table.put_item(Item=item)
                logger.info(f"Ingested supplier: {item.get('supplier_id')}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to ingest supplier data: {str(e)}")
            return False

    def retrieve_and_store_inventory(self, query: str = "inventory") -> bool:
        """
        Retrieve inventory data from knowledge base and store in DynamoDB.
        
        Args:
            query: Search query for inventory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Retrieving and storing inventory data")
            
            # Retrieve from knowledge base
            results = self.retrieve_from_knowledge_base(query)
            
            if not results:
                logger.warning("No inventory data found in knowledge base")
                return False
            
            # Parse results
            inventory_items = []
            for result in results:
                content = result.get('content', '')
                try:
                    # Try to parse as JSON
                    item = json.loads(content)
                    inventory_items.append(item)
                except json.JSONDecodeError:
                    # If not JSON, create item from content
                    logger.warning(f"Could not parse JSON from knowledge base result: {content}")
            
            # Ingest into DynamoDB
            if inventory_items:
                return self.ingest_inventory_data(inventory_items)
            
            return False
        except Exception as e:
            logger.error(f"Failed to retrieve and store inventory: {str(e)}")
            return False

    def retrieve_and_store_sales_history(self, query: str = "sales history") -> bool:
        """
        Retrieve sales history from knowledge base and store in DynamoDB.
        
        Args:
            query: Search query for sales history
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Retrieving and storing sales history")
            
            # Retrieve from knowledge base
            results = self.retrieve_from_knowledge_base(query)
            
            if not results:
                logger.warning("No sales history found in knowledge base")
                return False
            
            # Parse results
            sales_items = []
            for result in results:
                content = result.get('content', '')
                try:
                    # Try to parse as JSON
                    item = json.loads(content)
                    sales_items.append(item)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON from knowledge base result: {content}")
            
            # Ingest into DynamoDB
            if sales_items:
                return self.ingest_sales_history(sales_items)
            
            return False
        except Exception as e:
            logger.error(f"Failed to retrieve and store sales history: {str(e)}")
            return False

    def retrieve_and_store_suppliers(self, query: str = "suppliers") -> bool:
        """
        Retrieve supplier data from knowledge base and store in DynamoDB.
        
        Args:
            query: Search query for suppliers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Retrieving and storing supplier data")
            
            # Retrieve from knowledge base
            results = self.retrieve_from_knowledge_base(query)
            
            if not results:
                logger.warning("No supplier data found in knowledge base")
                return False
            
            # Parse results
            supplier_items = []
            for result in results:
                content = result.get('content', '')
                try:
                    # Try to parse as JSON
                    item = json.loads(content)
                    supplier_items.append(item)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON from knowledge base result: {content}")
            
            # Ingest into DynamoDB
            if supplier_items:
                return self.ingest_supplier_data(supplier_items)
            
            return False
        except Exception as e:
            logger.error(f"Failed to retrieve and store suppliers: {str(e)}")
            return False

    def sync_all_data(self) -> Dict[str, bool]:
        """
        Sync all data from knowledge base to DynamoDB.
        
        Returns:
            Dictionary with sync status for each data type
        """
        logger.info("Starting full data sync from knowledge base to DynamoDB")
        
        results = {
            'inventory': self.retrieve_and_store_inventory(),
            'sales_history': self.retrieve_and_store_sales_history(),
            'suppliers': self.retrieve_and_store_suppliers(),
        }
        
        logger.info(f"Data sync complete: {results}")
        return results

    def get_inventory_from_kb(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Get inventory data from knowledge base for a specific SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Inventory data or None
        """
        try:
            query = f"inventory for SKU {sku}"
            results = self.retrieve_from_knowledge_base(query, max_results=1)
            
            if results:
                content = results[0].get('content', '')
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse inventory data for {sku}")
            
            return None
        except Exception as e:
            logger.error(f"Failed to get inventory from KB: {str(e)}")
            return None

    def get_sales_history_from_kb(self, sku: str) -> List[Dict[str, Any]]:
        """
        Get sales history from knowledge base for a specific SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            List of sales records
        """
        try:
            query = f"sales history for SKU {sku}"
            results = self.retrieve_from_knowledge_base(query, max_results=12)
            
            sales_items = []
            for result in results:
                content = result.get('content', '')
                try:
                    item = json.loads(content)
                    sales_items.append(item)
                except json.JSONDecodeError:
                    pass
            
            return sales_items
        except Exception as e:
            logger.error(f"Failed to get sales history from KB: {str(e)}")
            return []

    def get_supplier_from_kb(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """
        Get supplier data from knowledge base.
        
        Args:
            supplier_id: Supplier ID
            
        Returns:
            Supplier data or None
        """
        try:
            query = f"supplier {supplier_id}"
            results = self.retrieve_from_knowledge_base(query, max_results=1)
            
            if results:
                content = results[0].get('content', '')
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse supplier data for {supplier_id}")
            
            return None
        except Exception as e:
            logger.error(f"Failed to get supplier from KB: {str(e)}")
            return None
