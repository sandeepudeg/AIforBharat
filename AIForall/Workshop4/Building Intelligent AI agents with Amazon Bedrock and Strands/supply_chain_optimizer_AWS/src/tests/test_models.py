"""Tests for data models."""

from datetime import datetime, date, timedelta
import json

import pytest
from hypothesis import given, strategies as st

from src.models import (
    Product,
    ProductValidator,
    Inventory,
    InventoryValidator,
    Forecast,
    ForecastValidator,
    PurchaseOrder,
    PurchaseOrderValidator,
    Supplier,
    SupplierValidator,
    Anomaly,
    AnomalyValidator,
    Report,
    ReportValidator,
)
from src.models.purchase_order import POStatus
from src.models.anomaly import AnomalyType, SeverityLevel, AnomalyStatus
from src.models.report import ReportType


class TestProductModel:
    """Tests for Product model."""

    def test_product_creation_valid(self):
        """Test creating a valid product."""
        product = Product(
            sku="PROD-001",
            name="Widget A",
            category="Electronics",
            unit_cost=10.50,
            holding_cost_per_unit=2.10,
            ordering_cost=50.00,
            lead_time_days=7,
            supplier_id="SUP-001",
        )
        assert product.sku == "PROD-001"
        assert product.name == "Widget A"
        assert product.unit_cost == 10.50

    def test_product_validation_empty_sku(self):
        """Test product validation with empty SKU."""
        with pytest.raises(ValueError):
            Product(
                sku="",
                name="Widget A",
                category="Electronics",
                unit_cost=10.50,
                holding_cost_per_unit=2.10,
                ordering_cost=50.00,
                lead_time_days=7,
                supplier_id="SUP-001",
            )

    def test_product_validation_negative_cost(self):
        """Test product validation with negative cost."""
        with pytest.raises(ValueError):
            Product(
                sku="PROD-001",
                name="Widget A",
                category="Electronics",
                unit_cost=-10.50,
                holding_cost_per_unit=2.10,
                ordering_cost=50.00,
                lead_time_days=7,
                supplier_id="SUP-001",
            )

    def test_product_validator(self):
        """Test ProductValidator."""
        data = {
            "sku": "PROD-001",
            "name": "Widget A",
            "category": "Electronics",
            "unit_cost": 10.50,
            "holding_cost_per_unit": 2.10,
            "ordering_cost": 50.00,
            "lead_time_days": 7,
            "supplier_id": "SUP-001",
        }
        product = ProductValidator.validate(data)
        assert product.sku == "PROD-001"


class TestInventoryModel:
    """Tests for Inventory model."""

    def test_inventory_creation_valid(self):
        """Test creating a valid inventory record."""
        inventory = Inventory(
            inventory_id="INV-001",
            sku="PROD-001",
            warehouse_id="WH-001",
            quantity_on_hand=500,
            quantity_reserved=100,
        )
        assert inventory.inventory_id == "INV-001"
        assert inventory.quantity_available == 400

    def test_inventory_available_calculation(self):
        """Test that available quantity is calculated correctly."""
        inventory = Inventory(
            inventory_id="INV-001",
            sku="PROD-001",
            warehouse_id="WH-001",
            quantity_on_hand=500,
            quantity_reserved=150,
        )
        assert inventory.quantity_available == 350

    def test_inventory_validation_empty_id(self):
        """Test inventory validation with empty ID."""
        with pytest.raises(ValueError):
            Inventory(
                inventory_id="",
                sku="PROD-001",
                warehouse_id="WH-001",
                quantity_on_hand=500,
            )

    def test_inventory_validator(self):
        """Test InventoryValidator."""
        data = {
            "inventory_id": "INV-001",
            "sku": "PROD-001",
            "warehouse_id": "WH-001",
            "quantity_on_hand": 500,
            "quantity_reserved": 100,
        }
        inventory = InventoryValidator.validate(data)
        assert inventory.inventory_id == "INV-001"


