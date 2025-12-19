"""
Tests for DifficultyManager
Includes unit tests and property-based tests for difficulty management
Requirements: 2.2, 2.3, 2.4, 4.2, 4.3, 6.4
"""

import pytest
import time
from hypothesis import given, strategies as st, settings
from difficulty_manager import DifficultyManager
from game_types import DifficultyLevel, DifficultyDelta


class TestDifficultyManagerInitialization:
    """Tests for difficulty manager initialization"""

    def test_initialize_with_default_difficulty(self):
        """Should initialize with default difficulty"""
        manager = DifficultyManager()
        difficulty = manager.get_current_difficulty()
        assert difficulty.level == 1
        assert difficulty.speed == 5
        assert difficulty.adaptive_mode is True

    def test_initialize_with_custom_difficulty(self):
        """Should initialize with custom difficulty"""
        custom = DifficultyLevel(
            level=5,
            speed=7,
            obstacle_density=2,
            food_spawn_rate=1.5,
            adaptive_mode=False
        )
        manager = DifficultyManager(custom)
        difficulty = manager.get_current_difficulty()
        assert difficulty.level == 5
        assert difficulty.speed == 7


class TestManualDifficultyControl:
    """Tests for manual difficulty control"""

    def test_set_manual_difficulty(self):
        """Should set manual difficulty"""
        manager = DifficultyManager()
        new_difficulty = DifficultyLevel(
            level=7,
            speed=8,
            obstacle_density=3,
            food_spawn_rate=1.8,
            adaptive_mode=False
        )

        result = manager.set_manual_difficulty(new_difficulty)
        assert result is True
        assert manager.get_current_difficulty().level == 7

    def test_reject_invalid_difficulty(self):
        """Should reject invalid difficulty parameters"""
        manager = DifficultyManager()
        invalid_difficulty = DifficultyLevel(
            level=15,  # Out of bounds
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )

        result = manager.set_manual_difficulty(invalid_difficulty)
        assert result is False

    def test_clamp_parameters(self):
        """Should clamp parameters to valid bounds"""
        manager = DifficultyManager()
        out_of_bounds = DifficultyLevel(
            level=15,
            speed=20,
            obstacle_density=10,
            food_spawn_rate=5.0,
            adaptive_mode=True
        )

        clamped = manager.clamp_parameters(out_of_bounds)
        assert clamped.level == 10
        assert clamped.speed == 10
        assert clamped.obstacle_density == 5
        assert clamped.food_spawn_rate == 2.0


class TestAdaptiveModeToggle:
    """Tests for adaptive mode toggle"""

    def test_enable_adaptive_mode(self):
        """Should enable adaptive mode"""
        manager = DifficultyManager()
        manager.disable_adaptive_mode()
        assert manager.is_adaptive_mode_enabled() is False

        manager.enable_adaptive_mode()
        assert manager.is_adaptive_mode_enabled() is True

    def test_disable_adaptive_mode(self):
        """Should disable adaptive mode"""
        manager = DifficultyManager()
        assert manager.is_adaptive_mode_enabled() is True

        manager.disable_adaptive_mode()
        assert manager.is_adaptive_mode_enabled() is False

    def test_adaptive_mode_persists_through_adjustments(self):
        """Should preserve adaptive mode setting through adjustments"""
        manager = DifficultyManager()
        manager.disable_adaptive_mode()

        delta = DifficultyDelta(
            speed_delta=1,
            obstacle_density_delta=0.5,
            food_spawn_rate_delta=0.1,
            reason="Test"
        )
        manager.apply_difficulty_adjustment(delta)

        assert manager.is_adaptive_mode_enabled() is False


