"""AWS Integration Tests - Test complete workflow with AWS services."""

import pytest
from datetime import datetime, timedelta
from src.agents.demand_forecasting_agent import DemandForecastingAgent
from src.agents.inventory_optimizer_agent import InventoryOptimizerAgent
from src.agents.supplier_coordination_agent import SupplierCoordinationAgent
from src.agents.anomaly_detection_agent import AnomalyDetectionAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.config import logger


@pytest.fixture
def agents():
    """Initialize all agents."""
    return {
        'forecasting': DemandForecastingAgent(),
        'inventory': InventoryOptimizerAgent(),
        'supplier': SupplierCoordinationAgent(),
        'anomaly': AnomalyDetectionAgent(),
        'reporting': ReportGenerationAgent(),
    }


class TestDemandForecastingWithAWS:
    """Test demand forecasting agent with AWS services."""
    
    def test_forecast_generation(self, agents):
        """Test forecast generation and storage."""
        agent = agents['forecasting']
        
        # Generate forecast
        sales_data = [
            {"date": f"2025-{(12-i):02d}-01", "quantity": 100 + i*5}
            for i in range(12)
        ]
        
        analysis = agent.analyze_sales_history(
            sku="PROD-AWS-001",
            sales_data=sales_data
        )
        
        assert analysis is not None
        assert 'average_demand' in analysis
        logger.info(f"Forecast analysis: {analysis}")
        
        forecast = agent.generate_forecast(
            sku="PROD-AWS-001",
            sales_analysis=analysis,
            forecast_period=30
        )
        
        assert forecast is not None
        assert forecast['forecasted_demand'] > 0
        assert 'confidence_80' in forecast
        assert 'confidence_95' in forecast
        logger.info(f"Forecast generated: {forecast['forecasted_demand']} units")


class TestInventoryOptimizationWithAWS:
    """Test inventory optimization agent with AWS services."""
    
    def test_eoq_calculation(self, agents):
        """Test EOQ calculation."""
        agent = agents['inventory']
        
        eoq = agent.calculate_eoq(
            annual_demand=36000,
            ordering_cost=50,
            holding_cost_per_unit=2
        )
        
        assert eoq > 0
        assert eoq == pytest.approx(3000, rel=0.01)
        logger.info(f"EOQ calculated: {eoq} units")
    
    def test_reorder_point_calculation(self, agents):
        """Test reorder point calculation."""
        agent = agents['inventory']
        
        reorder_point = agent.calculate_reorder_point(
            average_daily_demand=100,
            lead_time_days=7,
            safety_stock=200
        )
        
        assert reorder_point > 0
        assert reorder_point >= 200  # At least safety stock
        logger.info(f"Reorder point calculated: {reorder_point} units")


class TestSupplierCoordinationWithAWS:
    """Test supplier coordination agent with AWS services."""
    
    def test_purchase_order_placement(self, agents):
        """Test purchase order placement."""
        agent = agents['supplier']
        
        po = agent.send_purchase_order(
            po_id=f"PO-AWS-{datetime.now().timestamp()}",
            sku="PROD-AWS-001",
            supplier_id="SUPP-001",
            quantity=1000,
            unit_price=10.50,
            delivery_date=(datetime.now() + timedelta(days=7)).isoformat()
        )
        
        assert po is not None
        assert po['status'] in ['pending', 'confirmed']
        logger.info(f"Purchase order placed: {po['po_id']}")
    
    def test_supplier_comparison(self, agents):
        """Test supplier comparison."""
        agent = agents['supplier']
        
        suppliers = [
            {
                'supplier_id': 'SUPP-001',
                'name': 'Supplier A',
                'price': 10.00,
                'lead_time': 7,
                'reliability_score': 95,
                'on_time_delivery_rate': 0.98,
            },
            {
                'supplier_id': 'SUPP-002',
                'name': 'Supplier B',
                'price': 9.50,
                'lead_time': 10,
                'reliability_score': 90,
                'on_time_delivery_rate': 0.95,
            },
        ]
        
        comparison = agent.compare_suppliers(suppliers)
        
        assert comparison is not None
        assert 'best_supplier' in comparison
        logger.info(f"Best supplier: {comparison['best_supplier']}")


class TestAnomalyDetectionWithAWS:
    """Test anomaly detection agent with AWS services."""
    
    def test_inventory_anomaly_detection(self, agents):
        """Test inventory anomaly detection."""
        agent = agents['anomaly']
        
        anomaly = agent.detect_inventory_anomaly(
            sku="PROD-AWS-001",
            current_inventory=500,
            forecasted_inventory=1000,
            confidence_80=950,
            confidence_95=900
        )
        
        assert anomaly is not None
        assert 'is_anomaly' in anomaly
        logger.info(f"Anomaly detection result: {anomaly['is_anomaly']}")
    
    def test_demand_spike_detection(self, agents):
        """Test demand spike detection."""
        agent = agents['anomaly']
        
        anomaly = agent.detect_demand_spike(
            sku="PROD-AWS-001",
            current_demand=500,
            historical_average=100
        )
        
        assert anomaly is not None
        assert 'is_spike' in anomaly
        logger.info(f"Demand spike detected: {anomaly['is_spike']}")