class TestForecastModel:
    """Tests for Forecast model."""

    def test_forecast_creation_valid(self):
        """Test creating a valid forecast."""
        forecast = Forecast(
            forecast_id="FCST-001",
            sku="PROD-001",
            forecast_date=date.today(),
            forecast_period="2024-01-01 to 2024-01-30",
            forecasted_demand=1000,
            confidence_80=950,
            confidence_95=900,
        )
        assert forecast.forecast_id == "FCST-001"
        assert forecast.forecasted_demand == 1000

    def test_forecast_confidence_intervals(self):
        """Test forecast confidence interval validation."""
        with pytest.raises(ValueError):
            Forecast(
                forecast_id="FCST-001",
                sku="PROD-001",
                forecast_date=date.today(),
                forecast_period="2024-01-01 to 2024-01-30",
                forecasted_demand=1000,
                confidence_80=900,
                confidence_95=950,  # Invalid: 95% should be <= 80%
            )

    def test_forecast_validator(self):
        """Test ForecastValidator."""
        data = {
            "forecast_id": "FCST-001",
            "sku": "PROD-001",
            "forecast_date": date.today(),
            "forecast_period": "2024-01-01 to 2024-01-30",
            "forecasted_demand": 1000,
            "confidence_80": 950,
            "confidence_95": 900,
        }
        forecast = ForecastValidator.validate(data)
        assert forecast.forecast_id == "FCST-001"


class TestPurchaseOrderModel:
    """Tests for PurchaseOrder model."""

    def test_purchase_order_creation_valid(self):
        """Test creating a valid purchase order."""
        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            expected_delivery_date=date.today() + timedelta(days=7),
        )
        assert po.po_id == "PO-001"
        assert po.total_cost == 1050.00

    def test_purchase_order_total_cost_calculation(self):
        """Test that total cost is calculated correctly."""
        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=50,
            unit_price=20.00,
            expected_delivery_date=date.today() + timedelta(days=7),
        )
        assert po.total_cost == 1000.00

    def test_purchase_order_status_enum(self):
        """Test purchase order status enum."""
        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            expected_delivery_date=date.today() + timedelta(days=7),
            status=POStatus.CONFIRMED,
        )
        assert po.status == POStatus.CONFIRMED

    def test_purchase_order_validator(self):
        """Test PurchaseOrderValidator."""
        data = {
            "po_id": "PO-001",
            "sku": "PROD-001",
            "supplier_id": "SUP-001",
            "quantity": 100,
            "unit_price": 10.50,
            "expected_delivery_date": date.today() + timedelta(days=7),
        }
        po = PurchaseOrderValidator.validate(data)
        assert po.po_id == "PO-001"


class TestSupplierModel:
    """Tests for Supplier model."""

    def test_supplier_creation_valid(self):
        """Test creating a valid supplier."""
        supplier = Supplier(
            supplier_id="SUP-001",
            name="Acme Supplies",
            contact_email="contact@acme.com",
            contact_phone="+1-555-0100",
            lead_time_days=7,
        )
        assert supplier.supplier_id == "SUP-001"
        assert supplier.name == "Acme Supplies"

    def test_supplier_validation_invalid_email(self):
        """Test supplier validation with invalid email."""
        with pytest.raises(ValueError):
            Supplier(
                supplier_id="SUP-001",
                name="Acme Supplies",
                contact_email="invalid-email",
                contact_phone="+1-555-0100",
                lead_time_days=7,
            )

    def test_supplier_validation_empty_name(self):
        """Test supplier validation with empty name."""
        with pytest.raises(ValueError):
            Supplier(
                supplier_id="SUP-001",
                name="",
                contact_email="contact@acme.com",
                contact_phone="+1-555-0100",
                lead_time_days=7,
            )

    def test_supplier_validator(self):
        """Test SupplierValidator."""
        data = {
            "supplier_id": "SUP-001",
            "name": "Acme Supplies",
            "contact_email": "contact@acme.com",
            "contact_phone": "+1-555-0100",
            "lead_time_days": 7,
        }
        supplier = SupplierValidator.validate(data)
        assert supplier.supplier_id == "SUP-001"


class TestAnomalyModel:
    """Tests for Anomaly model."""

    def test_anomaly_creation_valid(self):
        """Test creating a valid anomaly."""
        anomaly = Anomaly(
            anomaly_id="ANM-001",
            anomaly_type=AnomalyType.INVENTORY_DEVIATION,
            sku="PROD-001",
            warehouse_id="WH-001",
            severity=SeverityLevel.HIGH,
            confidence_score=0.95,
            description="Inventory level 30% below forecast",
        )
        assert anomaly.anomaly_id == "ANM-001"
        assert anomaly.severity == SeverityLevel.HIGH

    def test_anomaly_validation_invalid_confidence(self):
        """Test anomaly validation with invalid confidence score."""
        with pytest.raises(ValueError):
            Anomaly(
                anomaly_id="ANM-001",
                anomaly_type=AnomalyType.INVENTORY_DEVIATION,
                sku="PROD-001",
                severity=SeverityLevel.HIGH,
                confidence_score=1.5,  # Invalid: > 1
                description="Inventory level 30% below forecast",
            )

    def test_anomaly_validator(self):
        """Test AnomalyValidator."""
        data = {
            "anomaly_id": "ANM-001",
            "anomaly_type": AnomalyType.INVENTORY_DEVIATION,
            "sku": "PROD-001",
            "severity": SeverityLevel.HIGH,
            "confidence_score": 0.95,
            "description": "Inventory level 30% below forecast",
        }
        anomaly = AnomalyValidator.validate(data)
        assert anomaly.anomaly_id == "ANM-001"


