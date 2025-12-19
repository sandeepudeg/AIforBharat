"""
Unit tests for DifficultyIndicator component
Tests difficulty level display (1-10) and visual representation
Requirements: 3.1
"""

import pytest
from difficulty_indicator import DifficultyIndicator
from game_types import DifficultyLevel


class TestDifficultyIndicator:
    """Test suite for DifficultyIndicator component"""

    @pytest.fixture
    def indicator(self):
        """Create a difficulty indicator instance"""
        return DifficultyIndicator()

    # Initialization Tests
    def test_initialization(self, indicator):
        """Test indicator initializes with no difficulty"""
        assert indicator.get_current_difficulty() is None

    def test_initialization_display(self, indicator):
        """Test initial display message"""
        display = indicator.get_difficulty_display()
        assert display == "No difficulty set"

    # Difficulty Display Tests
    def test_display_difficulty_1(self, indicator):
        """Test displaying difficulty level 1"""
        difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        assert "1/10" in display

    def test_display_difficulty_5(self, indicator):
        """Test displaying difficulty level 5"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        assert "5/10" in display

    def test_display_difficulty_10(self, indicator):
        """Test displaying difficulty level 10"""
        difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        assert "10/10" in display

    def test_display_all_difficulty_levels(self, indicator):
        """Test displaying all difficulty levels 1-10"""
        for level in range(1, 11):
            difficulty = DifficultyLevel(
                level=level,
                speed=level,
                obstacle_density=level // 2,
                food_spawn_rate=0.5 + (level * 0.15),
                adaptive_mode=True
            )
            indicator.update_difficulty(difficulty)
            display = indicator.get_difficulty_display()
            assert f"{level}/10" in display

    # Visual Representation Tests
    def test_visual_bar_difficulty_1(self, indicator):
        """Test visual bar for difficulty 1"""
        difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        # Should have mostly empty bar
        assert "░" in display

    def test_visual_bar_difficulty_5(self, indicator):
        """Test visual bar for difficulty 5"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        # Should have half-filled bar
        assert "█" in display
        assert "░" in display

    def test_visual_bar_difficulty_10(self, indicator):
        """Test visual bar for difficulty 10"""
        difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        # Should have full bar
        assert "█" in display

    # Adaptive Mode Indicator Tests
    def test_adaptive_mode_enabled(self, indicator):
        """Test displaying adaptive mode when enabled"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        assert "Adaptive" in display

    def test_adaptive_mode_disabled(self, indicator):
        """Test displaying manual mode when disabled"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        )
        indicator.update_difficulty(difficulty)
        display = indicator.get_difficulty_display()
        assert "Manual" in display

    def test_toggle_adaptive_mode(self, indicator):
        """Test toggling between adaptive and manual modes"""
        adaptive_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(adaptive_difficulty)
        assert "Adaptive" in indicator.get_difficulty_display()

        manual_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        )
        indicator.update_difficulty(manual_difficulty)
        assert "Manual" in indicator.get_difficulty_display()

    # Color Coding Tests
    def test_color_easy_difficulty(self, indicator):
        """Test green color for easy difficulty (1-3)"""
        for level in range(1, 4):
            difficulty = DifficultyLevel(
                level=level, speed=level, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
            )
            indicator.update_difficulty(difficulty)
            assert indicator.get_difficulty_color() == "GREEN"

    def test_color_medium_difficulty(self, indicator):
        """Test yellow color for medium difficulty (4-6)"""
        for level in range(4, 7):
            difficulty = DifficultyLevel(
                level=level,
                speed=level,
                obstacle_density=level // 2,
                food_spawn_rate=1.0,
                adaptive_mode=True
            )
            indicator.update_difficulty(difficulty)
            assert indicator.get_difficulty_color() == "YELLOW"

    def test_color_hard_difficulty(self, indicator):
        """Test orange color for hard difficulty (7-8)"""
        for level in range(7, 9):
            difficulty = DifficultyLevel(
                level=level,
                speed=level,
                obstacle_density=level // 2,
                food_spawn_rate=1.5,
                adaptive_mode=True
            )
            indicator.update_difficulty(difficulty)
            assert indicator.get_difficulty_color() == "ORANGE"

    def test_color_very_hard_difficulty(self, indicator):
        """Test red color for very hard difficulty (9-10)"""
        for level in range(9, 11):
            difficulty = DifficultyLevel(
                level=level, speed=level, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
            )
            indicator.update_difficulty(difficulty)
            assert indicator.get_difficulty_color() == "RED"

    # Category Tests
    def test_category_easy(self, indicator):
        """Test easy category"""
        difficulty = DifficultyLevel(
            level=2, speed=2, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_difficulty_category() == "Easy"

    def test_category_medium(self, indicator):
        """Test medium category"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_difficulty_category() == "Medium"

    def test_category_hard(self, indicator):
        """Test hard category"""
        difficulty = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.5, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_difficulty_category() == "Hard"

    def test_category_very_hard(self, indicator):
        """Test very hard category"""
        difficulty = DifficultyLevel(
            level=9, speed=9, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_difficulty_category() == "Very Hard"

    # State Management Tests
    def test_store_current_difficulty(self, indicator):
        """Test storing current difficulty"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        current = indicator.get_current_difficulty()
        assert current == difficulty

    def test_update_difficulty_multiple_times(self, indicator):
        """Test updating difficulty multiple times"""
        difficulty1 = DifficultyLevel(
            level=3, speed=3, obstacle_density=1, food_spawn_rate=0.7, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty1)
        assert indicator.get_difficulty_level() == 3

        difficulty2 = DifficultyLevel(
            level=7, speed=7, obstacle_density=3, food_spawn_rate=1.5, adaptive_mode=False
        )
        indicator.update_difficulty(difficulty2)
        assert indicator.get_difficulty_level() == 7

    # Getter Tests
    def test_get_difficulty_level(self, indicator):
        """Test getting difficulty level"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_difficulty_level() == 5

    def test_get_speed(self, indicator):
        """Test getting speed"""
        difficulty = DifficultyLevel(
            level=5, speed=7, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_speed() == 7

    def test_get_obstacle_density(self, indicator):
        """Test getting obstacle density"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=3, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_obstacle_density() == 3

    def test_get_food_spawn_rate(self, indicator):
        """Test getting food spawn rate"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.5, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        assert indicator.get_food_spawn_rate() == 1.5

    def test_is_adaptive_mode(self, indicator):
        """Test checking adaptive mode"""
        adaptive_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(adaptive_difficulty)
        assert indicator.is_adaptive_mode() is True

        manual_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        )
        indicator.update_difficulty(manual_difficulty)
        assert indicator.is_adaptive_mode() is False

    # Info Dictionary Tests
    def test_get_difficulty_info(self, indicator):
        """Test getting complete difficulty information"""
        difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=True
        )
        indicator.update_difficulty(difficulty)
        info = indicator.get_difficulty_info()

        assert info["level"] == 5
        assert info["speed"] == 5
        assert info["obstacle_density"] == 2
        assert info["food_spawn_rate"] == 1.0
        assert info["adaptive_mode"] is True
        assert info["category"] == "Medium"
        assert info["color"] == "YELLOW"
        assert "5/10" in info["display"]

    def test_get_difficulty_info_empty(self, indicator):
        """Test getting difficulty info when no difficulty is set"""
        info = indicator.get_difficulty_info()
        assert info == {}

    # Edge Cases Tests
    def test_rapid_difficulty_updates(self, indicator):
        """Test rapid difficulty updates"""
        for i in range(10):
            difficulty = DifficultyLevel(
                level=(i % 10) + 1,
                speed=(i % 10) + 1,
                obstacle_density=(i % 10) // 2,
                food_spawn_rate=0.5 + ((i % 10) * 0.15),
                adaptive_mode=i % 2 == 0
            )
            indicator.update_difficulty(difficulty)

        assert indicator.get_difficulty_level() == 10

    def test_boundary_difficulty_values(self, indicator):
        """Test boundary difficulty values"""
        min_difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        indicator.update_difficulty(min_difficulty)
        assert indicator.get_difficulty_level() == 1
        assert indicator.get_difficulty_category() == "Easy"

        max_difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        indicator.update_difficulty(max_difficulty)
        assert indicator.get_difficulty_level() == 10
        assert indicator.get_difficulty_category() == "Very Hard"
