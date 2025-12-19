"""
Tests for Settings Menu
Includes unit tests for manual difficulty adjustment and adaptive mode toggle
Requirements: 4.1, 4.2, 4.3, 4.4
"""

import pytest
from settings_menu import SettingsMenu
from difficulty_manager import DifficultyManager
from game_types import DifficultyLevel


class TestSettingsMenuInitialization:
    """Tests for settings menu initialization"""

    def test_initialize_settings_menu(self):
        """Should initialize settings menu"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        assert menu.is_menu_open() is False
        assert menu.selected_option == 0

    def test_menu_starts_closed(self):
        """Menu should start in closed state"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        assert menu.is_menu_open() is False


class TestMenuOpenClose:
    """Tests for menu open/close functionality"""

    def test_open_menu(self):
        """Should open menu"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.open_menu()
        assert menu.is_menu_open() is True

    def test_close_menu(self):
        """Should close menu"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.open_menu()
        menu.close_menu()
        assert menu.is_menu_open() is False

    def test_toggle_menu(self):
        """Should toggle menu state"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        assert menu.is_menu_open() is False
        menu.toggle_menu()
        assert menu.is_menu_open() is True
        menu.toggle_menu()
        assert menu.is_menu_open() is False

    def test_toggle_menu_returns_state(self):
        """Toggle should return new state"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        result = menu.toggle_menu()
        assert result is True
        result = menu.toggle_menu()
        assert result is False


class TestMenuNavigation:
    """Tests for menu navigation"""

    def test_select_next_option(self):
        """Should move to next option"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        assert menu.selected_option == 0
        menu.select_next_option()
        assert menu.selected_option == 1
        menu.select_next_option()
        assert menu.selected_option == 2

    def test_select_previous_option(self):
        """Should move to previous option"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        menu.select_previous_option()
        assert menu.selected_option == 1
        menu.select_previous_option()
        assert menu.selected_option == 0

    def test_navigation_wraps_around(self):
        """Navigation should wrap around"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        menu.select_next_option()
        assert menu.selected_option == 0

        menu.selected_option = 0
        menu.select_previous_option()
        assert menu.selected_option == 3


class TestAdaptiveModeToggle:
    """Tests for adaptive mode toggle"""

    def test_toggle_adaptive_mode_on(self):
        """Should toggle adaptive mode on"""
        manager = DifficultyManager()
        manager.disable_adaptive_mode()
        menu = SettingsMenu(manager)

        menu.selected_option = 0
        result = menu.activate_selected_option()

        assert result is True
        assert manager.is_adaptive_mode_enabled() is True

    def test_toggle_adaptive_mode_off(self):
        """Should toggle adaptive mode off"""
        manager = DifficultyManager()
        manager.enable_adaptive_mode()
        menu = SettingsMenu(manager)

        menu.selected_option = 0
        result = menu.activate_selected_option()

        assert result is True
        assert manager.is_adaptive_mode_enabled() is False

    def test_adaptive_mode_toggle_calls_callback(self):
        """Should call callback when adaptive mode is toggled"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_called = False

        def on_change():
            nonlocal callback_called
            callback_called = True

        menu.set_on_settings_changed_callback(on_change)
        menu.selected_option = 0
        menu.activate_selected_option()

        assert callback_called is True

    def test_adaptive_mode_toggle_immediate_application(self):
        """Should apply adaptive mode toggle immediately"""
        manager = DifficultyManager()
        manager.enable_adaptive_mode()
        menu = SettingsMenu(manager)

        assert manager.is_adaptive_mode_enabled() is True

        menu.selected_option = 0
        menu.activate_selected_option()

        # Should be immediately disabled
        assert manager.is_adaptive_mode_enabled() is False


class TestSpeedAdjustment:
    """Tests for speed adjustment"""

    def test_increase_speed(self):
        """Should increase speed"""
        manager = DifficultyManager()
        initial_speed = manager.get_current_difficulty().speed
        menu = SettingsMenu(manager)

        menu.selected_option = 1
        result = menu.increase_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().speed == initial_speed + 1.0

    def test_decrease_speed(self):
        """Should decrease speed"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 1
        result = menu.decrease_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().speed == 6.0

    def test_speed_clamped_to_maximum(self):
        """Should clamp speed to maximum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=10, speed=9, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 1
        result = menu.increase_selected_value(5.0)

        assert result is True
        assert manager.get_current_difficulty().speed == 10

    def test_speed_clamped_to_minimum(self):
        """Should clamp speed to minimum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=1, speed=2, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 1
        result = menu.decrease_selected_value(5.0)

        assert result is True
        assert manager.get_current_difficulty().speed == 1

    def test_speed_adjustment_immediate_application(self):
        """Should apply speed adjustment immediately"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.selected_option = 1
        menu.increase_selected_value(1.0)

        # Should be immediately applied
        assert manager.get_current_difficulty().speed > 5


