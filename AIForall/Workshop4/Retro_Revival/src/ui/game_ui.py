"""
Game UI Integration Component
Combines game board rendering with difficulty indicator display and notifications
Requirements: 1.1, 3.1, 3.2
"""

import sys
import os
from typing import Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_types import GameState, PerformanceMetrics, SkillAssessment
from game_board import GameBoard
from difficulty_indicator import DifficultyIndicator
from difficulty_change_notification import DifficultyChangeNotificationSystem
from pause_menu import PauseMenu
from help_system import HelpSystem
from settings_menu import SettingsMenu
from difficulty_manager import DifficultyManager


class GameUI:
    """Integrates game board, difficulty indicator, and notifications into a unified UI"""

    def __init__(self, board_width: int = 20, board_height: int = 20, cell_size: int = 20, difficulty_manager: Optional[DifficultyManager] = None):
        """Initialize the game UI with board, difficulty indicator, notification system, pause menu, help system, and settings menu"""
        self.game_board = GameBoard(
            cell_size=cell_size,
            board_width=board_width,
            board_height=board_height
        )
        self.difficulty_indicator = DifficultyIndicator()
        self.notification_system = DifficultyChangeNotificationSystem()
        self.pause_menu = PauseMenu()
        self.help_system = HelpSystem()
        
        # Initialize difficulty manager if not provided
        if difficulty_manager is None:
            difficulty_manager = DifficultyManager()
        self.difficulty_manager = difficulty_manager
        self.settings_menu = SettingsMenu(difficulty_manager)
        
        self.last_difficulty: Optional[GameState] = None

    def update_game_state(self, game_state: GameState) -> None:
        """Update the UI with new game state"""
        # Check for difficulty changes and create notifications
        if self.last_difficulty and self.last_difficulty.difficulty != game_state.difficulty:
            self.notification_system.detect_changes(
                self.last_difficulty.difficulty,
                game_state.difficulty
            )
        
        # Update difficulty indicator
        self.difficulty_indicator.update_difficulty(game_state.difficulty)
        
        # Store current difficulty for next comparison
        self.last_difficulty = game_state

    def render_game_display(self, game_state: GameState) -> str:
        """
        Render the complete game display including board, difficulty indicator, and notifications
        Returns a formatted string representation of the full UI
        """
        # Validate game state can be rendered
        if not self.game_board.validate_render(game_state):
            return "Invalid game state"

        # Update UI state
        self.update_game_state(game_state)

        # Build the display
        lines = []

        # Add difficulty indicator at top
        difficulty_display = self.difficulty_indicator.get_difficulty_display()
        lines.append(difficulty_display)
        lines.append("-" * len(difficulty_display))

        # Add notification if active
        if self.notification_system.is_notification_active():
            notification_display = self.notification_system.get_notification_display()
            lines.append(f"[NOTIFICATION] {notification_display}")
            lines.append("")

        # Add game board
        board_str = self.game_board.render_to_string(game_state)
        lines.append(board_str)

        return "\n".join(lines)

    def render_game_display_with_info(self, game_state: GameState) -> str:
        """
        Render the complete game display with additional difficulty information and notifications
        Returns a formatted string with board, difficulty, detailed info, and notifications
        """
        # Validate game state can be rendered
        if not self.game_board.validate_render(game_state):
            return "Invalid game state"

        # Update UI state
        self.update_game_state(game_state)

        # Build the display
        lines = []

        # Add difficulty indicator at top
        difficulty_display = self.difficulty_indicator.get_difficulty_display()
        lines.append(difficulty_display)
        lines.append("-" * len(difficulty_display))

        # Add notification if active
        if self.notification_system.is_notification_active():
            notification_display = self.notification_system.get_notification_display()
            lines.append(f"[NOTIFICATION] {notification_display}")
            lines.append("")

        # Add game board
        board_str = self.game_board.render_to_string(game_state)
        lines.append(board_str)

        # Add difficulty details
        lines.append("")
        lines.append("Difficulty Details:")
        difficulty_info = self.difficulty_indicator.get_difficulty_info()
        if difficulty_info:
            lines.append(f"  Category: {difficulty_info['category']}")
            lines.append(f"  Speed: {difficulty_info['speed']}/10")
            lines.append(f"  Obstacles: {difficulty_info['obstacle_density']}/5")
            lines.append(f"  Food Spawn Rate: {difficulty_info['food_spawn_rate']:.1f}x")

        return "\n".join(lines)

    def get_difficulty_display(self) -> str:
        """Get just the difficulty display string"""
        return self.difficulty_indicator.get_difficulty_display()

    def get_difficulty_color(self) -> str:
        """Get the color code for current difficulty"""
        return self.difficulty_indicator.get_difficulty_color()

    def get_difficulty_category(self) -> str:
        """Get the difficulty category name"""
        return self.difficulty_indicator.get_difficulty_category()

    def get_difficulty_info(self) -> dict:
        """Get complete difficulty information"""
        return self.difficulty_indicator.get_difficulty_info()

    def is_adaptive_mode(self) -> bool:
        """Check if adaptive mode is enabled"""
        return self.difficulty_indicator.is_adaptive_mode()

    def get_difficulty_level(self) -> int:
        """Get the numeric difficulty level"""
        return self.difficulty_indicator.get_difficulty_level()

    def get_game_board(self) -> GameBoard:
        """Get the game board component"""
        return self.game_board

    def get_difficulty_indicator(self) -> DifficultyIndicator:
        """Get the difficulty indicator component"""
        return self.difficulty_indicator

    def get_notification_system(self) -> DifficultyChangeNotificationSystem:
        """Get the notification system component"""
        return self.notification_system

    def advance_notifications(self, current_time: Optional[float] = None) -> bool:
        """
        Advance to next notification if current one has expired
        Returns True if there are more notifications to display
        """
        if current_time is None:
            current_time = datetime.now().timestamp()
        return self.notification_system.advance_notification(current_time)

    def get_active_notification_display(self) -> str:
        """Get the display string for the active notification"""
        return self.notification_system.get_notification_display()

    def is_notification_active(self) -> bool:
        """Check if there's an active notification"""
        return self.notification_system.is_notification_active()

    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notification_system.clear_notifications()

    def get_pause_menu(self) -> PauseMenu:
        """Get the pause menu component"""
        return self.pause_menu

    def pause_game(self) -> None:
        """Pause the game"""
        self.pause_menu.pause()

    def resume_game(self) -> None:
        """Resume the game"""
        self.pause_menu.resume()

    def toggle_pause(self) -> bool:
        """Toggle pause state and return new state"""
        return self.pause_menu.toggle_pause()

    def is_game_paused(self) -> bool:
        """Check if game is paused"""
        return self.pause_menu.is_game_paused()

    def set_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Set performance metrics for pause menu display"""
        self.pause_menu.set_performance_metrics(metrics)

    def set_skill_assessment(self, assessment: SkillAssessment) -> None:
        """Set skill assessment for pause menu display"""
        self.pause_menu.set_skill_assessment(assessment)

    def render_pause_display(self) -> str:
        """Render the pause menu display"""
        if not self.is_game_paused():
            return ""
        return self.pause_menu.get_full_pause_display()

    def render_game_display_with_pause(self, game_state: GameState) -> str:
        """
        Render game display, showing pause menu if paused
        Returns pause menu if paused, otherwise returns normal game display
        """
        if self.is_game_paused():
            return self.render_pause_display()
        return self.render_game_display(game_state)

    def get_help_system(self) -> HelpSystem:
        """Get the help system component"""
        return self.help_system

    def render_help_menu(self) -> str:
        """Render the help menu"""
        return self.help_system.get_help_menu()

    def render_adaptation_strategy(self) -> str:
        """Render the adaptation strategy explanation"""
        # Update help system with current difficulty and assessment
        self.help_system.set_difficulty_level(self.difficulty_indicator.get_current_difficulty())
        return self.help_system.get_adaptation_strategy_explanation()

    def render_quick_tips(self) -> str:
        """Render quick tips"""
        return self.help_system.get_quick_tips()

    def render_difficulty_guide(self) -> str:
        """Render difficulty guide"""
        return self.help_system.get_difficulty_guide()

    def render_faq(self) -> str:
        """Render FAQ"""
        return self.help_system.get_faq()

    def get_settings_menu(self) -> SettingsMenu:
        """Get the settings menu component"""
        return self.settings_menu

    def open_settings_menu(self) -> None:
        """Open the settings menu"""
        self.settings_menu.open_menu()

    def close_settings_menu(self) -> None:
        """Close the settings menu"""
        self.settings_menu.close_menu()

    def toggle_settings_menu(self) -> bool:
        """Toggle settings menu open/closed state"""
        return self.settings_menu.toggle_menu()

    def is_settings_menu_open(self) -> bool:
        """Check if settings menu is open"""
        return self.settings_menu.is_menu_open()

    def render_settings_menu(self) -> str:
        """Render the settings menu display"""
        return self.settings_menu.get_menu_display()

    def render_game_display_with_settings(self, game_state: GameState) -> str:
        """
        Render game display, showing settings menu if open
        Returns settings menu if open, otherwise returns normal game display
        """
        if self.is_settings_menu_open():
            return self.render_settings_menu()
        return self.render_game_display(game_state)