class TestReportModel:
    """Tests for Report model."""

    def test_report_creation_valid(self):
        """Test creating a valid report."""
        report = Report(
            report_id="RPT-001",
            report_type=ReportType.WEEKLY,
            period_start=date.today() - timedelta(days=7),
            period_end=date.today(),
            inventory_turnover=4.5,
            stockout_rate=0.02,
            supplier_performance_score=92.0,
            forecast_accuracy=88.5,
            generated_by="Report Generation Agent",
        )
        assert report.report_id == "RPT-001"
        assert report.report_type == ReportType.WEEKLY

    def test_report_validation_invalid_dates(self):
        """Test report validation with invalid date range."""
        with pytest.raises(ValueError):
            Report(
                report_id="RPT-001",
                report_type=ReportType.WEEKLY,
                period_start=date.today(),
                period_end=date.today() - timedelta(days=7),  # End before start
                inventory_turnover=4.5,
                stockout_rate=0.02,
                supplier_performance_score=92.0,
                forecast_accuracy=88.5,
                generated_by="Report Generation Agent",
            )

    def test_report_validator(self):
        """Test ReportValidator."""
        data = {
            "report_id": "RPT-001",
            "report_type": ReportType.WEEKLY,
            "period_start": date.today() - timedelta(days=7),
            "period_end": date.today(),
            "inventory_turnover": 4.5,
            "stockout_rate": 0.02,
            "supplier_performance_score": 92.0,
            "forecast_accuracy": 88.5,
            "generated_by": "Report Generation Agent",
        }
        report = ReportValidator.validate(data)
        assert report.report_id == "RPT-001"


class TestBatchValidation:
    """Tests for batch validation."""

    def test_product_batch_validation(self):
        """Test batch validation for products."""
        data_list = [
            {
                "sku": "PROD-001",
                "name": "Widget A",
                "category": "Electronics",
                "unit_cost": 10.50,
                "holding_cost_per_unit": 2.10,
                "ordering_cost": 50.00,
                "lead_time_days": 7,
                "supplier_id": "SUP-001",
            },
            {
                "sku": "PROD-002",
                "name": "Widget B",
                "category": "Electronics",
                "unit_cost": 15.00,
                "holding_cost_per_unit": 3.00,
                "ordering_cost": 50.00,
                "lead_time_days": 5,
                "supplier_id": "SUP-002",
            },
        ]
        products = ProductValidator.validate_batch(data_list)
        assert len(products) == 2
        assert products[0].sku == "PROD-001"
        assert products[1].sku == "PROD-002"

    def test_inventory_batch_validation(self):
        """Test batch validation for inventory."""
        data_list = [
            {
                "inventory_id": "INV-001",
                "sku": "PROD-001",
                "warehouse_id": "WH-001",
                "quantity_on_hand": 500,
                "quantity_reserved": 100,
            },
            {
                "inventory_id": "INV-002",
                "sku": "PROD-002",
                "warehouse_id": "WH-002",
                "quantity_on_hand": 300,
                "quantity_reserved": 50,
            },
        ]
        inventories = InventoryValidator.validate_batch(data_list)
        assert len(inventories) == 2
        assert inventories[0].inventory_id == "INV-001"



# Property-Based Tests
# Feature: supply-chain-optimizer, Property 32: Data Persistence Round Trip

from hypothesis import settings, HealthCheck

