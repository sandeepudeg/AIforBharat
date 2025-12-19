"""
Settings Menu Component
Provides UI for manual difficulty control and adaptive mode toggle
Requirements: 4.1, 4.2, 4.3, 4.4
"""

from typing import Optional, Callable
from game_types import DifficultyLevel
from difficulty_manager import DifficultyManager


class SettingsMenu:
    """Manages settings menu for manual difficulty control"""

    def __init__(self, difficulty_manager: DifficultyManager):
        """Initialize settings menu with difficulty manager"""
        self.difficulty_manager = difficulty_manager
        self.is_open = False
        self.selected_option = 0
        self.on_settings_changed: Optional[Callable] = None

    def open_menu(self) -> None:
        """Open the settings menu"""
        self.is_open = True
        self.selected_option = 0

    def close_menu(self) -> None:
        """Close the settings menu"""
        self.is_open = False

    def toggle_menu(self) -> bool:
        """Toggle menu open/closed state"""
        self.is_open = not self.is_open
        if self.is_open:
            self.selected_option = 0
        return self.is_open

    def is_menu_open(self) -> bool:
        """Check if menu is open"""
        return self.is_open

    def get_menu_display(self) -> str:
        """Get formatted menu display string"""
        lines = []
        lines.append("=" * 40)
        lines.append("SETTINGS MENU")
        lines.append("=" * 40)
        lines.append("")

        current_difficulty = self.difficulty_manager.get_current_difficulty()

        # Adaptive mode option
        adaptive_status = "ON" if current_difficulty.adaptive_mode else "OFF"
        adaptive_marker = ">" if self.selected_option == 0 else " "
        lines.append(f"{adaptive_marker} 1. Adaptive Mode: {adaptive_status}")

        # Speed slider
        speed_marker = ">" if self.selected_option == 1 else " "
        speed_bar = self._get_slider_bar(
            current_difficulty.speed,
            DifficultyManager.SPEED_MIN,
            DifficultyManager.SPEED_MAX
        )
        lines.append(f"{speed_marker} 2. Speed: {speed_bar} ({current_difficulty.speed:.1f})")

        # Obstacle density slider
        obstacle_marker = ">" if self.selected_option == 2 else " "
        obstacle_bar = self._get_slider_bar(
            current_difficulty.obstacle_density,
            DifficultyManager.OBSTACLE_DENSITY_MIN,
            DifficultyManager.OBSTACLE_DENSITY_MAX
        )
        lines.append(
            f"{obstacle_marker} 3. Obstacles: {obstacle_bar} "
            f"({current_difficulty.obstacle_density:.1f})"
        )

        # Food spawn rate slider
        food_marker = ">" if self.selected_option == 3 else " "
        food_bar = self._get_slider_bar(
            current_difficulty.food_spawn_rate,
            DifficultyManager.FOOD_SPAWN_RATE_MIN,
            DifficultyManager.FOOD_SPAWN_RATE_MAX
        )
        lines.append(
            f"{food_marker} 4. Food Spawn Rate: {food_bar} "
            f"({current_difficulty.food_spawn_rate:.2f}x)"
        )

        lines.append("")
        lines.append("Controls:")
        lines.append("  UP/DOWN - Navigate")
        lines.append("  LEFT/RIGHT - Adjust value")
        lines.append("  ENTER - Toggle option")
        lines.append("  ESC - Close menu")
        lines.append("=" * 40)

        return "\n".join(lines)

    def _get_slider_bar(self, value: float, min_val: float, max_val: float) -> str:
        """Generate a visual slider bar"""
        bar_length = 20
        normalized = (value - min_val) / (max_val - min_val)
        filled = int(normalized * bar_length)
        bar = "[" + "=" * filled + "-" * (bar_length - filled) + "]"
        return bar

    def select_next_option(self) -> None:
        """Move selection to next option"""
        self.selected_option = (self.selected_option + 1) % 4

    def select_previous_option(self) -> None:
        """Move selection to previous option"""
        self.selected_option = (self.selected_option - 1) % 4

    def activate_selected_option(self) -> bool:
        """Activate the currently selected option"""
        if self.selected_option == 0:
            # Toggle adaptive mode
            return self._toggle_adaptive_mode()
        return False

    def increase_selected_value(self, amount: float = 0.5) -> bool:
        """Increase the value of the selected slider"""
        if self.selected_option == 0:
            # Can't increase adaptive mode toggle
            return False

        current_difficulty = self.difficulty_manager.get_current_difficulty()

        if self.selected_option == 1:
            # Speed
            new_speed = min(
                current_difficulty.speed + amount,
                DifficultyManager.SPEED_MAX
            )
            return self._apply_speed_change(new_speed)

        elif self.selected_option == 2:
            # Obstacle density
            new_density = min(
                current_difficulty.obstacle_density + amount,
                DifficultyManager.OBSTACLE_DENSITY_MAX
            )
            return self._apply_obstacle_density_change(new_density)

        elif self.selected_option == 3:
            # Food spawn rate
            new_rate = min(
                current_difficulty.food_spawn_rate + amount,
                DifficultyManager.FOOD_SPAWN_RATE_MAX
            )
            return self._apply_food_spawn_rate_change(new_rate)

        return False

    def decrease_selected_value(self, amount: float = 0.5) -> bool:
        """Decrease the value of the selected slider"""
        if self.selected_option == 0:
            # Can't decrease adaptive mode toggle
            return False

        current_difficulty = self.difficulty_manager.get_current_difficulty()

        if self.selected_option == 1:
            # Speed
            new_speed = max(
                current_difficulty.speed - amount,
                DifficultyManager.SPEED_MIN
            )
            return self._apply_speed_change(new_speed)

        elif self.selected_option == 2:
            # Obstacle density
            new_density = max(
                current_difficulty.obstacle_density - amount,
                DifficultyManager.OBSTACLE_DENSITY_MIN
            )
            return self._apply_obstacle_density_change(new_density)

        elif self.selected_option == 3:
            # Food spawn rate
            new_rate = max(
                current_difficulty.food_spawn_rate - amount,
                DifficultyManager.FOOD_SPAWN_RATE_MIN
            )
            return self._apply_food_spawn_rate_change(new_rate)

        return False

    def _toggle_adaptive_mode(self) -> bool:
        """Toggle adaptive mode on/off"""
        current_difficulty = self.difficulty_manager.get_current_difficulty()

        if current_difficulty.adaptive_mode:
            self.difficulty_manager.disable_adaptive_mode()
        else:
            self.difficulty_manager.enable_adaptive_mode()

        self._notify_settings_changed()
        return True

    def _apply_speed_change(self, new_speed: float) -> bool:
        """Apply speed change immediately"""
        current_difficulty = self.difficulty_manager.get_current_difficulty()

        updated_difficulty = DifficultyLevel(
            level=current_difficulty.level,
            speed=new_speed,
            obstacle_density=current_difficulty.obstacle_density,
            food_spawn_rate=current_difficulty.food_spawn_rate,
            adaptive_mode=current_difficulty.adaptive_mode
        )

        result = self.difficulty_manager.set_manual_difficulty(updated_difficulty)
        if result:
            self._notify_settings_changed()
        return result

    def _apply_obstacle_density_change(self, new_density: float) -> bool:
        """Apply obstacle density change immediately"""
        current_difficulty = self.difficulty_manager.get_current_difficulty()

        updated_difficulty = DifficultyLevel(
            level=current_difficulty.level,
            speed=current_difficulty.speed,
            obstacle_density=new_density,
            food_spawn_rate=current_difficulty.food_spawn_rate,
            adaptive_mode=current_difficulty.adaptive_mode
        )

        result = self.difficulty_manager.set_manual_difficulty(updated_difficulty)
        if result:
            self._notify_settings_changed()
        return result

    def _apply_food_spawn_rate_change(self, new_rate: float) -> bool:
        """Apply food spawn rate change immediately"""
        current_difficulty = self.difficulty_manager.get_current_difficulty()

        updated_difficulty = DifficultyLevel(
            level=current_difficulty.level,
            speed=current_difficulty.speed,
            obstacle_density=current_difficulty.obstacle_density,
            food_spawn_rate=new_rate,
            adaptive_mode=current_difficulty.adaptive_mode
        )

        result = self.difficulty_manager.set_manual_difficulty(updated_difficulty)
        if result:
            self._notify_settings_changed()
        return result

    def _notify_settings_changed(self) -> None:
        """Notify that settings have changed"""
        if self.on_settings_changed:
            self.on_settings_changed()

    def set_on_settings_changed_callback(self, callback: Callable) -> None:
        """Set callback for when settings change"""
        self.on_settings_changed = callback

    def get_current_settings(self) -> DifficultyLevel:
        """Get current difficulty settings"""
        return self.difficulty_manager.get_current_difficulty()

    def apply_settings(self, difficulty: DifficultyLevel) -> bool:
        """Apply new settings directly"""
        result = self.difficulty_manager.set_manual_difficulty(difficulty)
        if result:
            self._notify_settings_changed()
        return result