class TestReportGenerationWithAWS:
    """Test report generation agent with AWS services."""
    
    def test_kpi_calculation(self, agents):
        """Test KPI calculation."""
        agent = agents['reporting']
        
        kpis = agent.calculate_kpis(
            inventory_data=[
                {'sku': 'PROD-001', 'quantity': 1000, 'value': 50000},
                {'sku': 'PROD-002', 'quantity': 500, 'value': 25000},
            ],
            forecast_data=[
                {'sku': 'PROD-001', 'forecasted': 100, 'actual': 95},
                {'sku': 'PROD-002', 'forecasted': 50, 'actual': 52},
            ],
            supplier_data=[
                {'supplier_id': 'SUPP-001', 'reliability_score': 95},
                {'supplier_id': 'SUPP-002', 'reliability_score': 90},
            ],
            period_start=datetime.now().date(),
            period_end=datetime.now().date()
        )
        
        assert kpis is not None
        assert 'inventory_turnover' in kpis
        assert 'forecast_accuracy' in kpis
        assert 'supplier_reliability' in kpis
        logger.info(f"KPIs calculated: {kpis}")
    
    def test_report_generation(self, agents):
        """Test report generation."""
        agent = agents['reporting']
        
        report = agent.generate_report(
            period_start=datetime.now().date(),
            period_end=datetime.now().date(),
            report_type='daily'
        )
        
        assert report is not None
        assert 'report_id' in report
        assert 'kpis' in report
        logger.info(f"Report generated: {report['report_id']}")


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_complete_daily_optimization(self, agents):
        """Test complete daily optimization workflow."""
        logger.info("Starting end-to-end workflow test...")
        
        # Step 1: Forecast demand
        logger.info("Step 1: Forecasting demand...")
        forecasting_agent = agents['forecasting']
        sales_data = [
            {"date": f"2025-{(12-i):02d}-01", "quantity": 100 + i*5}
            for i in range(12)
        ]
        
        analysis = forecasting_agent.analyze_sales_history(
            sku="PROD-E2E-001",
            sales_data=sales_data
        )
        
        forecast = forecasting_agent.generate_forecast(
            sku="PROD-E2E-001",
            sales_analysis=analysis,
            forecast_period=30
        )
        
        assert forecast['forecasted_demand'] > 0
        logger.info(f"✓ Demand forecast: {forecast['forecasted_demand']} units")
        
        # Step 2: Optimize inventory
        logger.info("Step 2: Optimizing inventory...")
        inventory_agent = agents['inventory']
        
        eoq = inventory_agent.calculate_eoq(
            annual_demand=forecast['forecasted_demand'] * 12,
            ordering_cost=50,
            holding_cost_per_unit=2
        )
        
        reorder_point = inventory_agent.calculate_reorder_point(
            average_daily_demand=forecast['forecasted_demand'] / 30,
            lead_time_days=7,
            safety_stock=200
        )
        
        assert eoq > 0
        assert reorder_point > 0
        logger.info(f"✓ EOQ: {eoq} units, Reorder point: {reorder_point} units")
        
        # Step 3: Detect anomalies
        logger.info("Step 3: Detecting anomalies...")
        anomaly_agent = agents['anomaly']
        
        anomaly = anomaly_agent.detect_inventory_anomaly(
            sku="PROD-E2E-001",
            current_inventory=reorder_point + 500,
            forecasted_inventory=forecast['forecasted_demand'],
            confidence_80=forecast['confidence_80'],
            confidence_95=forecast['confidence_95']
        )
        
        assert anomaly is not None
        logger.info(f"✓ Anomaly detection: {anomaly['is_anomaly']}")
        
        # Step 4: Generate report
        logger.info("Step 4: Generating report...")
        reporting_agent = agents['reporting']
        
        kpis = reporting_agent.calculate_kpis(
            inventory_data=[
                {'sku': 'PROD-E2E-001', 'quantity': reorder_point + 500, 'value': (reorder_point + 500) * 10}
            ],
            forecast_data=[
                {'sku': 'PROD-E2E-001', 'forecasted': forecast['forecasted_demand'], 'actual': forecast['forecasted_demand']}
            ],
            supplier_data=[
                {'supplier_id': 'SUPP-001', 'reliability_score': 95}
            ],
            period_start=datetime.now().date(),
            period_end=datetime.now().date()
        )
        
        assert 'inventory_turnover' in kpis
        logger.info(f"✓ KPIs calculated: {list(kpis.keys())}")
        
        logger.info("\n✓ End-to-end workflow completed successfully!")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