# Hypothesis strategies for generating valid model data
# Use simple alphanumeric strings to avoid whitespace-only strings
simple_text = st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
simple_text_long = st.text(min_size=1, max_size=255, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

product_strategy = st.fixed_dictionaries({
    "sku": simple_text,
    "name": simple_text_long,
    "category": st.text(min_size=1, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
    "unit_cost": st.floats(min_value=0.01, max_value=10000),
    "holding_cost_per_unit": st.floats(min_value=0, max_value=1000),
    "ordering_cost": st.floats(min_value=0, max_value=1000),
    "lead_time_days": st.integers(min_value=0, max_value=365),
    "supplier_id": simple_text,
})

inventory_strategy = st.fixed_dictionaries({
    "inventory_id": simple_text,
    "sku": simple_text,
    "warehouse_id": simple_text,
    "quantity_on_hand": st.integers(min_value=0, max_value=100000),
    "quantity_reserved": st.integers(min_value=0, max_value=50000),  # Ensure reserved <= on_hand
})

forecast_strategy = st.fixed_dictionaries({
    "forecast_id": simple_text,
    "sku": simple_text,
    "forecast_date": st.dates(),
    "forecast_period": st.text(min_size=1, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
    "forecasted_demand": st.integers(min_value=0, max_value=1000000),
    "confidence_80": st.floats(min_value=0, max_value=1000000),
    "confidence_95": st.floats(min_value=0, max_value=1000000),
})

supplier_strategy = st.fixed_dictionaries({
    "supplier_id": simple_text,
    "name": simple_text_long,
    "contact_email": st.emails(),
    "contact_phone": st.text(min_size=1, max_size=20, alphabet='0123456789+-'),
    "lead_time_days": st.integers(min_value=0, max_value=365),
})

anomaly_strategy = st.fixed_dictionaries({
    "anomaly_id": simple_text,
    "anomaly_type": st.sampled_from([AnomalyType.INVENTORY_DEVIATION, AnomalyType.SUPPLIER_DELAY, 
                                      AnomalyType.DEMAND_SPIKE, AnomalyType.INVENTORY_SHRINKAGE]),
    "sku": simple_text,
    "severity": st.sampled_from([SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]),
    "confidence_score": st.floats(min_value=0, max_value=1),
    "description": st.text(min_size=1, max_size=1000, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
})

report_strategy = st.fixed_dictionaries({
    "report_id": simple_text,
    "report_type": st.sampled_from([ReportType.DAILY, ReportType.WEEKLY, ReportType.MONTHLY, ReportType.CUSTOM]),
    "period_start": st.dates(),
    "period_end": st.dates(),
    "inventory_turnover": st.floats(min_value=0, max_value=1000),
    "stockout_rate": st.floats(min_value=0, max_value=1),
    "supplier_performance_score": st.floats(min_value=0, max_value=100),
    "forecast_accuracy": st.floats(min_value=0, max_value=100),
    "generated_by": simple_text_long,
})


class TestDataPersistenceRoundTrip:
    """Property-based tests for data persistence round trip.
    
    Feature: supply-chain-optimizer, Property 32: Data Persistence Round Trip
    Validates: Requirements 8.1, 8.2
    
    For any supply chain data (inventory, forecast, order, anomaly), storing and 
    retrieving the data should return the exact same values with all fields intact.
    """

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(product_strategy)
    def test_product_persistence_round_trip(self, product_data):
        """Test that Product data survives serialization and deserialization.
        
        For any valid product data, creating a Product, converting to dict,
        and recreating from dict should produce an equivalent Product.
        """
        # Create product from data
        product = Product(**product_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = product.model_dump()
        
        # Deserialize back to Product
        retrieved_product = Product(**persisted_data)
        
        # Verify all fields match
        assert retrieved_product.sku == product.sku
        assert retrieved_product.name == product.name
        assert retrieved_product.category == product.category
        assert retrieved_product.unit_cost == product.unit_cost
        assert retrieved_product.holding_cost_per_unit == product.holding_cost_per_unit
        assert retrieved_product.ordering_cost == product.ordering_cost
        assert retrieved_product.lead_time_days == product.lead_time_days
        assert retrieved_product.supplier_id == product.supplier_id

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(inventory_strategy)
    def test_inventory_persistence_round_trip(self, inventory_data):
        """Test that Inventory data survives serialization and deserialization.
        
        For any valid inventory data, creating an Inventory, converting to dict,
        and recreating from dict should produce an equivalent Inventory.
        """
        # Ensure quantity_reserved doesn't exceed quantity_on_hand
        if inventory_data["quantity_reserved"] > inventory_data["quantity_on_hand"]:
            inventory_data["quantity_reserved"] = inventory_data["quantity_on_hand"]
        
        # Create inventory from data
        inventory = Inventory(**inventory_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = inventory.model_dump()
        
        # Deserialize back to Inventory
        retrieved_inventory = Inventory(**persisted_data)
        
        # Verify all fields match
        assert retrieved_inventory.inventory_id == inventory.inventory_id
        assert retrieved_inventory.sku == inventory.sku
        assert retrieved_inventory.warehouse_id == inventory.warehouse_id
        assert retrieved_inventory.quantity_on_hand == inventory.quantity_on_hand
        assert retrieved_inventory.quantity_reserved == inventory.quantity_reserved
        assert retrieved_inventory.quantity_available == inventory.quantity_available

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(forecast_strategy)
    def test_forecast_persistence_round_trip(self, forecast_data):
        """Test that Forecast data survives serialization and deserialization.
        
        For any valid forecast data, creating a Forecast, converting to dict,
        and recreating from dict should produce an equivalent Forecast.
        """
        # Ensure confidence_95 <= confidence_80 for valid data
        if forecast_data["confidence_95"] > forecast_data["confidence_80"]:
            forecast_data["confidence_95"] = forecast_data["confidence_80"]
        
        # Create forecast from data
        forecast = Forecast(**forecast_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = forecast.model_dump()
        
        # Deserialize back to Forecast
        retrieved_forecast = Forecast(**persisted_data)
        
        # Verify all fields match
        assert retrieved_forecast.forecast_id == forecast.forecast_id
        assert retrieved_forecast.sku == forecast.sku
        assert retrieved_forecast.forecast_date == forecast.forecast_date
        assert retrieved_forecast.forecast_period == forecast.forecast_period
        assert retrieved_forecast.forecasted_demand == forecast.forecasted_demand
        assert retrieved_forecast.confidence_80 == forecast.confidence_80
        assert retrieved_forecast.confidence_95 == forecast.confidence_95

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(supplier_strategy)
    def test_supplier_persistence_round_trip(self, supplier_data):
        """Test that Supplier data survives serialization and deserialization.
        
        For any valid supplier data, creating a Supplier, converting to dict,
        and recreating from dict should produce an equivalent Supplier.
        """
        # Create supplier from data
        supplier = Supplier(**supplier_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = supplier.model_dump()
        
        # Deserialize back to Supplier
        retrieved_supplier = Supplier(**persisted_data)
        
        # Verify all fields match
        assert retrieved_supplier.supplier_id == supplier.supplier_id
        assert retrieved_supplier.name == supplier.name
        assert retrieved_supplier.contact_email == supplier.contact_email
        assert retrieved_supplier.contact_phone == supplier.contact_phone
        assert retrieved_supplier.lead_time_days == supplier.lead_time_days

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(anomaly_strategy)
    def test_anomaly_persistence_round_trip(self, anomaly_data):
        """Test that Anomaly data survives serialization and deserialization.
        
        For any valid anomaly data, creating an Anomaly, converting to dict,
        and recreating from dict should produce an equivalent Anomaly.
        """
        # Create anomaly from data
        anomaly = Anomaly(**anomaly_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = anomaly.model_dump()
        
        # Deserialize back to Anomaly
        retrieved_anomaly = Anomaly(**persisted_data)
        
        # Verify all fields match
        assert retrieved_anomaly.anomaly_id == anomaly.anomaly_id
        assert retrieved_anomaly.anomaly_type == anomaly.anomaly_type
        assert retrieved_anomaly.sku == anomaly.sku
        assert retrieved_anomaly.severity == anomaly.severity
        assert retrieved_anomaly.confidence_score == anomaly.confidence_score
        assert retrieved_anomaly.description == anomaly.description

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(report_strategy)
    def test_report_persistence_round_trip(self, report_data):
        """Test that Report data survives serialization and deserialization.
        
        For any valid report data, creating a Report, converting to dict,
        and recreating from dict should produce an equivalent Report.
        """
        # Ensure period_end >= period_start
        if report_data["period_end"] < report_data["period_start"]:
            report_data["period_end"] = report_data["period_start"]
        
        # Create report from data
        report = Report(**report_data)
        
        # Serialize to dict (simulating persistence)
        persisted_data = report.model_dump()
        
        # Deserialize back to Report
        retrieved_report = Report(**persisted_data)
        
        # Verify all fields match
        assert retrieved_report.report_id == report.report_id
        assert retrieved_report.report_type == report.report_type
        assert retrieved_report.period_start == report.period_start
        assert retrieved_report.period_end == report.period_end
        assert retrieved_report.inventory_turnover == report.inventory_turnover
        assert retrieved_report.stockout_rate == report.stockout_rate
        assert retrieved_report.supplier_performance_score == report.supplier_performance_score
        assert retrieved_report.forecast_accuracy == report.forecast_accuracy
        assert retrieved_report.generated_by == report.generated_by
