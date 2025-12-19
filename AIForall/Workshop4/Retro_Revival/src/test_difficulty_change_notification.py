"""
Unit tests for DifficultyChangeNotificationSystem
Tests notification creation, display, and management for difficulty changes
Requirements: 3.2
"""

import pytest
from difficulty_change_notification import (
    DifficultyChangeNotificationSystem,
    DifficultyChangeNotification
)
from game_types import DifficultyLevel


class TestDifficultyChangeNotificationSystem:
    """Test suite for difficulty change notification system"""

    @pytest.fixture
    def notification_system(self):
        """Create a notification system instance"""
        return DifficultyChangeNotificationSystem()

    @pytest.fixture
    def base_difficulty(self):
        """Create base difficulty level"""
        return DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

    # Initialization Tests
    def test_initialization(self, notification_system):
        """Test notification system initializes empty"""
        assert notification_system.get_active_notification() is None
        assert notification_system.get_notification_count() == 0
        assert not notification_system.is_notification_active()

    # Speed Change Detection Tests
    def test_detect_speed_increase(self, notification_system, base_difficulty):
        """Test detecting speed increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'speed'
        assert changes[0].old_value == 5
        assert changes[0].new_value == 7

    def test_detect_speed_decrease(self, notification_system, base_difficulty):
        """Test detecting speed decrease"""
        new_difficulty = DifficultyLevel(
            level=5, speed=3, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'speed'
        assert changes[0].old_value == 5
        assert changes[0].new_value == 3

    # Obstacle Density Change Detection Tests
    def test_detect_obstacle_increase(self, notification_system, base_difficulty):
        """Test detecting obstacle density increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=4, food_spawn_rate=1.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'obstacle_density'
        assert changes[0].old_value == 2
        assert changes[0].new_value == 4

    def test_detect_obstacle_decrease(self, notification_system, base_difficulty):
        """Test detecting obstacle density decrease"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'obstacle_density'
        assert changes[0].old_value == 2
        assert changes[0].new_value == 1

    # Food Spawn Rate Change Detection Tests
    def test_detect_spawn_rate_increase(self, notification_system, base_difficulty):
        """Test detecting food spawn rate increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.5, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'food_spawn_rate'
        assert changes[0].old_value == 1.0
        assert changes[0].new_value == 1.5

    def test_detect_spawn_rate_decrease(self, notification_system, base_difficulty):
        """Test detecting food spawn rate decrease"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=0.7, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].parameter == 'food_spawn_rate'
        assert changes[0].old_value == 1.0
        assert changes[0].new_value == 0.7

    # Level Change Detection Tests
    def test_detect_level_increase(self, notification_system, base_difficulty):
        """Test detecting overall level increase"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        # Should detect level change plus individual parameter changes
        level_changes = [c for c in changes if c.parameter == 'level']
        assert len(level_changes) == 1
        assert level_changes[0].old_value == 5
        assert level_changes[0].new_value == 7

    def test_detect_level_decrease(self, notification_system, base_difficulty):
        """Test detecting overall level decrease"""
        new_difficulty = DifficultyLevel(
            level=3, speed=3, obstacle_density=1, food_spawn_rate=0.8, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        level_changes = [c for c in changes if c.parameter == 'level']
        assert len(level_changes) == 1
        assert level_changes[0].old_value == 5
        assert level_changes[0].new_value == 3

    # Multiple Parameter Change Tests
    def test_detect_multiple_parameter_changes(self, notification_system, base_difficulty):
        """Test detecting multiple parameter changes at once"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        # Should detect all 4 changes
        assert len(changes) == 4
        parameters = {c.parameter for c in changes}
        assert parameters == {'speed', 'obstacle_density', 'food_spawn_rate', 'level'}

    def test_detect_no_changes(self, notification_system, base_difficulty):
        """Test detecting no changes when difficulty is identical"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(base_difficulty, new_difficulty)

        assert len(changes) == 0

    # Notification Display Tests
    def test_notification_display_speed_increase(self, notification_system, base_difficulty):
        """Test notification display for speed increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        display = notification_system.get_notification_display()
        assert "Speed" in display
        assert "5" in display
        assert "7" in display
        assert "playing well" in display.lower()

    def test_notification_display_speed_decrease(self, notification_system, base_difficulty):
        """Test notification display for speed decrease"""
        new_difficulty = DifficultyLevel(
            level=5, speed=3, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        display = notification_system.get_notification_display()
        assert "Speed" in display
        assert "5" in display
        assert "3" in display
        assert "slow" in display.lower()

    def test_notification_display_obstacle_increase(self, notification_system, base_difficulty):
        """Test notification display for obstacle increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=4, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        display = notification_system.get_notification_display()
        assert "Obstacles" in display
        assert "2" in display
        assert "4" in display
        assert "challenge" in display.lower()

    def test_notification_display_spawn_rate_increase(self, notification_system, base_difficulty):
        """Test notification display for spawn rate increase"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        display = notification_system.get_notification_display()
        assert "Food Rate" in display
        assert "1.0" in display
        assert "1.5" in display

    # Active Notification Tests
    def test_active_notification_set_on_detect(self, notification_system, base_difficulty):
        """Test that active notification is set when changes are detected"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        assert notification_system.is_notification_active()
        assert notification_system.get_active_notification() is not None

    def test_active_notification_not_set_on_no_changes(self, notification_system, base_difficulty):
        """Test that active notification is not set when no changes"""
        new_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        assert not notification_system.is_notification_active()

    # Notification Queue Tests
    def test_notification_queue_multiple_changes(self, notification_system, base_difficulty):
        """Test notification queue with multiple changes"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        assert notification_system.get_notification_count() == 4

    def test_advance_notification(self, notification_system, base_difficulty):
        """Test advancing to next notification"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        first_notif = notification_system.get_active_notification()
        assert first_notif is not None

        # Advance past first notification
        current_time = first_notif.timestamp + 4.0  # 4 seconds later
        has_more = notification_system.advance_notification(current_time)

        assert has_more
        second_notif = notification_system.get_active_notification()
        assert second_notif != first_notif

    def test_advance_notification_to_end(self, notification_system, base_difficulty):
        """Test advancing through all notifications"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        first_notif = notification_system.get_active_notification()
        current_time = first_notif.timestamp

        # Advance through all notifications
        for _ in range(5):  # More than the 4 changes
            current_time += 4.0
            has_more = notification_system.advance_notification(current_time)
            if not has_more:
                break

        assert not notification_system.is_notification_active()

    # Custom Reason Tests
    def test_detect_changes_with_custom_reason(self, notification_system, base_difficulty):
        """Test detecting changes with custom reason"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        custom_reason = "You're on fire!"
        changes = notification_system.detect_changes(base_difficulty, new_difficulty, custom_reason)

        assert len(changes) == 1
        assert changes[0].reason == custom_reason

    # Clear Notifications Tests
    def test_clear_notifications(self, notification_system, base_difficulty):
        """Test clearing all notifications"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        assert notification_system.get_notification_count() > 0
        notification_system.clear_notifications()

        assert notification_system.get_notification_count() == 0
        assert not notification_system.is_notification_active()

    # Get All Notifications Tests
    def test_get_all_notifications(self, notification_system, base_difficulty):
        """Test getting all notifications"""
        new_difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        all_notifs = notification_system.get_all_notifications()
        assert len(all_notifs) == 4

    # Edge Cases Tests
    def test_notification_with_zero_values(self, notification_system):
        """Test notification with zero values"""
        old_difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        new_difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=1, food_spawn_rate=0.5, adaptive_mode=True
        )
        changes = notification_system.detect_changes(old_difficulty, new_difficulty)

        assert len(changes) == 1
        assert changes[0].old_value == 0
        assert changes[0].new_value == 1

    def test_notification_with_max_values(self, notification_system):
        """Test notification with maximum values"""
        old_difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        new_difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        changes = notification_system.detect_changes(old_difficulty, new_difficulty)

        assert len(changes) == 0

    def test_sequential_notifications(self, notification_system, base_difficulty):
        """Test sequential difficulty changes"""
        # First change
        difficulty1 = DifficultyLevel(
            level=6, speed=6, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, difficulty1)
        count1 = notification_system.get_notification_count()

        # Second change
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        notification_system.detect_changes(difficulty1, difficulty2)
        count2 = notification_system.get_notification_count()

        assert count2 > count1

    # Notification Duration Tests
    def test_notification_duration(self, notification_system, base_difficulty):
        """Test notification has correct duration"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        notif = notification_system.get_active_notification()
        assert notif.duration_ms == 3000  # 3 seconds

    # Parameter Name Formatting Tests
    def test_parameter_name_formatting(self, notification_system, base_difficulty):
        """Test parameter names are formatted correctly in display"""
        new_difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        notification_system.detect_changes(base_difficulty, new_difficulty)

        display = notification_system.get_notification_display()
        # Should contain formatted parameter name, not raw parameter
        assert "Speed" in display or "Obstacles" in display or "Food Rate" in display or "Level" in display
