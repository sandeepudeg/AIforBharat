"""Integration tests for API endpoints."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.api.app import create_app
from src.models.inventory import Inventory
from src.models.purchase_order import PurchaseOrder
from src.models.report import Report
from src.models.anomaly import Anomaly
from src.models.supplier import Supplier


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    response = client.post(
        "/api/auth/token",
        json={"username": "test@example.com", "password": "password"}
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "supply-chain-optimizer-api"


class TestAuthentication:
    """Test authentication endpoints."""

    def test_get_token(self, client):
        """Test token generation."""
        response = client.post(
            "/api/auth/token",
            json={"username": "test@example.com", "password": "password"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    def test_get_token_missing_credentials(self, client):
        """Test token generation with missing credentials."""
        response = client.post(
            "/api/auth/token",
            json={"username": "test@example.com"}
        )
        assert response.status_code == 400


class TestInventoryEndpoints:
    """Test inventory query endpoints."""

    @patch("src.api.inventory_routes.get_dynamodb_connection")
    def test_query_inventory(self, mock_dynamodb, client, auth_headers):
        """Test inventory query endpoint."""
        mock_table = MagicMock()
        mock_dynamodb.return_value.Table.return_value = mock_table

        # Mock inventory data
        inventory_data = {
            "inventory_id": "INV-001",
            "sku": "PROD-001",
            "warehouse_id": "WH-001",
            "quantity_on_hand": 500,
            "quantity_reserved": 100,
            "quantity_available": 400,
            "reorder_point": 100,
        }

        mock_table.query.return_value = {
            "Items": [inventory_data],
            "Count": 1,
        }

        response = client.get(
            "/api/inventory/query?sku=PROD-001",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["sku"] == "PROD-001"

    @patch("src.api.inventory_routes.get_dynamodb_connection")
    def test_get_inventory_by_id(self, mock_dynamodb, client, auth_headers):
        """Test get inventory by ID endpoint."""
        mock_table = MagicMock()
        mock_dynamodb.return_value.Table.return_value = mock_table

        inventory_data = {
            "inventory_id": "INV-001",
            "sku": "PROD-001",
            "warehouse_id": "WH-001",
            "quantity_on_hand": 500,
        }

        mock_table.get_item.return_value = {"Item": inventory_data}

        response = client.get(
            "/api/inventory/INV-001",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["inventory_id"] == "INV-001"

    @patch("src.api.inventory_routes.get_dynamodb_connection")
    def test_get_low_stock_items(self, mock_dynamodb, client, auth_headers):
        """Test get low stock items endpoint."""
        mock_table = MagicMock()
        mock_dynamodb.return_value.Table.return_value = mock_table

        inventory_data = {
            "inventory_id": "INV-001",
            "sku": "PROD-001",
            "warehouse_id": "WH-001",
            "quantity_on_hand": 50,
            "reorder_point": 100,
        }

        mock_table.scan.return_value = {
            "Items": [inventory_data],
            "Count": 1,
        }

        response = client.get(
            "/api/inventory/low-stock",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1


class TestPurchaseOrderEndpoints:
    """Test purchase order management endpoints."""

    @patch("src.api.purchase_order_routes.get_rds_session")
    def test_list_purchase_orders(self, mock_session, client, auth_headers):
        """Test list purchase orders endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            total_cost=1050.0,
            order_date=datetime.utcnow(),
            expected_delivery_date=(datetime.utcnow() + timedelta(days=7)).date(),
            status="pending",
        )

        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.limit.return_value.offset.return_value.all.return_value = [po]
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/purchase-orders",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1

    @patch("src.api.purchase_order_routes.get_rds_session")
    def test_get_purchase_order(self, mock_session, client, auth_headers):
        """Test get purchase order endpoint."""
        mock_db_session = MagicMock()
        mock_session.return_value = mock_db_session

        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            total_cost=1050.0,
            order_date=datetime.utcnow(),
            expected_delivery_date=(datetime.utcnow() + timedelta(days=7)).date(),
            status="pending",
        )

        # Mock the query chain properly
        mock_filter = MagicMock()
        mock_filter.first.return_value = po
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        mock_db_session.close = MagicMock()

        response = client.get(
            "/api/purchase-orders/PO-001",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["po_id"] == "PO-001"

    @patch("src.api.purchase_order_routes.get_rds_session")
    def test_update_purchase_order_status(self, mock_session, client, auth_headers):
        """Test update purchase order status endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_session.return_value = mock_db_session

        po = PurchaseOrder(
            po_id="PO-001",
            sku="PROD-001",
            supplier_id="SUP-001",
            quantity=100,
            unit_price=10.50,
            total_cost=1050.0,
            order_date=datetime.utcnow(),
            expected_delivery_date=(datetime.utcnow() + timedelta(days=7)).date(),
            status="pending",
        )

        mock_query = MagicMock()
        mock_query.first.return_value = po
        mock_db_session.query.return_value.filter.return_value = mock_query

        response = client.patch(
            "/api/purchase-orders/PO-001/status",
            json={"status": "shipped"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "shipped"


class TestReportEndpoints:
    """Test report retrieval endpoints."""

    @patch("src.api.report_routes.get_rds_session")
    def test_list_reports(self, mock_session, client, auth_headers):
        """Test list reports endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        report = Report(
            report_id="RPT-001",
            report_type="daily",
            period_start=datetime.utcnow().date(),
            period_end=datetime.utcnow().date(),
            inventory_turnover=5.2,
            stockout_rate=0.02,
            supplier_performance_score=92.5,
            forecast_accuracy=0.88,
            cost_savings=15000.0,
            recommendations=["Increase safety stock", "Review supplier performance"],
            generated_at=datetime.utcnow(),
            generated_by="report_agent",
        )

        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [report]
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/reports",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1

    @patch("src.api.report_routes.get_rds_session")
    def test_get_report(self, mock_session, client, auth_headers):
        """Test get report endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        report = Report(
            report_id="RPT-001",
            report_type="daily",
            period_start=datetime.utcnow().date(),
            period_end=datetime.utcnow().date(),
            inventory_turnover=5.2,
            stockout_rate=0.02,
            supplier_performance_score=92.5,
            forecast_accuracy=0.88,
            cost_savings=15000.0,
            recommendations=["Increase safety stock"],
            generated_at=datetime.utcnow(),
            generated_by="report_agent",
        )

        mock_query = MagicMock()
        mock_query.first.return_value = report
        mock_db_session.query.return_value.filter.return_value = mock_query

        response = client.get(
            "/api/reports/RPT-001",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["report_id"] == "RPT-001"


class TestAnomalyEndpoints:
    """Test anomaly query endpoints."""

    @patch("src.api.anomaly_routes.get_rds_session")
    def test_list_anomalies(self, mock_session, client, auth_headers):
        """Test list anomalies endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        anomaly = Anomaly(
            anomaly_id="ANM-001",
            anomaly_type="inventory_deviation",
            sku="PROD-001",
            warehouse_id="WH-001",
            severity="high",
            confidence_score=0.92,
            description="Inventory deviation detected",
            root_cause="Unrecorded shipment",
            recommended_action="Investigate and reconcile",
            status="open",
            created_at=datetime.utcnow(),
        )

        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [anomaly]
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/anomalies",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1

    @patch("src.api.anomaly_routes.get_rds_session")
    def test_get_critical_anomalies(self, mock_session, client, auth_headers):
        """Test get critical anomalies endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        anomaly = Anomaly(
            anomaly_id="ANM-001",
            anomaly_type="inventory_deviation",
            sku="PROD-001",
            warehouse_id="WH-001",
            severity="critical",
            confidence_score=0.98,
            description="Critical inventory deviation",
            root_cause="System error",
            recommended_action="Immediate investigation",
            status="open",
            created_at=datetime.utcnow(),
        )

        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = [anomaly]
        mock_db_session.query.return_value.filter.return_value = mock_query

        response = client.get(
            "/api/anomalies/critical",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1


class TestSupplierEndpoints:
    """Test supplier management endpoints."""

    @patch("src.api.supplier_routes.get_rds_session")
    def test_list_suppliers(self, mock_session, client, auth_headers):
        """Test list suppliers endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        supplier = Supplier(
            supplier_id="SUP-001",
            name="Supplier A",
            contact_email="contact@supplier-a.com",
            contact_phone="+1-555-0123",
            lead_time_days=7,
            reliability_score=95.0,
            average_delivery_days=6.5,
            price_competitiveness=85.0,
            on_time_delivery_rate=0.95,
            total_orders=50,
        )

        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.limit.return_value.offset.return_value.all.return_value = [supplier]
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/suppliers",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1

    @patch("src.api.supplier_routes.get_rds_session")
    def test_get_supplier(self, mock_session, client, auth_headers):
        """Test get supplier endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        supplier = Supplier(
            supplier_id="SUP-001",
            name="Supplier A",
            contact_email="contact@supplier-a.com",
            contact_phone="+1-555-0123",
            lead_time_days=7,
            reliability_score=95.0,
            average_delivery_days=6.5,
            price_competitiveness=85.0,
            on_time_delivery_rate=0.95,
            total_orders=50,
        )

        mock_query = MagicMock()
        mock_query.first.return_value = supplier
        mock_db_session.query.return_value.filter.return_value = mock_query

        response = client.get(
            "/api/suppliers/SUP-001",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["supplier_id"] == "SUP-001"

    @patch("src.api.supplier_routes.get_rds_session")
    def test_get_top_performers(self, mock_session, client, auth_headers):
        """Test get top performers endpoint."""
        mock_db_session = MagicMock()
        mock_db_session.close = MagicMock()
        mock_session.return_value = mock_db_session

        supplier = Supplier(
            supplier_id="SUP-001",
            name="Supplier A",
            contact_email="contact@supplier-a.com",
            contact_phone="+1-555-0123",
            lead_time_days=7,
            reliability_score=98.0,
            average_delivery_days=6.5,
            price_competitiveness=90.0,
            on_time_delivery_rate=0.98,
            total_orders=100,
        )

        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [supplier]
        mock_db_session.query.return_value = mock_query

        response = client.get(
            "/api/suppliers/top-performers",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
