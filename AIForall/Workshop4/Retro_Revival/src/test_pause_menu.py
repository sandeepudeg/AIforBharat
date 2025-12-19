"""
Unit tests for PauseMenu component
Tests pause functionality and performance summary display
Requirements: 3.3
"""

import pytest
from pause_menu import PauseMenu
from game_types import PerformanceMetrics, SkillAssessment


class TestPauseMenu:
    """Test suite for pause menu component"""

    @pytest.fixture
    def pause_menu(self):
        """Create a pause menu instance"""
        return PauseMenu()

    @pytest.fixture
    def sample_metrics(self):
        """Create sample performance metrics"""
        return PerformanceMetrics(
            survival_time=125.5,  # 2m 5.5s
            food_consumed=15,
            reaction_time=[100, 120, 110, 105, 115],
            collisions_avoided=3,
            average_speed=2.5,
            timestamp=0
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
    def test_initialization(self, pause_menu):
        """Test pause menu initializes in unpaused state"""
        assert not pause_menu.is_game_paused()
        assert not pause_menu.has_metrics()
        assert not pause_menu.has_assessment()

    # Pause State Tests
    def test_pause_game(self, pause_menu):
        """Test pausing the game"""
        pause_menu.pause()
        assert pause_menu.is_game_paused()

    def test_resume_game(self, pause_menu):
        """Test resuming the game"""
        pause_menu.pause()
        pause_menu.resume()
        assert not pause_menu.is_game_paused()

    def test_toggle_pause_from_unpaused(self, pause_menu):
        """Test toggling pause from unpaused state"""
        result = pause_menu.toggle_pause()
        assert result is True
        assert pause_menu.is_game_paused()

    def test_toggle_pause_from_paused(self, pause_menu):
        """Test toggling pause from paused state"""
        pause_menu.pause()
        result = pause_menu.toggle_pause()
        assert result is False
        assert not pause_menu.is_game_paused()

    def test_multiple_pause_resume_cycles(self, pause_menu):
        """Test multiple pause/resume cycles"""
        for _ in range(5):
            pause_menu.pause()
            assert pause_menu.is_game_paused()
            pause_menu.resume()
            assert not pause_menu.is_game_paused()

    # Metrics Tests
    def test_set_performance_metrics(self, pause_menu, sample_metrics):
        """Test setting performance metrics"""
        pause_menu.set_performance_metrics(sample_metrics)
        assert pause_menu.has_metrics()

    def test_get_performance_summary_with_metrics(self, pause_menu, sample_metrics):
        """Test getting performance summary with metrics"""
        pause_menu.set_performance_metrics(sample_metrics)
        summary = pause_menu.get_performance_summary()

        assert "PERFORMANCE SUMMARY" in summary
        assert "Survival Time: 2m 5s" in summary
        assert "Food Consumed: 15" in summary
        assert "Average Reaction Time:" in summary
        assert "Collisions Avoided: 3" in summary
        assert "Average Speed: 2.5" in summary

    def test_get_performance_summary_without_metrics(self, pause_menu):
        """Test getting performance summary without metrics"""
        summary = pause_menu.get_performance_summary()
        assert "No performance data available" in summary

    def test_performance_summary_survival_time_formatting(self, pause_menu):
        """Test survival time formatting in summary"""
        metrics = PerformanceMetrics(
            survival_time=3661.5,  # 1h 1m 1.5s
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0,
            timestamp=0
        )
        pause_menu.set_performance_metrics(metrics)
        summary = pause_menu.get_performance_summary()

        assert "61m 1s" in summary

    def test_performance_summary_with_zero_reaction_time(self, pause_menu):
        """Test performance summary with empty reaction time"""
        metrics = PerformanceMetrics(
            survival_time=100,
            food_consumed=5,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=1.5,
            timestamp=0
        )
        pause_menu.set_performance_metrics(metrics)
        summary = pause_menu.get_performance_summary()

        # Should not crash and should contain other metrics
        assert "Survival Time:" in summary
        assert "Food Consumed: 5" in summary

    def test_performance_summary_with_multiple_reaction_times(self, pause_menu):
        """Test performance summary with multiple reaction times"""
        metrics = PerformanceMetrics(
            survival_time=100,
            food_consumed=10,
            reaction_time=[100, 150, 120, 110, 130, 140],
            collisions_avoided=2,
            average_speed=2.0,
            timestamp=0
        )
        pause_menu.set_performance_metrics(metrics)
        summary = pause_menu.get_performance_summary()

        # Average should be (100+150+120+110+130+140)/6 = 125
        assert "Average Reaction Time: 125ms" in summary

    # Skill Assessment Tests
    def test_set_skill_assessment(self, pause_menu, sample_assessment):
        """Test setting skill assessment"""
        pause_menu.set_skill_assessment(sample_assessment)
        assert pause_menu.has_assessment()

    def test_get_skill_assessment_summary_with_assessment(self, pause_menu, sample_assessment):
        """Test getting skill assessment summary with assessment"""
        pause_menu.set_skill_assessment(sample_assessment)
        summary = pause_menu.get_skill_assessment_summary()

        assert "SKILL ASSESSMENT" in summary
        assert "Skill Level: 75/100" in summary
        assert "Trend:" in summary
        assert "Improving" in summary
        assert "Confidence: 85%" in summary

    def test_get_skill_assessment_summary_without_assessment(self, pause_menu):
        """Test getting skill assessment summary without assessment"""
        summary = pause_menu.get_skill_assessment_summary()
        assert "No skill assessment available" in summary

    def test_skill_assessment_trend_improving(self, pause_menu):
        """Test skill assessment with improving trend"""
        assessment = SkillAssessment(
            skill_level=75,
            trend='improving',
            confidence=0.85,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment)
        summary = pause_menu.get_skill_assessment_summary()

        assert "Improving" in summary

    def test_skill_assessment_trend_declining(self, pause_menu):
        """Test skill assessment with declining trend"""
        assessment = SkillAssessment(
            skill_level=50,
            trend='declining',
            confidence=0.70,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment)
        summary = pause_menu.get_skill_assessment_summary()

        assert "Declining" in summary

    def test_skill_assessment_trend_stable(self, pause_menu):
        """Test skill assessment with stable trend"""
        assessment = SkillAssessment(
            skill_level=60,
            trend='stable',
            confidence=0.75,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment)
        summary = pause_menu.get_skill_assessment_summary()

        assert "Stable" in summary

    def test_skill_assessment_confidence_formatting(self, pause_menu):
        """Test confidence percentage formatting"""
        assessment = SkillAssessment(
            skill_level=80,
            trend='improving',
            confidence=0.95,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment)
        summary = pause_menu.get_skill_assessment_summary()

        assert "Confidence: 95%" in summary

    # Full Display Tests
    def test_full_pause_display_with_all_data(self, pause_menu, sample_metrics, sample_assessment):
        """Test full pause display with all data"""
        pause_menu.set_performance_metrics(sample_metrics)
        pause_menu.set_skill_assessment(sample_assessment)
        display = pause_menu.get_full_pause_display()

        assert "GAME PAUSED" in display
        assert "PERFORMANCE SUMMARY" in display
        assert "SKILL ASSESSMENT" in display
        assert "Press SPACE to resume" in display

    def test_full_pause_display_with_partial_data(self, pause_menu, sample_metrics):
        """Test full pause display with only metrics"""
        pause_menu.set_performance_metrics(sample_metrics)
        display = pause_menu.get_full_pause_display()

        assert "GAME PAUSED" in display
        assert "PERFORMANCE SUMMARY" in display
        assert "No skill assessment available" in display

    def test_full_pause_display_with_no_data(self, pause_menu):
        """Test full pause display with no data"""
        display = pause_menu.get_full_pause_display()

        assert "GAME PAUSED" in display
        assert "No performance data available" in display
        assert "No skill assessment available" in display

    # Individual Display Tests
    def test_pause_header(self, pause_menu):
        """Test pause header display"""
        header = pause_menu.get_pause_header()
        assert "GAME PAUSED" in header
        assert "SPACE" in header

    def test_metrics_display(self, pause_menu, sample_metrics):
        """Test metrics display"""
        pause_menu.set_performance_metrics(sample_metrics)
        display = pause_menu.get_metrics_display()

        assert "PERFORMANCE SUMMARY" in display
        assert "Survival Time:" in display

    def test_assessment_display(self, pause_menu, sample_assessment):
        """Test assessment display"""
        pause_menu.set_skill_assessment(sample_assessment)
        display = pause_menu.get_assessment_display()

        assert "SKILL ASSESSMENT" in display
        assert "Skill Level:" in display

    # Clear Data Tests
    def test_clear_data(self, pause_menu, sample_metrics, sample_assessment):
        """Test clearing stored data"""
        pause_menu.set_performance_metrics(sample_metrics)
        pause_menu.set_skill_assessment(sample_assessment)

        assert pause_menu.has_metrics()
        assert pause_menu.has_assessment()

        pause_menu.clear_data()

        assert not pause_menu.has_metrics()
        assert not pause_menu.has_assessment()

    # Edge Cases Tests
    def test_pause_menu_with_zero_metrics(self, pause_menu):
        """Test pause menu with zero values in metrics"""
        metrics = PerformanceMetrics(
            survival_time=0,
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0,
            timestamp=0
        )
        pause_menu.set_performance_metrics(metrics)
        summary = pause_menu.get_performance_summary()

        assert "Survival Time: 0m 0s" in summary
        assert "Food Consumed: 0" in summary

    def test_pause_menu_with_high_metrics(self, pause_menu):
        """Test pause menu with high metric values"""
        metrics = PerformanceMetrics(
            survival_time=3599,  # 59m 59s
            food_consumed=100,
            reaction_time=[500] * 50,
            collisions_avoided=50,
            average_speed=10.0,
            timestamp=0
        )
        pause_menu.set_performance_metrics(metrics)
        summary = pause_menu.get_performance_summary()

        assert "59m 59s" in summary
        assert "Food Consumed: 100" in summary
        assert "Average Reaction Time: 500ms" in summary

    def test_pause_menu_with_extreme_skill_levels(self, pause_menu):
        """Test pause menu with extreme skill levels"""
        # Very low skill
        assessment_low = SkillAssessment(
            skill_level=1,
            trend='declining',
            confidence=0.1,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment_low)
        summary = pause_menu.get_skill_assessment_summary()
        assert "Skill Level: 1/100" in summary
        assert "Confidence: 10%" in summary

        # Very high skill
        assessment_high = SkillAssessment(
            skill_level=100,
            trend='improving',
            confidence=0.99,
            last_updated=0
        )
        pause_menu.set_skill_assessment(assessment_high)
        summary = pause_menu.get_skill_assessment_summary()
        assert "Skill Level: 100/100" in summary
        assert "Confidence: 99%" in summary

    def test_pause_state_independent_of_data(self, pause_menu, sample_metrics):
        """Test that pause state is independent of data"""
        pause_menu.set_performance_metrics(sample_metrics)
        pause_menu.pause()

        assert pause_menu.is_game_paused()
        assert pause_menu.has_metrics()

        pause_menu.clear_data()

        assert pause_menu.is_game_paused()
        assert not pause_menu.has_metrics()

    def test_multiple_data_updates(self, pause_menu):
        """Test updating metrics and assessment multiple times"""
        metrics1 = PerformanceMetrics(
            survival_time=100, food_consumed=5, reaction_time=[100],
            collisions_avoided=0, average_speed=1.0, timestamp=0
        )
        pause_menu.set_performance_metrics(metrics1)
        summary1 = pause_menu.get_performance_summary()

        metrics2 = PerformanceMetrics(
            survival_time=200, food_consumed=10, reaction_time=[150],
            collisions_avoided=1, average_speed=2.0, timestamp=0
        )
        pause_menu.set_performance_metrics(metrics2)
        summary2 = pause_menu.get_performance_summary()

        assert summary1 != summary2
        assert "Food Consumed: 10" in summary2