class TestObstacleDensityAdjustment:
    """Tests for obstacle density adjustment"""

    def test_increase_obstacle_density(self):
        """Should increase obstacle density"""
        manager = DifficultyManager()
        initial_density = manager.get_current_difficulty().obstacle_density
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        result = menu.increase_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().obstacle_density == initial_density + 1.0

    def test_decrease_obstacle_density(self):
        """Should decrease obstacle density"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=5, speed=5, obstacle_density=3, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        result = menu.decrease_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().obstacle_density == 2.0

    def test_obstacle_density_clamped_to_maximum(self):
        """Should clamp obstacle density to maximum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=10, speed=5, obstacle_density=4, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        result = menu.increase_selected_value(5.0)

        assert result is True
        assert manager.get_current_difficulty().obstacle_density == 5

    def test_obstacle_density_clamped_to_minimum(self):
        """Should clamp obstacle density to minimum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        result = menu.decrease_selected_value(5.0)

        assert result is True
        assert manager.get_current_difficulty().obstacle_density == 0

    def test_obstacle_density_adjustment_immediate_application(self):
        """Should apply obstacle density adjustment immediately"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.selected_option = 2
        menu.increase_selected_value(1.0)

        # Should be immediately applied
        assert manager.get_current_difficulty().obstacle_density > 1


class TestFoodSpawnRateAdjustment:
    """Tests for food spawn rate adjustment"""

    def test_increase_food_spawn_rate(self):
        """Should increase food spawn rate"""
        manager = DifficultyManager()
        initial_rate = manager.get_current_difficulty().food_spawn_rate
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        result = menu.increase_selected_value(0.2)

        assert result is True
        assert manager.get_current_difficulty().food_spawn_rate == initial_rate + 0.2

    def test_decrease_food_spawn_rate(self):
        """Should decrease food spawn rate"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.5, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        result = menu.decrease_selected_value(0.2)

        assert result is True
        assert manager.get_current_difficulty().food_spawn_rate == 1.3

    def test_food_spawn_rate_clamped_to_maximum(self):
        """Should clamp food spawn rate to maximum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=10, speed=5, obstacle_density=2, food_spawn_rate=1.9, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        result = menu.increase_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().food_spawn_rate == 2.0

    def test_food_spawn_rate_clamped_to_minimum(self):
        """Should clamp food spawn rate to minimum"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=1, speed=5, obstacle_density=2, food_spawn_rate=0.6, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        result = menu.decrease_selected_value(1.0)

        assert result is True
        assert manager.get_current_difficulty().food_spawn_rate == 0.5

    def test_food_spawn_rate_adjustment_immediate_application(self):
        """Should apply food spawn rate adjustment immediately"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        menu.selected_option = 3
        menu.increase_selected_value(0.2)

        # Should be immediately applied
        assert manager.get_current_difficulty().food_spawn_rate > 1.0


class TestSettingsMenuDisplay:
    """Tests for menu display"""

    def test_get_menu_display(self):
        """Should generate menu display"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        display = menu.get_menu_display()

        assert "SETTINGS MENU" in display
        assert "Adaptive Mode" in display
        assert "Speed" in display
        assert "Obstacles" in display
        assert "Food Spawn Rate" in display

    def test_menu_display_shows_current_values(self):
        """Menu display should show current values"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=7, speed=8, obstacle_density=3, food_spawn_rate=1.5, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        display = menu.get_menu_display()

        assert "8.0" in display or "8" in display
        assert "3.0" in display or "3" in display
        assert "1.5" in display or "1.50" in display

    def test_menu_display_shows_adaptive_mode_status(self):
        """Menu display should show adaptive mode status"""
        manager = DifficultyManager()
        manager.enable_adaptive_mode()
        menu = SettingsMenu(manager)

        display = menu.get_menu_display()
        assert "ON" in display

        manager.disable_adaptive_mode()
        display = menu.get_menu_display()
        assert "OFF" in display


