"""Property-based tests for data persistence round trip.

Feature: supply-chain-optimizer, Property 32: Data Persistence Round Trip
Validates: Requirements 8.1, 8.2
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict
import json
import random
import string

from src.models.product import Product
from src.models.inventory import Inventory
from src.models.forecast import Forecast
from src.models.purchase_order import PurchaseOrder, POStatus


def generate_random_string(min_size: int = 1, max_size: int = 50) -> str:
    """Generate a random string."""
    size = random.randint(min_size, max_size)
    return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=size))


def generate_random_float(min_value: float = 0.01, max_value: float = 10000.0) -> float:
    """Generate a random float."""
    return random.uniform(min_value, max_value)


def generate_random_int(min_value: int = 0, max_value: int = 10000) -> int:
    """Generate a random integer."""
    return random.randint(min_value, max_value)


def generate_random_date(min_days: int = 0, max_days: int = 365) -> date:
    """Generate a random date."""
    days_offset = random.randint(min_days, max_days)
    return date.today() + timedelta(days=days_offset)


def product_data_generator() -> Dict[str, Any]:
    """Generate valid Product data."""
    return {
        "sku": generate_random_string(1, 50),
        "name": generate_random_string(1, 255),
        "category": generate_random_string(1, 100),
        "unit_cost": generate_random_float(0.01, 10000.0),
        "holding_cost_per_unit": generate_random_float(0.0, 1000.0),
        "ordering_cost": generate_random_float(0.0, 1000.0),
        "lead_time_days": generate_random_int(0, 365),
        "supplier_id": generate_random_string(1, 50),
        "reorder_point": generate_random_int(0, 10000),
        "safety_stock": generate_random_int(0, 10000),
        "economic_order_quantity": generate_random_int(0, 10000),
    }


def inventory_data_generator() -> Dict[str, Any]:
    """Generate valid Inventory data."""
    quantity_on_hand = generate_random_int(0, 10000)
    quantity_reserved = generate_random_int(0, quantity_on_hand)
    return {
        "inventory_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "warehouse_id": generate_random_string(1, 50),
        "quantity_on_hand": quantity_on_hand,
        "quantity_reserved": quantity_reserved,
        "reorder_point": generate_random_int(0, 10000),
    }


def forecast_data_generator() -> Dict[str, Any]:
    """Generate valid Forecast data."""
    confidence_80 = generate_random_int(0, 10000)
    confidence_95 = generate_random_int(0, confidence_80)
    return {
        "forecast_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "forecast_date": generate_random_date(),
        "forecast_period": generate_random_string(1, 100),
        "forecasted_demand": generate_random_int(0, 10000),
        "confidence_80": float(confidence_80),
        "confidence_95": float(confidence_95),
    }


def purchase_order_data_generator() -> Dict[str, Any]:
    """Generate valid PurchaseOrder data."""
    return {
        "po_id": generate_random_string(1, 50),
        "sku": generate_random_string(1, 50),
        "supplier_id": generate_random_string(1, 50),
        "quantity": generate_random_int(1, 10000),
        "unit_price": generate_random_float(0.01, 10000.0),
        "expected_delivery_date": generate_random_date(0, 365),
        "status": random.choice([status.value for status in POStatus]),
    }


class TestDataPersistenceRoundTrip:
    """Test data persistence round trip for all data models.
    
    Feature: supply-chain-optimizer, Property 32: Data Persistence Round Trip
    Validates: Requirements 8.1, 8.2
    """

    def test_product_persistence_round_trip_multiple_iterations(self):
        """For any valid Product data, storing and retrieving should return identical data.
        
        Property: *For any* supply chain data (inventory, forecast, order, anomaly), 
        storing and retrieving the data should return the exact same values with all fields intact.
        """
        # Run 100 iterations with random data
        for _ in range(100):
            product_data = product_data_generator()
            
            # Create Product instance
            product = Product(**product_data)
            
            # Simulate persistence: convert to dict (as would be stored)
            stored_data = product.model_dump()
            
            # Simulate retrieval: recreate from stored data
            retrieved_product = Product(**stored_data)
            
            # Verify round trip: all fields should match
            assert retrieved_product.sku == product.sku
            assert retrieved_product.name == product.name
            assert retrieved_product.category == product.category
            assert retrieved_product.unit_cost == product.unit_cost
            assert retrieved_product.holding_cost_per_unit == product.holding_cost_per_unit
            assert retrieved_product.ordering_cost == product.ordering_cost
            assert retrieved_product.lead_time_days == product.lead_time_days
            assert retrieved_product.supplier_id == product.supplier_id
            assert retrieved_product.reorder_point == product.reorder_point
            assert retrieved_product.safety_stock == product.safety_stock
            assert retrieved_product.economic_order_quantity == product.economic_order_quantity

    def test_inventory_persistence_round_trip_multiple_iterations(self):
        """For any valid Inventory data, storing and retrieving should return identical data.
        
        Property: *For any* supply chain data (inventory, forecast, order, anomaly), 
        storing and retrieving the data should return the exact same values with all fields intact.
        """
        # Run 100 iterations with random data
        for _ in range(100):
            inventory_data = inventory_data_generator()
            
            # Create Inventory instance
            inventory = Inventory(**inventory_data)
            
            # Simulate persistence: convert to dict
            stored_data = inventory.model_dump()
            
            # Simulate retrieval: recreate from stored data
            retrieved_inventory = Inventory(**stored_data)
            
            # Verify round trip: all fields should match
            assert retrieved_inventory.inventory_id == inventory.inventory_id
            assert retrieved_inventory.sku == inventory.sku
            assert retrieved_inventory.warehouse_id == inventory.warehouse_id
            assert retrieved_inventory.quantity_on_hand == inventory.quantity_on_hand
            assert retrieved_inventory.quantity_reserved == inventory.quantity_reserved
            assert retrieved_inventory.quantity_available == inventory.quantity_available
            assert retrieved_inventory.reorder_point == inventory.reorder_point

    def test_forecast_persistence_round_trip_multiple_iterations(self):
        """For any valid Forecast data, storing and retrieving should return identical data.
        
        Property: *For any* supply chain data (inventory, forecast, order, anomaly), 
        storing and retrieving the data should return the exact same values with all fields intact.
        """
        # Run 100 iterations with random data
        for _ in range(100):
            forecast_data = forecast_data_generator()
            
            # Create Forecast instance
            forecast = Forecast(**forecast_data)
            
            # Simulate persistence: convert to dict
            stored_data = forecast.model_dump()
            
            # Simulate retrieval: recreate from stored data
            retrieved_forecast = Forecast(**stored_data)
            
            # Verify round trip: all fields should match
            assert retrieved_forecast.forecast_id == forecast.forecast_id
            assert retrieved_forecast.sku == forecast.sku
            assert retrieved_forecast.forecast_date == forecast.forecast_date
            assert retrieved_forecast.forecast_period == forecast.forecast_period
            assert retrieved_forecast.forecasted_demand == forecast.forecasted_demand
            assert retrieved_forecast.confidence_80 == forecast.confidence_80
            assert retrieved_forecast.confidence_95 == forecast.confidence_95

    def test_purchase_order_persistence_round_trip_multiple_iterations(self):
        """For any valid PurchaseOrder data, storing and retrieving should return identical data.
        
        Property: *For any* supply chain data (inventory, forecast, order, anomaly), 
        storing and retrieving the data should return the exact same values with all fields intact.
        """
        # Run 100 iterations with random data
        for _ in range(100):
            po_data = purchase_order_data_generator()
            
            # Create PurchaseOrder instance
            purchase_order = PurchaseOrder(**po_data)
            
            # Simulate persistence: convert to dict
            stored_data = purchase_order.model_dump()
            
            # Simulate retrieval: recreate from stored data
            retrieved_po = PurchaseOrder(**stored_data)
            
            # Verify round trip: all fields should match
            assert retrieved_po.po_id == purchase_order.po_id
            assert retrieved_po.sku == purchase_order.sku
            assert retrieved_po.supplier_id == purchase_order.supplier_id
            assert retrieved_po.quantity == purchase_order.quantity
            assert retrieved_po.unit_price == purchase_order.unit_price
            assert retrieved_po.total_cost == purchase_order.total_cost
            assert retrieved_po.expected_delivery_date == purchase_order.expected_delivery_date
            assert retrieved_po.status == purchase_order.status

    def test_product_json_serialization_round_trip(self):
        """Test that Product can be serialized to JSON and deserialized back.
        
        Property: *For any* supply chain data, storing and retrieving the data 
        should return the exact same values with all fields intact.
        """
        product_data = {
            "sku": "TEST-001",
            "name": "Test Product",
            "category": "Test Category",
            "unit_cost": 100.0,
            "holding_cost_per_unit": 10.0,
            "ordering_cost": 50.0,
            "lead_time_days": 7,
            "supplier_id": "SUP-001",
            "reorder_point": 100,
            "safety_stock": 50,
            "economic_order_quantity": 200,
        }
        
        product = Product(**product_data)
        
        # Serialize to JSON string
        json_str = product.model_dump_json()
        
        # Deserialize from JSON string
        retrieved_product = Product.model_validate_json(json_str)
        
        # Verify all fields match
        assert retrieved_product.sku == product.sku
        assert retrieved_product.name == product.name
        assert retrieved_product.category == product.category
        assert retrieved_product.unit_cost == product.unit_cost
        assert retrieved_product.holding_cost_per_unit == product.holding_cost_per_unit
        assert retrieved_product.ordering_cost == product.ordering_cost
        assert retrieved_product.lead_time_days == product.lead_time_days
        assert retrieved_product.supplier_id == product.supplier_id

    def test_inventory_json_serialization_round_trip(self):
        """Test that Inventory can be serialized to JSON and deserialized back.
        
        Property: *For any* supply chain data, storing and retrieving the data 
        should return the exact same values with all fields intact.
        """
        inventory_data = {
            "inventory_id": "INV-001",
            "sku": "PROD-001",
            "warehouse_id": "WH-001",
            "quantity_on_hand": 500,
            "quantity_reserved": 100,
            "reorder_point": 100,
        }
        
        inventory = Inventory(**inventory_data)
        
        # Serialize to JSON string
        json_str = inventory.model_dump_json()
        
        # Deserialize from JSON string
        retrieved_inventory = Inventory.model_validate_json(json_str)
        
        # Verify all fields match
        assert retrieved_inventory.inventory_id == inventory.inventory_id
        assert retrieved_inventory.sku == inventory.sku
        assert retrieved_inventory.warehouse_id == inventory.warehouse_id
        assert retrieved_inventory.quantity_on_hand == inventory.quantity_on_hand
        assert retrieved_inventory.quantity_reserved == inventory.quantity_reserved
        assert retrieved_inventory.quantity_available == inventory.quantity_available

    def test_forecast_json_serialization_round_trip(self):
        """Test that Forecast can be serialized to JSON and deserialized back.
        
        Property: *For any* supply chain data, storing and retrieving the data 
        should return the exact same values with all fields intact.
        """
        forecast_data = {
            "forecast_id": "FCST-001",
            "sku": "PROD-001",
            "forecast_date": date.today(),
            "forecast_period": "2024-01-01 to 2024-01-30",
            "forecasted_demand": 1000,
            "confidence_80": 950.0,
            "confidence_95": 900.0,
        }
        
        forecast = Forecast(**forecast_data)
        
        # Serialize to JSON string
        json_str = forecast.model_dump_json()
        
        # Deserialize from JSON string
        retrieved_forecast = Forecast.model_validate_json(json_str)
        
        # Verify all fields match
        assert retrieved_forecast.forecast_id == forecast.forecast_id
        assert retrieved_forecast.sku == forecast.sku
        assert retrieved_forecast.forecast_date == forecast.forecast_date
        assert retrieved_forecast.forecast_period == forecast.forecast_period
        assert retrieved_forecast.forecasted_demand == forecast.forecasted_demand
        assert retrieved_forecast.confidence_80 == forecast.confidence_80
        assert retrieved_forecast.confidence_95 == forecast.confidence_95

    def test_purchase_order_json_serialization_round_trip(self):
        """Test that PurchaseOrder can be serialized to JSON and deserialized back.
        
        Property: *For any* supply chain data, storing and retrieving the data 
        should return the exact same values with all fields intact.
        """
        po_data = {
            "po_id": "PO-001",
            "sku": "PROD-001",
            "supplier_id": "SUP-001",
            "quantity": 100,
            "unit_price": 10.50,
            "expected_delivery_date": date.today() + timedelta(days=7),
            "status": "pending",
        }
        
        purchase_order = PurchaseOrder(**po_data)
        
        # Serialize to JSON string
        json_str = purchase_order.model_dump_json()
        
        # Deserialize from JSON string
        retrieved_po = PurchaseOrder.model_validate_json(json_str)
        
        # Verify all fields match
        assert retrieved_po.po_id == purchase_order.po_id
        assert retrieved_po.sku == purchase_order.sku
        assert retrieved_po.supplier_id == purchase_order.supplier_id
        assert retrieved_po.quantity == purchase_order.quantity
        assert retrieved_po.unit_price == purchase_order.unit_price
        assert retrieved_po.total_cost == purchase_order.total_cost
        assert retrieved_po.expected_delivery_date == purchase_order.expected_delivery_date
        assert retrieved_po.status == purchase_order.status
