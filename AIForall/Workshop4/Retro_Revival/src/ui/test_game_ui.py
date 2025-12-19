"""
Unit tests for GameUI component
Tests difficulty indicator display integration with game board rendering
Requirements: 1.1, 3.1
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.game_ui import GameUI
from game_types import GameState, Segment, Position, Obstacle, DifficultyLevel


class TestGameUIIntegration:
    """Test suite for GameUI integration component"""

    @pytest.fixture
    def game_ui(self):
        """Create a game UI instance"""
        return GameUI(board_width=20, board_height=20, cell_size=20)

    @pytest.fixture
    def default_difficulty(self):
        """Create default difficulty level"""
        return DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

    def create_game_state(self, difficulty=None, snake=None, food=None, obstacles=None, score=0):
        """Helper to create a game state"""
        if difficulty is None:
            difficulty = DifficultyLevel(
                level=5,
                speed=5,
                obstacle_density=2,
                food_spawn_rate=1.0,
                adaptive_mode=True
            )

        if snake is None:
            snake = [Segment(x=10, y=10), Segment(x=10, y=11), Segment(x=10, y=12)]
        if food is None:
            food = [Position(x=5, y=5)]
        if obstacles is None:
            obstacles = [Obstacle(x=8, y=8, type='static')]

        return GameState(
            snake=snake,
            food=food,
            obstacles=obstacles,
            score=score,
            game_over=False,
            difficulty=difficulty,
            timestamp=0
        )

    # Initialization Tests
    def test_game_ui_initialization(self, game_ui):
        """Test GameUI initializes correctly"""
        assert game_ui.game_board is not None
        assert game_ui.difficulty_indicator is not None

    def test_game_ui_custom_dimensions(self):
        """Test GameUI with custom board dimensions"""
        ui = GameUI(board_width=30, board_height=25, cell_size=15)
        assert ui.game_board.board_width == 30
        assert ui.game_board.board_height == 25
        assert ui.game_board.cell_size == 15

    # Difficulty Display Tests
    def test_render_difficulty_display_easy(self, game_ui):
        """Test rendering difficulty display for easy level"""
        difficulty = DifficultyLevel(
            level=2, speed=2, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        display = game_ui.get_difficulty_display()
        assert "2/10" in display
        assert "Adaptive" in display

    def test_render_difficulty_display_medium(self, game_ui):
        """Test rendering difficulty display for medium level"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        display = game_ui.get_difficulty_display()
        assert "5/10" in display

    def test_render_difficulty_display_hard(self, game_ui):
        """Test rendering difficulty display for hard level"""
        difficulty = DifficultyLevel(
            level=8, speed=8, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=False
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        display = game_ui.get_difficulty_display()
        assert "8/10" in display
        assert "Manual" in display

    def test_render_difficulty_display_very_hard(self, game_ui):
        """Test rendering difficulty display for very hard level"""
        difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        display = game_ui.get_difficulty_display()
        assert "10/10" in display

    # Complete Game Display Tests
    def test_render_game_display_basic(self, game_ui):
        """Test rendering complete game display"""
        game_state = self.create_game_state()
        display = game_ui.render_game_display(game_state)

        # Should contain difficulty display
        assert "5/10" in display
        # Should contain board elements
        assert "H" in display  # Snake head
        assert "*" in display  # Food
        assert "#" in display  # Obstacle
        assert "Score:" in display

    def test_render_game_display_with_info(self, game_ui):
        """Test rendering game display with detailed difficulty info"""
        game_state = self.create_game_state()
        display = game_ui.render_game_display_with_info(game_state)

        # Should contain difficulty display
        assert "5/10" in display
        # Should contain board elements
        assert "H" in display
        assert "*" in display
        assert "#" in display
        # Should contain difficulty details
        assert "Difficulty Details:" in display
        assert "Category:" in display
        assert "Speed:" in display
        assert "Obstacles:" in display
        assert "Food Spawn Rate:" in display

    def test_render_game_display_all_difficulty_levels(self, game_ui):
        """Test rendering game display for all difficulty levels"""
        for level in range(1, 11):
            difficulty = DifficultyLevel(
                level=level,
                speed=level,
                obstacle_density=level // 2,
                food_spawn_rate=0.5 + (level * 0.15),
                adaptive_mode=level % 2 == 0
            )
            game_state = self.create_game_state(difficulty=difficulty)
            display = game_ui.render_game_display(game_state)

            assert f"{level}/10" in display

    # Difficulty Info Tests
    def test_get_difficulty_color(self, game_ui):
        """Test getting difficulty color"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        color = game_ui.get_difficulty_color()
        assert color == "YELLOW"  # Medium difficulty

    def test_get_difficulty_category(self, game_ui):
        """Test getting difficulty category"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        category = game_ui.get_difficulty_category()
        assert category == "Medium"

    def test_get_difficulty_info(self, game_ui):
        """Test getting complete difficulty information"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        info = game_ui.get_difficulty_info()
        assert info["level"] == 5
        assert info["speed"] == 5
        assert info["obstacle_density"] == 2
        assert info["food_spawn_rate"] == 1.0
        assert info["adaptive_mode"] is True
        assert info["category"] == "Medium"
        assert info["color"] == "YELLOW"

    def test_is_adaptive_mode(self, game_ui):
        """Test checking adaptive mode"""
        adaptive_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=adaptive_difficulty)
        game_ui.update_game_state(game_state)
        assert game_ui.is_adaptive_mode() is True

        manual_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        )
        game_state = self.create_game_state(difficulty=manual_difficulty)
        game_ui.update_game_state(game_state)
        assert game_ui.is_adaptive_mode() is False

    def test_get_difficulty_level(self, game_ui):
        """Test getting difficulty level"""
        difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.5, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        level = game_ui.get_difficulty_level()
        assert level == 7

    # Component Access Tests
    def test_get_game_board(self, game_ui):
        """Test getting game board component"""
        board = game_ui.get_game_board()
        assert board is not None
        assert board == game_ui.game_board

    def test_get_difficulty_indicator(self, game_ui):
        """Test getting difficulty indicator component"""
        indicator = game_ui.get_difficulty_indicator()
        assert indicator is not None
        assert indicator == game_ui.difficulty_indicator

    # State Update Tests
    def test_update_game_state_updates_difficulty(self, game_ui):
        """Test that updating game state updates difficulty indicator"""
        difficulty = DifficultyLevel(
            level=3, speed=3, obstacle_density=1, food_spawn_rate=0.7, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        assert game_ui.get_difficulty_level() == 3

    def test_update_game_state_multiple_times(self, game_ui):
        """Test updating game state multiple times"""
        difficulty1 = DifficultyLevel(
            level=2, speed=2, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)
        assert game_ui.get_difficulty_level() == 2

        difficulty2 = DifficultyLevel(
            level=8, speed=8, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=False
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        game_ui.update_game_state(game_state2)
        assert game_ui.get_difficulty_level() == 8

    # Invalid State Tests
    def test_render_invalid_game_state(self, game_ui):
        """Test rendering with invalid game state"""
        # Create invalid state with out-of-bounds snake
        invalid_state = GameState(
            snake=[Segment(x=25, y=25)],  # Out of bounds
            food=[Position(x=5, y=5)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=0
        )

        display = game_ui.render_game_display(invalid_state)
        assert display == "Invalid game state"

    # Edge Cases Tests
    def test_render_with_no_food(self, game_ui):
        """Test rendering game display with no food"""
        game_state = self.create_game_state(food=[])
        display = game_ui.render_game_display(game_state)

        assert "5/10" in display
        assert "H" in display
        assert "Score:" in display

    def test_render_with_no_obstacles(self, game_ui):
        """Test rendering game display with no obstacles"""
        game_state = self.create_game_state(obstacles=[])
        display = game_ui.render_game_display(game_state)

        assert "5/10" in display
        assert "H" in display
        assert "*" in display

    def test_render_with_high_score(self, game_ui):
        """Test rendering with high score"""
        game_state = self.create_game_state(score=9999)
        display = game_ui.render_game_display(game_state)

        assert "Score: 9999" in display

    def test_render_with_long_snake(self, game_ui):
        """Test rendering with long snake"""
        # Create a snake that fits within the 20x20 board
        snake = [Segment(x=10, y=10 - i) for i in range(10)]  # 10 segments going up
        game_state = self.create_game_state(snake=snake)
        display = game_ui.render_game_display(game_state)

        assert "H" in display
        assert "S" in display

    # Display Format Tests
    def test_display_format_contains_separator(self, game_ui):
        """Test that display contains separator line"""
        game_state = self.create_game_state()
        display = game_ui.render_game_display(game_state)

        # Should have separator line after difficulty display
        lines = display.split("\n")
        assert len(lines) > 2
        # Second line should be separator (dashes)
        assert "-" in lines[1]

    def test_display_format_with_info_contains_details(self, game_ui):
        """Test that detailed display contains all sections"""
        game_state = self.create_game_state()
        display = game_ui.render_game_display_with_info(game_state)

        lines = display.split("\n")
        # Should have multiple sections
        assert len(lines) > 10
        # Should contain difficulty details section
        assert any("Difficulty Details:" in line for line in lines)

    # Consistency Tests
    def test_difficulty_display_consistency(self, game_ui):
        """Test that difficulty display is consistent across calls"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)

        display1 = game_ui.get_difficulty_display()
        display2 = game_ui.get_difficulty_display()

        assert display1 == display2

    def test_game_display_consistency(self, game_ui):
        """Test that game display is consistent across calls"""
        game_state = self.create_game_state()

        display1 = game_ui.render_game_display(game_state)
        display2 = game_ui.render_game_display(game_state)

        assert display1 == display2

    # Notification System Tests
    def test_notification_system_initialized(self, game_ui):
        """Test that notification system is initialized"""
        assert game_ui.get_notification_system() is not None

    def test_notification_on_difficulty_change(self, game_ui):
        """Test that notification is created when difficulty changes"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        game_ui.update_game_state(game_state2)

        # Should have active notification
        assert game_ui.is_notification_active()

    def test_no_notification_on_same_difficulty(self, game_ui):
        """Test that no notification is created when difficulty stays same"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = self.create_game_state(difficulty=difficulty)
        game_ui.update_game_state(game_state)
        game_ui.update_game_state(game_state)

        # Should not have active notification
        assert not game_ui.is_notification_active()

    def test_notification_display_in_render(self, game_ui):
        """Test that notification appears in rendered display"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        display = game_ui.render_game_display(game_state2)

        # Display should contain notification
        assert "[NOTIFICATION]" in display

    def test_notification_display_with_info(self, game_ui):
        """Test that notification appears in detailed display"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        display = game_ui.render_game_display_with_info(game_state2)

        # Display should contain notification
        assert "[NOTIFICATION]" in display

    def test_get_active_notification_display(self, game_ui):
        """Test getting active notification display"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        game_ui.update_game_state(game_state2)

        display = game_ui.get_active_notification_display()
        assert len(display) > 0

    def test_advance_notifications(self, game_ui):
        """Test advancing through notifications"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty with multiple parameter changes
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        game_ui.update_game_state(game_state2)

        # Should have active notification
        assert game_ui.is_notification_active()

        # Advance past first notification
        has_more = game_ui.advance_notifications()
        # May or may not have more depending on timing

    def test_clear_notifications(self, game_ui):
        """Test clearing notifications"""
        # Create initial game state
        difficulty1 = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state1 = self.create_game_state(difficulty=difficulty1)
        game_ui.update_game_state(game_state1)

        # Change difficulty
        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.2, adaptive_mode=True
        )
        game_state2 = self.create_game_state(difficulty=difficulty2)
        game_ui.update_game_state(game_state2)

        # Should have active notification
        assert game_ui.is_notification_active()

        # Clear notifications
        game_ui.clear_notifications()

        # Should not have active notification
        assert not game_ui.is_notification_active()

    # Pause Menu Tests
    def test_pause_menu_initialized(self, game_ui):
        """Test that pause menu is initialized"""
        assert game_ui.get_pause_menu() is not None

    def test_pause_game(self, game_ui):
        """Test pausing the game"""
        game_ui.pause_game()
        assert game_ui.is_game_paused()

    def test_resume_game(self, game_ui):
        """Test resuming the game"""
        game_ui.pause_game()
        game_ui.resume_game()
        assert not game_ui.is_game_paused()

    def test_toggle_pause(self, game_ui):
        """Test toggling pause"""
        result = game_ui.toggle_pause()
        assert result is True
        assert game_ui.is_game_paused()

        result = game_ui.toggle_pause()
        assert result is False
        assert not game_ui.is_game_paused()

    def test_set_performance_metrics(self, game_ui):
        """Test setting performance metrics"""
        from game_types import PerformanceMetrics
        metrics = PerformanceMetrics(
            survival_time=100,
            food_consumed=10,
            reaction_time=[100, 120],
            collisions_avoided=2,
            average_speed=2.0,
            timestamp=0
        )
        game_ui.set_performance_metrics(metrics)
        assert game_ui.get_pause_menu().has_metrics()

    def test_set_skill_assessment(self, game_ui):
        """Test setting skill assessment"""
        from game_types import SkillAssessment
        assessment = SkillAssessment(
            skill_level=75,
            trend='improving',
            confidence=0.85,
            last_updated=0
        )
        game_ui.set_skill_assessment(assessment)
        assert game_ui.get_pause_menu().has_assessment()

    def test_render_pause_display_when_paused(self, game_ui):
        """Test rendering pause display when game is paused"""
        from game_types import PerformanceMetrics, SkillAssessment
        
        metrics = PerformanceMetrics(
            survival_time=100,
            food_consumed=10,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=2.0,
            timestamp=0
        )
        assessment = SkillAssessment(
            skill_level=75,
            trend='improving',
            confidence=0.85,
            last_updated=0
        )
        
        game_ui.set_performance_metrics(metrics)
        game_ui.set_skill_assessment(assessment)
        game_ui.pause_game()

        display = game_ui.render_pause_display()
        assert "GAME PAUSED" in display
        assert "PERFORMANCE SUMMARY" in display

    def test_render_pause_display_when_not_paused(self, game_ui):
        """Test rendering pause display when game is not paused"""
        display = game_ui.render_pause_display()
        assert display == ""

    def test_render_game_display_with_pause_when_paused(self, game_ui):
        """Test rendering game display with pause when paused"""
        from game_types import PerformanceMetrics, SkillAssessment
        
        metrics = PerformanceMetrics(
            survival_time=100,
            food_consumed=10,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=2.0,
            timestamp=0
        )
        assessment = SkillAssessment(
            skill_level=75,
            trend='improving',
            confidence=0.85,
            last_updated=0
        )
        
        game_state = self.create_game_state()
        game_ui.set_performance_metrics(metrics)
        game_ui.set_skill_assessment(assessment)
        game_ui.pause_game()

        display = game_ui.render_game_display_with_pause(game_state)
        assert "GAME PAUSED" in display

    def test_render_game_display_with_pause_when_not_paused(self, game_ui):
        """Test rendering game display with pause when not paused"""
        game_state = self.create_game_state()
        display = game_ui.render_game_display_with_pause(game_state)

        # Should show normal game display
        assert "5/10" in display  # Difficulty display
        assert "H" in display  # Snake head

    # Help System Tests
    def test_help_system_initialized(self, game_ui):
        """Test that help system is initialized"""
        assert game_ui.get_help_system() is not None

    def test_render_help_menu(self, game_ui):
        """Test rendering help menu"""
        menu = game_ui.render_help_menu()

        assert "SNAKE ADAPTIVE AI - HELP" in menu
        assert "GAME CONTROLS:" in menu

    def test_render_adaptation_strategy(self, game_ui):
        """Test rendering adaptation strategy"""
        strategy = game_ui.render_adaptation_strategy()

        assert "ADAPTATION STRATEGY" in strategy

    def test_render_quick_tips(self, game_ui):
        """Test rendering quick tips"""
        tips = game_ui.render_quick_tips()

        assert "QUICK TIPS" in tips
        assert "BEGINNER TIPS:" in tips

    def test_render_difficulty_guide(self, game_ui):
        """Test rendering difficulty guide"""
        guide = game_ui.render_difficulty_guide()

        assert "DIFFICULTY GUIDE" in guide
        assert "EASY" in guide

    def test_render_faq(self, game_ui):
        """Test rendering FAQ"""
        faq = game_ui.render_faq()

        assert "FREQUENTLY ASKED QUESTIONS" in faq
        assert "Q:" in faq