class TestDifficultyAdjustment:
    """Tests for difficulty adjustment"""

    def test_apply_difficulty_adjustment(self):
        """Should apply difficulty adjustment"""
        manager = DifficultyManager()
        initial_speed = manager.get_current_difficulty().speed

        delta = DifficultyDelta(
            speed_delta=1,
            obstacle_density_delta=0.5,
            food_spawn_rate_delta=0.1,
            reason="Test"
        )

        result = manager.apply_difficulty_adjustment(delta)
        assert result is True

        # Wait for transition to complete
        time.sleep(2.6)

        final_difficulty = manager.get_current_difficulty()
        assert final_difficulty.speed == initial_speed + 1

    def test_reject_adjustment_exceeding_bounds(self):
        """Should reject adjustment that exceeds bounds"""
        manager = DifficultyManager()

        # Try to increase speed beyond maximum
        delta = DifficultyDelta(
            speed_delta=10,
            obstacle_density_delta=0,
            food_spawn_rate_delta=0,
            reason="Test"
        )

        result = manager.apply_difficulty_adjustment(delta)
        assert result is False

    def test_adjustment_clamps_to_bounds(self):
        """Should clamp adjustment to valid bounds"""
        manager = DifficultyManager()

        # Apply adjustment that would exceed bounds
        delta = DifficultyDelta(
            speed_delta=5,
            obstacle_density_delta=0,
            food_spawn_rate_delta=0,
            reason="Test"
        )

        # This should succeed but clamp the value
        result = manager.apply_difficulty_adjustment(delta)
        assert result is True
        
        # Wait for transition
        time.sleep(2.6)
        
        # Speed should be clamped to maximum
        difficulty = manager.get_current_difficulty()
        assert difficulty.speed == 10


class TestSmoothTransition:
    """Tests for smooth difficulty transitions"""

    def test_transition_in_progress(self):
        """Should indicate transition in progress"""
        manager = DifficultyManager()

        delta = DifficultyDelta(
            speed_delta=2,
            obstacle_density_delta=1,
            food_spawn_rate_delta=0.2,
            reason="Test"
        )

        manager.apply_difficulty_adjustment(delta)
        assert manager.transition_in_progress is True

    def test_transition_completes(self):
        """Should complete transition after duration"""
        manager = DifficultyManager()

        delta = DifficultyDelta(
            speed_delta=1,
            obstacle_density_delta=0.5,
            food_spawn_rate_delta=0.1,
            reason="Test"
        )

        manager.apply_difficulty_adjustment(delta)
        assert manager.transition_in_progress is True

        # Wait for transition to complete
        time.sleep(2.6)

        manager.get_current_difficulty()
        assert manager.transition_in_progress is False

    def test_smooth_parameter_interpolation(self):
        """Should interpolate parameters smoothly"""
        manager = DifficultyManager()
        initial_speed = manager.get_current_difficulty().speed

        delta = DifficultyDelta(
            speed_delta=2,
            obstacle_density_delta=0,
            food_spawn_rate_delta=0,
            reason="Test"
        )

        manager.apply_difficulty_adjustment(delta)

        # Check intermediate value
        time.sleep(1.0)
        intermediate = manager.get_current_difficulty().speed

        # Should be between initial and target
        assert initial_speed < intermediate < initial_speed + 2


