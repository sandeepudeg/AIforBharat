"""
Unit tests for HelpSystem component
Tests help menu and adaptation strategy explanation display
Requirements: 3.4
"""

import pytest
from help_system import HelpSystem
from game_types import DifficultyLevel, SkillAssessment


class TestHelpSystem:
    """Test suite for help system component"""

    @pytest.fixture
    def help_system(self):
        """Create a help system instance"""
        return HelpSystem()

    @pytest.fixture
    def sample_difficulty(self):
        """Create sample difficulty level"""
        return DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

    @pytest.fixture
    def sample_assessment(self):
        """Create sample skill assessment"""
        return SkillAssessment(
            skill_level=75,
            trend='improving',
            confidence=0.85,
            last_updated=0
        )

    # Initialization Tests
    def test_initialization(self, help_system):
        """Test help system initializes empty"""
        assert help_system.current_difficulty is None
        assert help_system.current_skill_assessment is None

    # Help Menu Tests
    def test_get_help_menu(self, help_system):
        """Test getting help menu"""
        menu = help_system.get_help_menu()

        assert "SNAKE ADAPTIVE AI - HELP" in menu
        assert "GAME CONTROLS:" in menu
        assert "Arrow Keys" in menu
        assert "DIFFICULTY SYSTEM:" in menu
        assert "ADAPTIVE PARAMETERS:" in menu
        assert "Speed:" in menu
        assert "Obstacles:" in menu
        assert "Food Spawn Rate:" in menu

    def test_help_menu_contains_controls(self, help_system):
        """Test help menu contains game controls"""
        menu = help_system.get_help_menu()

        assert "Arrow Keys" in menu or "WASD" in menu
        assert "SPACE" in menu
        assert "Pause" in menu

    def test_help_menu_contains_difficulty_info(self, help_system):
        """Test help menu contains difficulty information"""
        menu = help_system.get_help_menu()

        assert "Easy" in menu
        assert "Medium" in menu
        assert "Hard" in menu
        assert "Very Hard" in menu

    def test_help_menu_contains_tips(self, help_system):
        """Test help menu contains tips"""
        menu = help_system.get_help_menu()

        assert "TIPS:" in menu

    # Adaptation Strategy Tests
    def test_get_adaptation_strategy_without_data(self, help_system):
        """Test getting adaptation strategy without data"""
        strategy = help_system.get_adaptation_strategy_explanation()

        assert "ADAPTATION STRATEGY" in strategy
        assert "MONITORING:" in strategy
        assert "ASSESSMENT:" in strategy
        assert "ADJUSTMENT:" in strategy
        assert "SMOOTHING:" in strategy

    def test_get_adaptation_strategy_with_improving_trend(self, help_system, sample_difficulty, sample_assessment):
        """Test adaptation strategy with improving trend"""
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "CURRENT ADAPTATION STRATEGY" in strategy
        assert "75/100" in strategy
        assert "improving" in strategy.lower()
        assert "harder" in strategy.lower()

    def test_get_adaptation_strategy_with_declining_trend(self, help_system, sample_difficulty):
        """Test adaptation strategy with declining trend"""
        assessment = SkillAssessment(
            skill_level=40,
            trend='declining',
            confidence=0.70,
            last_updated=0
        )
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "struggling" in strategy.lower() or "declining" in strategy.lower()
        assert "easier" in strategy.lower()

    def test_get_adaptation_strategy_with_stable_trend(self, help_system, sample_difficulty):
        """Test adaptation strategy with stable trend"""
        assessment = SkillAssessment(
            skill_level=60,
            trend='stable',
            confidence=0.75,
            last_updated=0
        )
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "stable" in strategy.lower()
        assert "consistent" in strategy.lower()

    def test_adaptation_strategy_shows_parameters(self, help_system, sample_difficulty, sample_assessment):
        """Test that adaptation strategy shows current parameters"""
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "Speed: 5/10" in strategy
        assert "Obstacles: 2/5" in strategy
        assert "Food Spawn Rate: 1.0x" in strategy

    def test_adaptation_strategy_shows_mode(self, help_system, sample_difficulty, sample_assessment):
        """Test that adaptation strategy shows adaptive mode"""
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "ADAPTIVE" in strategy

    def test_adaptation_strategy_shows_manual_mode(self, help_system, sample_assessment):
        """Test that adaptation strategy shows manual mode"""
        manual_difficulty = DifficultyLevel(
            level=5, speed=5, obstacle_density=2, food_spawn_rate=1.0, adaptive_mode=False
        )
        help_system.set_difficulty_level(manual_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "MANUAL" in strategy

    # Quick Tips Tests
    def test_get_quick_tips(self, help_system):
        """Test getting quick tips"""
        tips = help_system.get_quick_tips()

        assert "QUICK TIPS" in tips
        assert "BEGINNER TIPS:" in tips
        assert "INTERMEDIATE TIPS:" in tips
        assert "ADVANCED TIPS:" in tips
        assert "GENERAL TIPS:" in tips

    def test_quick_tips_contains_beginner_advice(self, help_system):
        """Test quick tips contains beginner advice"""
        tips = help_system.get_quick_tips()

        assert "easy difficulty" in tips.lower()
        assert "learn" in tips.lower()

    def test_quick_tips_contains_advanced_advice(self, help_system):
        """Test quick tips contains advanced advice"""
        tips = help_system.get_quick_tips()

        assert "predict" in tips.lower() or "pattern" in tips.lower()

    # Difficulty Guide Tests
    def test_get_difficulty_guide(self, help_system):
        """Test getting difficulty guide"""
        guide = help_system.get_difficulty_guide()

        assert "DIFFICULTY GUIDE" in guide
        assert "LEVEL 1-3: EASY" in guide
        assert "LEVEL 4-6: MEDIUM" in guide
        assert "LEVEL 7-8: HARD" in guide
        assert "LEVEL 9-10: VERY HARD" in guide

    def test_difficulty_guide_contains_easy_info(self, help_system):
        """Test difficulty guide contains easy level info"""
        guide = help_system.get_difficulty_guide()

        assert "EASY" in guide
        assert "1-3/10" in guide or "Slow" in guide

    def test_difficulty_guide_contains_hard_info(self, help_system):
        """Test difficulty guide contains hard level info"""
        guide = help_system.get_difficulty_guide()

        assert "HARD" in guide
        assert "7-8/10" in guide or "Fast" in guide

    def test_difficulty_guide_contains_very_hard_info(self, help_system):
        """Test difficulty guide contains very hard level info"""
        guide = help_system.get_difficulty_guide()

        assert "VERY HARD" in guide
        assert "9-10/10" in guide or "Very Fast" in guide

    # FAQ Tests
    def test_get_faq(self, help_system):
        """Test getting FAQ"""
        faq = help_system.get_faq()

        assert "FREQUENTLY ASKED QUESTIONS" in faq
        assert "Q:" in faq
        assert "A:" in faq

    def test_faq_contains_difficulty_questions(self, help_system):
        """Test FAQ contains difficulty-related questions"""
        faq = help_system.get_faq()

        assert "difficulty" in faq.lower()

    def test_faq_contains_skill_questions(self, help_system):
        """Test FAQ contains skill-related questions"""
        faq = help_system.get_faq()

        assert "skill" in faq.lower()

    def test_faq_contains_manual_mode_info(self, help_system):
        """Test FAQ contains manual mode information"""
        faq = help_system.get_faq()

        assert "manual" in faq.lower()

    # Set Data Tests
    def test_set_difficulty_level(self, help_system, sample_difficulty):
        """Test setting difficulty level"""
        help_system.set_difficulty_level(sample_difficulty)
        assert help_system.current_difficulty == sample_difficulty

    def test_set_skill_assessment(self, help_system, sample_assessment):
        """Test setting skill assessment"""
        help_system.set_skill_assessment(sample_assessment)
        assert help_system.current_skill_assessment == sample_assessment

    # Edge Cases Tests
    def test_adaptation_strategy_with_zero_skill(self, help_system, sample_difficulty):
        """Test adaptation strategy with zero skill level"""
        assessment = SkillAssessment(
            skill_level=0,
            trend='declining',
            confidence=0.1,
            last_updated=0
        )
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "0/100" in strategy

    def test_adaptation_strategy_with_max_skill(self, help_system, sample_difficulty):
        """Test adaptation strategy with maximum skill level"""
        assessment = SkillAssessment(
            skill_level=100,
            trend='improving',
            confidence=0.99,
            last_updated=0
        )
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "100/100" in strategy

    def test_adaptation_strategy_with_easy_difficulty(self, help_system, sample_assessment):
        """Test adaptation strategy with easy difficulty"""
        easy_difficulty = DifficultyLevel(
            level=1, speed=1, obstacle_density=0, food_spawn_rate=0.5, adaptive_mode=True
        )
        help_system.set_difficulty_level(easy_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "1/10" in strategy

    def test_adaptation_strategy_with_hard_difficulty(self, help_system, sample_assessment):
        """Test adaptation strategy with hard difficulty"""
        hard_difficulty = DifficultyLevel(
            level=10, speed=10, obstacle_density=5, food_spawn_rate=2.0, adaptive_mode=True
        )
        help_system.set_difficulty_level(hard_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy = help_system.get_adaptation_strategy_explanation()

        assert "10/10" in strategy

    # Content Consistency Tests
    def test_all_menus_have_proper_formatting(self, help_system):
        """Test that all menus have proper formatting"""
        menus = [
            help_system.get_help_menu(),
            help_system.get_quick_tips(),
            help_system.get_difficulty_guide(),
            help_system.get_faq()
        ]

        for menu in menus:
            assert "╔" in menu or "=" in menu  # Has header
            assert len(menu) > 100  # Has substantial content

    def test_strategy_explanation_consistency(self, help_system, sample_difficulty, sample_assessment):
        """Test that strategy explanation is consistent"""
        help_system.set_difficulty_level(sample_difficulty)
        help_system.set_skill_assessment(sample_assessment)

        strategy1 = help_system.get_adaptation_strategy_explanation()
        strategy2 = help_system.get_adaptation_strategy_explanation()

        assert strategy1 == strategy2

    # Multiple Updates Tests
    def test_multiple_difficulty_updates(self, help_system, sample_assessment):
        """Test updating difficulty multiple times"""
        difficulty1 = DifficultyLevel(
            level=3, speed=3, obstacle_density=1, food_spawn_rate=0.7, adaptive_mode=True
        )
        help_system.set_difficulty_level(difficulty1)
        help_system.set_skill_assessment(sample_assessment)
        strategy1 = help_system.get_adaptation_strategy_explanation()

        difficulty2 = DifficultyLevel(
            level=8, speed=8, obstacle_density=4, food_spawn_rate=1.5, adaptive_mode=True
        )
        help_system.set_difficulty_level(difficulty2)
        strategy2 = help_system.get_adaptation_strategy_explanation()

        assert strategy1 != strategy2
        assert "3/10" in strategy1
        assert "8/10" in strategy2

    def test_multiple_assessment_updates(self, help_system, sample_difficulty):
        """Test updating assessment multiple times"""
        help_system.set_difficulty_level(sample_difficulty)

        assessment1 = SkillAssessment(
            skill_level=30, trend='declining', confidence=0.6, last_updated=0
        )
        help_system.set_skill_assessment(assessment1)
        strategy1 = help_system.get_adaptation_strategy_explanation()

        assessment2 = SkillAssessment(
            skill_level=80, trend='improving', confidence=0.9, last_updated=0
        )
        help_system.set_skill_assessment(assessment2)
        strategy2 = help_system.get_adaptation_strategy_explanation()

        assert strategy1 != strategy2
        assert "struggling" in strategy1.lower() or "declining" in strategy1.lower()
        assert "improving" in strategy2.lower()
