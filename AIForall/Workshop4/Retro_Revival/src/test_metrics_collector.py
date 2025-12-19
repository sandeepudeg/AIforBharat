"""
Tests for MetricsCollector
Requirements: 2.1, 6.3
"""

import pytest
import time
from metrics_collector import MetricsCollector
from game_types import PerformanceMetrics


class TestMetricsCollectorInitialization:
    """Tests for metrics collector initialization"""

    def test_initialize_collector(self):
        """Should initialize metrics collector"""
        collector = MetricsCollector()
        assert collector.session_start_time is None
        assert collector.reaction_times == []
        assert collector.food_consumed == 0
        assert collector.collisions_avoided == 0


class TestSessionManagement:
    """Tests for session management"""

    def test_start_session(self):
        """Should start a new session"""
        collector = MetricsCollector()
        collector.start_session()
        assert collector.session_start_time is not None
        assert collector.food_consumed == 0
        assert collector.reaction_times == []

    def test_reset_on_new_session(self):
        """Should reset metrics on new session"""
        collector = MetricsCollector()
        collector.start_session()
        collector.food_consumed = 5
        collector.reaction_times = [100, 150]
        
        collector.start_session()
        assert collector.food_consumed == 0
        assert collector.reaction_times == []


class TestReactionTimeTracking:
    """Tests for reaction time tracking"""

    def test_record_input(self):
        """Should record input"""
        collector = MetricsCollector()
        collector.start_session()
        collector.record_input()
        assert collector.last_input_time is not None

    def test_calculate_reaction_time(self):
        """Should calculate reaction time between inputs"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_input()
        time.sleep(0.1)  # Sleep 100ms
        collector.record_input()
        
        assert len(collector.reaction_times) > 0
        # Reaction time should be approximately 100ms (allow some variance)
        assert 80 <= collector.reaction_times[0] <= 150

    def test_average_reaction_time(self):
        """Should calculate average reaction time"""
        collector = MetricsCollector()
        collector.reaction_times = [100, 150, 200]
        
        avg = collector.get_average_reaction_time()
        assert avg == 150.0

    def test_average_reaction_time_empty(self):
        """Should return 0 for empty reaction times"""
        collector = MetricsCollector()
        assert collector.get_average_reaction_time() == 0.0


class TestFoodConsumption:
    """Tests for food consumption tracking"""

    def test_record_food_consumption(self):
        """Should record food consumption"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_food_consumption()
        assert collector.food_consumed == 1
        
        collector.record_food_consumption()
        assert collector.food_consumed == 2

    def test_food_consumption_rate(self):
        """Should calculate food consumption rate"""
        collector = MetricsCollector()
        collector.start_session()
        
        # Record 6 food items
        for _ in range(6):
            collector.record_food_consumption()
        
        # Wait a bit to accumulate time
        time.sleep(0.1)
        
        rate = collector.get_food_consumption_rate()
        # Rate should be positive (items per minute)
        assert rate > 0


class TestCollisionAvoidance:
    """Tests for collision avoidance tracking"""

    def test_record_collision_avoided(self):
        """Should record collision avoidance"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_collision_avoided()
        assert collector.collisions_avoided == 1
        
        collector.record_collision_avoided()
        assert collector.collisions_avoided == 2


class TestMovementTracking:
    """Tests for movement tracking"""

    def test_record_movement(self):
        """Should record movement"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_movement()
        assert collector.move_count == 1
        assert collector.total_distance == 1

    def test_record_movement_with_distance(self):
        """Should record movement with custom distance"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_movement(5)
        assert collector.move_count == 1
        assert collector.total_distance == 5

    def test_average_speed(self):
        """Should calculate average speed"""
        collector = MetricsCollector()
        collector.start_session()
        
        # Record 10 moves
        for _ in range(10):
            collector.record_movement()
        
        time.sleep(0.1)
        
        speed = collector.get_average_speed()
        # Speed should be positive (moves per second)
        assert speed > 0


class TestSurvivalTime:
    """Tests for survival time tracking"""

    def test_survival_time_zero_initially(self):
        """Should return 0 survival time before session starts"""
        collector = MetricsCollector()
        assert collector.get_survival_time() == 0.0

    def test_survival_time_increases(self):
        """Should increase survival time"""
        collector = MetricsCollector()
        collector.start_session()
        
        time.sleep(0.1)
        
        survival_time = collector.get_survival_time()
        # Should be approximately 100ms
        assert 0.08 <= survival_time <= 0.2


class TestMetricsRetrieval:
    """Tests for metrics retrieval"""

    def test_get_metrics(self):
        """Should return performance metrics"""
        collector = MetricsCollector()
        collector.start_session()
        
        collector.record_food_consumption()
        collector.record_movement()
        
        metrics = collector.get_metrics()
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.food_consumed == 1
        assert metrics.survival_time >= 0

    def test_metrics_contain_all_fields(self):
        """Should include all required fields in metrics"""
        collector = MetricsCollector()
        collector.start_session()
        
        metrics = collector.get_metrics()
        assert hasattr(metrics, 'survival_time')
        assert hasattr(metrics, 'food_consumed')
        assert hasattr(metrics, 'reaction_time')
        assert hasattr(metrics, 'collisions_avoided')
        assert hasattr(metrics, 'average_speed')
        assert hasattr(metrics, 'timestamp')


class TestMetricsValidation:
    """Tests for metrics validation"""

    def test_validate_valid_metrics(self):
        """Should validate correct metrics"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100, 150, 120],
            collisions_avoided=2,
            average_speed=5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is True

    def test_validate_negative_survival_time(self):
        """Should reject negative survival time"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=-10.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is False

    def test_validate_negative_food_consumed(self):
        """Should reject negative food consumed"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=-5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is False

    def test_validate_negative_reaction_time(self):
        """Should reject negative reaction time"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100, -50],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is False

    def test_validate_negative_collisions_avoided(self):
        """Should reject negative collisions avoided"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=-2,
            average_speed=5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is False

    def test_validate_negative_average_speed(self):
        """Should reject negative average speed"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=-5.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is False

    def test_validate_zero_metrics(self):
        """Should accept zero metrics"""
        collector = MetricsCollector()
        metrics = PerformanceMetrics(
            survival_time=0.0,
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0.0,
            timestamp=int(time.time() * 1000)
        )
        
        assert collector.validate_metrics(metrics) is True