class TestParameterValidation:
    """Tests for parameter validation"""

    def test_validate_valid_parameters(self):
        """Should validate correct parameters"""
        manager = DifficultyManager()
        valid = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        assert manager.validate_parameters(valid) is True

    def test_validate_boundary_values(self):
        """Should validate boundary values"""
        manager = DifficultyManager()

        # Minimum values
        min_difficulty = DifficultyLevel(
            level=1,
            speed=1,
            obstacle_density=0,
            food_spawn_rate=0.5,
            adaptive_mode=True
        )
        assert manager.validate_parameters(min_difficulty) is True

        # Maximum values
        max_difficulty = DifficultyLevel(
            level=10,
            speed=10,
            obstacle_density=5,
            food_spawn_rate=2.0,
            adaptive_mode=True
        )
        assert manager.validate_parameters(max_difficulty) is True

    def test_validate_out_of_bounds_level(self):
        """Should reject out of bounds level"""
        manager = DifficultyManager()
        invalid = DifficultyLevel(
            level=15,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        assert manager.validate_parameters(invalid) is False

    def test_validate_out_of_bounds_speed(self):
        """Should reject out of bounds speed"""
        manager = DifficultyManager()
        invalid = DifficultyLevel(
            level=5,
            speed=15,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        assert manager.validate_parameters(invalid) is False

    def test_validate_out_of_bounds_obstacle_density(self):
        """Should reject out of bounds obstacle density"""
        manager = DifficultyManager()
        invalid = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=10,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        assert manager.validate_parameters(invalid) is False

    def test_validate_out_of_bounds_food_spawn_rate(self):
        """Should reject out of bounds food spawn rate"""
        manager = DifficultyManager()
        invalid = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=5.0,
            adaptive_mode=True
        )

        assert manager.validate_parameters(invalid) is False


class TestDifficultyLevelCalculation:
    """Tests for difficulty level calculation"""

    def test_calculate_difficulty_level_minimum(self):
        """Should calculate minimum difficulty level"""
        manager = DifficultyManager()
        level = manager._calculate_difficulty_level(1, 0, 0.5)
        assert level == 1

    def test_calculate_difficulty_level_maximum(self):
        """Should calculate maximum difficulty level"""
        manager = DifficultyManager()
        level = manager._calculate_difficulty_level(10, 5, 2.0)
        assert level == 10

    def test_calculate_difficulty_level_middle(self):
        """Should calculate middle difficulty level"""
        manager = DifficultyManager()
        level = manager._calculate_difficulty_level(5, 2, 1.0)
        assert 4 <= level <= 6


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestDifficultyManagerProperties:
    """Property-based tests for difficulty manager correctness"""

    def test_property_5_difficulty_bounds_enforcement(self):
        """
        Property 5: Difficulty Bounds Enforcement
        For any difficulty adjustment, all resulting parameters should remain
        within defined bounds: speed [1-10], obstacle density [0-5], food spawn rate [0.5-2.0].
        
        **Feature: snake-adaptive-ai, Property 5: Difficulty Bounds Enforcement**
        **Validates: Requirements 6.4**
        """
        manager = DifficultyManager()

        # Test various adjustments
        adjustments = [
            DifficultyDelta(1, 1, 0.2, "Increase"),
            DifficultyDelta(-1, -1, -0.2, "Decrease"),
            DifficultyDelta(0.5, 0.5, 0.1, "Slight increase"),
        ]

        for delta in adjustments:
            manager.apply_difficulty_adjustment(delta)
            difficulty = manager.get_current_difficulty()

            # Verify all parameters are in bounds
            assert 1 <= difficulty.speed <= 10
            assert 0 <= difficulty.obstacle_density <= 5
            assert 0.5 <= difficulty.food_spawn_rate <= 2.0

    def test_property_10_difficulty_parameter_smoothness(self):
        """
        Property 10: Difficulty Parameter Smoothness
        For any difficulty adjustment, the transition from old to new parameters
        should occur over 2-3 seconds without abrupt jumps in speed or obstacle density.
        
        **Feature: snake-adaptive-ai, Property 10: Difficulty Parameter Smoothness**
        **Validates: Requirements 2.4**
        """
        manager = DifficultyManager()
        initial_speed = manager.get_current_difficulty().speed

        delta = DifficultyDelta(
            speed_delta=2,
            obstacle_density_delta=1,
            food_spawn_rate_delta=0.2,
            reason="Test"
        )

        manager.apply_difficulty_adjustment(delta)

        # Sample parameters at different times
        samples = []
        for i in range(5):
            time.sleep(0.5)
            difficulty = manager.get_current_difficulty()
            samples.append(difficulty.speed)

        # Verify smooth progression (no abrupt jumps)
        for i in range(1, len(samples)):
            # Each step should be relatively small (allow up to 1.0 per 0.5 seconds)
            jump = abs(samples[i] - samples[i - 1])
            assert jump < 1.0  # Max jump of 1.0 per 0.5 seconds
