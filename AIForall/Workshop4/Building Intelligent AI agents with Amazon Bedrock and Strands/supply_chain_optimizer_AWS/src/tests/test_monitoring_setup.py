"""Tests for monitoring setup and initialization."""

from unittest.mock import MagicMock, patch
import pytest

from src.observability.setup import MonitoringSetup, setup_monitoring


class TestMonitoringSetup:
    """Tests for MonitoringSetup class."""

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_setup_all(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test setup_all method."""
        mock_metrics = MagicMock()
        mock_alarms = MagicMock()
        mock_dashboards = MagicMock()
        
        mock_metrics_class.return_value = mock_metrics
        mock_alarms_class.return_value = mock_alarms
        mock_dashboards_class.return_value = mock_dashboards

        setup = MonitoringSetup()
        result = setup.setup_all()

        assert "dashboards" in result
        assert "alarms" in result

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_setup_dashboards(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test setup_dashboards method."""
        mock_dashboards = MagicMock()
        mock_dashboards.create_main_dashboard.return_value = True
        mock_dashboards.create_agent_dashboard.return_value = True
        mock_dashboards.create_sla_dashboard.return_value = True
        
        mock_dashboards_class.return_value = mock_dashboards

        setup = MonitoringSetup()
        result = setup.setup_dashboards()

        assert result["main_dashboard"] is True
        assert result["agent_dashboard"] is True
        assert result["sla_dashboard"] is True
        mock_dashboards.create_main_dashboard.assert_called_once()
        mock_dashboards.create_agent_dashboard.assert_called_once()
        mock_dashboards.create_sla_dashboard.assert_called_once()

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_setup_alarms(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test setup_alarms method."""
        mock_alarms = MagicMock()
        mock_alarms.create_report_generation_sla_alarm.return_value = True
        mock_alarms.create_agent_failure_alarm.return_value = True
        mock_alarms.create_agent_performance_alarm.return_value = True
        mock_alarms.create_forecast_accuracy_alarm.return_value = True
        
        mock_alarms_class.return_value = mock_alarms

        setup = MonitoringSetup()
        result = setup.setup_alarms()

        assert result["standard_report_sla"] is True
        assert result["comprehensive_report_sla"] is True
        assert result["forecast_accuracy"] is True
        
        # Check that agent alarms were created
        assert "DemandForecastingAgentFailureAlarm" in result or \
               any("DemandForecastingAgent" in key for key in result.keys())

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_cleanup_dashboards(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test cleanup_dashboards method."""
        mock_dashboards = MagicMock()
        mock_dashboards.delete_dashboard.return_value = True
        
        mock_dashboards_class.return_value = mock_dashboards

        setup = MonitoringSetup()
        result = setup.cleanup_dashboards()

        assert result["SupplyChainOptimizer"] is True
        assert result["AgentMetrics"] is True
        assert result["SLAMetrics"] is True
        assert mock_dashboards.delete_dashboard.call_count == 3

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_cleanup_alarms(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test cleanup_alarms method."""
        mock_alarms = MagicMock()
        mock_alarms.delete_alarm.return_value = True
        
        mock_alarms_class.return_value = mock_alarms

        setup = MonitoringSetup()
        result = setup.cleanup_alarms()

        # Check that alarms were deleted
        assert mock_alarms.delete_alarm.call_count > 0

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_setup_dashboards_error_handling(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test error handling in setup_dashboards."""
        mock_dashboards = MagicMock()
        mock_dashboards.create_main_dashboard.side_effect = Exception("Test error")
        
        mock_dashboards_class.return_value = mock_dashboards

        setup = MonitoringSetup()
        result = setup.setup_dashboards()

        assert "error" in result

    @patch("src.observability.setup.CloudWatchDashboards")
    @patch("src.observability.setup.CloudWatchAlarms")
    @patch("src.observability.setup.CloudWatchMetrics")
    def test_setup_alarms_error_handling(self, mock_metrics_class, mock_alarms_class, mock_dashboards_class):
        """Test error handling in setup_alarms."""
        mock_alarms = MagicMock()
        mock_alarms.create_report_generation_sla_alarm.side_effect = Exception("Test error")
        
        mock_alarms_class.return_value = mock_alarms

        setup = MonitoringSetup()
        result = setup.setup_alarms()

        assert "error" in result


class TestSetupMonitoringFunction:
    """Tests for setup_monitoring function."""

    @patch("src.observability.setup.MonitoringSetup")
    def test_setup_monitoring(self, mock_setup_class):
        """Test setup_monitoring function."""
        mock_setup = MagicMock()
        mock_setup.setup_all.return_value = {
            "dashboards": {"main_dashboard": True},
            "alarms": {"standard_report_sla": True},
        }
        
        mock_setup_class.return_value = mock_setup

        result = setup_monitoring()

        assert "dashboards" in result
        assert "alarms" in result
        mock_setup.setup_all.assert_called_once()