class TestSettingsMenuCallbacks:
    """Tests for settings menu callbacks"""

    def test_set_callback(self):
        """Should set callback"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_called = False

        def on_change():
            nonlocal callback_called
            callback_called = True

        menu.set_on_settings_changed_callback(on_change)
        menu.selected_option = 1
        menu.increase_selected_value(1.0)

        assert callback_called is True

    def test_callback_called_on_speed_change(self):
        """Callback should be called on speed change"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_count = 0

        def on_change():
            nonlocal callback_count
            callback_count += 1

        menu.set_on_settings_changed_callback(on_change)
        menu.selected_option = 1
        menu.increase_selected_value(1.0)

        assert callback_count == 1

    def test_callback_called_on_obstacle_change(self):
        """Callback should be called on obstacle density change"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_count = 0

        def on_change():
            nonlocal callback_count
            callback_count += 1

        menu.set_on_settings_changed_callback(on_change)
        menu.selected_option = 2
        menu.increase_selected_value(1.0)

        assert callback_count == 1

    def test_callback_called_on_food_rate_change(self):
        """Callback should be called on food spawn rate change"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_count = 0

        def on_change():
            nonlocal callback_count
            callback_count += 1

        menu.set_on_settings_changed_callback(on_change)
        menu.selected_option = 3
        menu.increase_selected_value(0.2)

        assert callback_count == 1


class TestSettingsMenuGettersSetters:
    """Tests for getters and setters"""

    def test_get_current_settings(self):
        """Should get current settings"""
        manager = DifficultyManager()
        manager.set_manual_difficulty(DifficultyLevel(
            level=7, speed=8, obstacle_density=3, food_spawn_rate=1.5, adaptive_mode=False
        ))
        menu = SettingsMenu(manager)

        settings = menu.get_current_settings()

        assert settings.level == 7
        assert settings.speed == 8
        assert settings.obstacle_density == 3
        assert settings.food_spawn_rate == 1.5
        assert settings.adaptive_mode is False

    def test_apply_settings(self):
        """Should apply settings"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        new_settings = DifficultyLevel(
            level=9, speed=9, obstacle_density=4, food_spawn_rate=1.8, adaptive_mode=True
        )

        result = menu.apply_settings(new_settings)

        assert result is True
        current = menu.get_current_settings()
        assert current.speed == 9
        assert current.obstacle_density == 4

    def test_apply_settings_calls_callback(self):
        """Should call callback when applying settings"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        callback_called = False

        def on_change():
            nonlocal callback_called
            callback_called = True

        menu.set_on_settings_changed_callback(on_change)

        new_settings = DifficultyLevel(
            level=9, speed=9, obstacle_density=4, food_spawn_rate=1.8, adaptive_mode=True
        )

        menu.apply_settings(new_settings)

        assert callback_called is True


class TestSettingsMenuIntegration:
    """Integration tests for settings menu"""

    def test_manual_difficulty_adjustment_workflow(self):
        """Should support complete manual difficulty adjustment workflow"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        # Open menu
        menu.open_menu()
        assert menu.is_menu_open() is True

        # Navigate to speed option
        menu.selected_option = 1
        assert menu.selected_option == 1

        # Increase speed
        menu.increase_selected_value(2.0)
        assert manager.get_current_difficulty().speed == 7

        # Navigate to obstacle option
        menu.select_next_option()
        assert menu.selected_option == 2

        # Increase obstacles
        menu.increase_selected_value(1.0)
        assert manager.get_current_difficulty().obstacle_density == 2

        # Close menu
        menu.close_menu()
        assert menu.is_menu_open() is False

    def test_adaptive_mode_toggle_workflow(self):
        """Should support adaptive mode toggle workflow"""
        manager = DifficultyManager()
        manager.enable_adaptive_mode()
        menu = SettingsMenu(manager)

        # Open menu
        menu.open_menu()

        # Toggle adaptive mode
        menu.selected_option = 0
        menu.activate_selected_option()
        assert manager.is_adaptive_mode_enabled() is False

        # Toggle back on
        menu.activate_selected_option()
        assert manager.is_adaptive_mode_enabled() is True

        # Close menu
        menu.close_menu()

    def test_multiple_adjustments_in_sequence(self):
        """Should handle multiple adjustments in sequence"""
        manager = DifficultyManager()
        menu = SettingsMenu(manager)

        # Adjust speed
        menu.selected_option = 1
        menu.increase_selected_value(1.0)
        speed_after_first = manager.get_current_difficulty().speed

        # Adjust obstacles
        menu.selected_option = 2
        menu.increase_selected_value(1.0)
        obstacles_after_second = manager.get_current_difficulty().obstacle_density

        # Adjust food rate
        menu.selected_option = 3
        menu.increase_selected_value(0.2)
        rate_after_third = manager.get_current_difficulty().food_spawn_rate

        # Verify all changes were applied
        assert speed_after_first > 5
        assert obstacles_after_second > 1
        assert rate_after_third > 1.0
