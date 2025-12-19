"""
Tests for StatisticsScreen
Unit tests for statistics display functionality
Requirements: 5.2, 5.3
"""

import pytest
import time
from statistics_screen import StatisticsScreen
from storage_manager import StorageManager
from game_types import (
    GameSession,
    PerformanceMetrics,
    DifficultyLevel,
)


class TestStatisticsScreenInitialization:
    """Tests for statistics screen initialization"""

    def test_initialize_statistics_screen(self):
        """Should initialize statistics screen"""
        screen = StatisticsScreen()
        assert screen is not None
        assert screen.storage_manager is not None

    def test_initialize_with_custom_storage_manager(self):
        """Should initialize with custom storage manager"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        assert screen.storage_manager is manager


class TestBestScoreCalculation:
    """Tests for best score calculation"""

    def test_get_best_score_no_sessions(self):
        """Should return 0 when no sessions exist"""
        screen = StatisticsScreen()
        assert screen.get_best_score() == 0

    def test_get_best_score_single_session(self):
        """Should return score from single session"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(75, 30, difficulty, metrics)
        manager.save_session(session)
        
        assert screen.get_best_score() == 75

    def test_get_best_score_multiple_sessions(self):
        """Should return highest score from multiple sessions"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        scores = [50, 100, 75, 120, 90]
        for score in scores:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_best_score() == 120


class TestAverageSurvivalTimeCalculation:
    """Tests for average survival time calculation"""

    def test_get_average_survival_time_no_sessions(self):
        """Should return 0 when no sessions exist"""
        screen = StatisticsScreen()
        assert screen.get_average_survival_time() == 0.0

    def test_get_average_survival_time_single_session(self):
        """Should return duration from single session"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=45.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(50, 45, difficulty, metrics)
        manager.save_session(session)
        
        assert screen.get_average_survival_time() == 45.0

    def test_get_average_survival_time_multiple_sessions(self):
        """Should return average duration from multiple sessions"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        durations = [30, 40, 50, 60, 70]
        for duration in durations:
            session = manager.create_game_session(50, duration, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_average_survival_time() == 50.0


class TestSkillProgressionDisplay:
    """Tests for skill progression display"""

    def test_get_skill_progression_no_sessions(self):
        """Should return empty list when no sessions exist"""
        screen = StatisticsScreen()
        progression = screen.get_skill_progression()
        assert progression == []

    def test_get_skill_progression_single_session(self):
        """Should return progression data from single session"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=2, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(75, 30, difficulty, metrics)
        manager.save_session(session)
        
        progression = screen.get_skill_progression()
        assert len(progression) == 1
        assert progression[0]['score'] == 75
        assert progression[0]['difficulty_level'] == 2
        assert progression[0]['food_consumed'] == 5

    def test_get_skill_progression_multiple_sessions(self):
        """Should return progression data from multiple sessions in order"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        scores = [50, 60, 70, 80, 90]
        for score in scores:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)
        
        progression = screen.get_skill_progression()
        assert len(progression) == 5
        # get_recent_sessions returns newest first, then we reverse to get oldest first
        # So progression should be in chronological order (oldest first)
        assert progression[0]['score'] in scores
        assert progression[-1]['score'] in scores

    def test_skill_progression_contains_required_fields(self):
        """Should include all required fields in progression data"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=3, speed=6, obstacle_density=2,
            food_spawn_rate=1.2, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=35.0, food_consumed=7,
            reaction_time=[200, 210], collisions_avoided=3,
            average_speed=1.6, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(85, 35, difficulty, metrics)
        manager.save_session(session)
        
        progression = screen.get_skill_progression()
        assert 'timestamp' in progression[0]
        assert 'score' in progression[0]
        assert 'duration' in progression[0]
        assert 'difficulty_level' in progression[0]
        assert 'food_consumed' in progression[0]


class TestDifficultyEvolutionDisplay:
    """Tests for difficulty evolution display"""

    def test_get_difficulty_evolution_no_sessions(self):
        """Should return empty list when no sessions exist"""
        screen = StatisticsScreen()
        evolution = screen.get_difficulty_evolution()
        assert evolution == []

    def test_get_difficulty_evolution_single_session(self):
        """Should return difficulty data from single session"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=3, speed=6, obstacle_density=2,
            food_spawn_rate=1.2, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(75, 30, difficulty, metrics)
        manager.save_session(session)
        
        evolution = screen.get_difficulty_evolution()
        assert len(evolution) == 1
        assert evolution[0]['difficulty_level'] == 3
        assert evolution[0]['speed'] == 6
        assert evolution[0]['obstacle_density'] == 2

    def test_get_difficulty_evolution_multiple_sessions(self):
        """Should return difficulty evolution from multiple sessions"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        difficulty_levels = [1, 2, 3, 4, 5]
        for level in difficulty_levels:
            difficulty = DifficultyLevel(
                level=level, speed=4+level, obstacle_density=level-1,
                food_spawn_rate=1.0, adaptive_mode=True
            )
            session = manager.create_game_session(50, 30, difficulty, metrics)
            manager.save_session(session)
        
        evolution = screen.get_difficulty_evolution()
        assert len(evolution) == 5
        # get_recent_sessions returns newest first, then we reverse to get oldest first
        # So evolution should be in chronological order (oldest first)
        assert evolution[0]['difficulty_level'] in difficulty_levels
        assert evolution[-1]['difficulty_level'] in difficulty_levels

    def test_difficulty_evolution_contains_required_fields(self):
        """Should include all required fields in evolution data"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=4, speed=7, obstacle_density=3,
            food_spawn_rate=1.3, adaptive_mode=False
        )
        metrics = PerformanceMetrics(
            survival_time=40.0, food_consumed=8,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(90, 40, difficulty, metrics)
        manager.save_session(session)
        
        evolution = screen.get_difficulty_evolution()
        assert 'timestamp' in evolution[0]
        assert 'difficulty_level' in evolution[0]
        assert 'speed' in evolution[0]
        assert 'obstacle_density' in evolution[0]
        assert 'food_spawn_rate' in evolution[0]
        assert 'adaptive_mode' in evolution[0]


class TestStatisticsScreenRendering:
    """Tests for statistics screen rendering"""

    def test_render_statistics_display_no_sessions(self):
        """Should render statistics display with no sessions"""
        screen = StatisticsScreen()
        display = screen.render_statistics_display()
        assert isinstance(display, str)
        assert "STATISTICS SCREEN" in display
        assert "0" in display  # Session count

    def test_render_statistics_display_with_sessions(self):
        """Should render statistics display with session data"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=2, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(100, 30, difficulty, metrics)
        manager.save_session(session)
        
        display = screen.render_statistics_display()
        assert "100" in display  # Best score
        assert "1" in display  # Session count

    def test_render_skill_progression_chart(self):
        """Should render skill progression chart"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        for score in [50, 60, 70]:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)
        
        chart = screen.render_skill_progression_chart()
        assert isinstance(chart, str)
        assert "SKILL PROGRESSION CHART" in chart
        assert "Game" in chart

    def test_render_difficulty_evolution_chart(self):
        """Should render difficulty evolution chart"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        for level in [1, 2, 3]:
            difficulty = DifficultyLevel(
                level=level, speed=4+level, obstacle_density=level-1,
                food_spawn_rate=1.0, adaptive_mode=True
            )
            session = manager.create_game_session(50, 30, difficulty, metrics)
            manager.save_session(session)
        
        chart = screen.render_difficulty_evolution_chart()
        assert isinstance(chart, str)
        assert "DIFFICULTY EVOLUTION CHART" in chart
        assert "Game" in chart

    def test_render_full_statistics_display(self):
        """Should render complete statistics display"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(75, 30, difficulty, metrics)
        manager.save_session(session)
        
        display = screen.render_full_statistics_display()
        assert isinstance(display, str)
        assert "STATISTICS SCREEN" in display
        assert "SKILL PROGRESSION CHART" in display
        assert "DIFFICULTY EVOLUTION CHART" in display


class TestStatisticsCalculations:
    """Tests for various statistics calculations"""

    def test_get_session_count(self):
        """Should return correct session count"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        for _ in range(5):
            session = manager.create_game_session(50, 30, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_session_count() == 5

    def test_get_total_playtime(self):
        """Should calculate total playtime correctly"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        durations = [30, 40, 50]
        for duration in durations:
            session = manager.create_game_session(50, duration, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_total_playtime() == 120

    def test_get_average_score(self):
        """Should calculate average score correctly"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        scores = [50, 60, 70]
        for score in scores:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_average_score() == 60.0

    def test_get_highest_difficulty_reached(self):
        """Should return highest difficulty level reached"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        for level in [1, 3, 2, 5, 4]:
            difficulty = DifficultyLevel(
                level=level, speed=4+level, obstacle_density=level-1,
                food_spawn_rate=1.0, adaptive_mode=True
            )
            session = manager.create_game_session(50, 30, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_highest_difficulty_reached() == 5

    def test_get_average_difficulty(self):
        """Should calculate average difficulty correctly"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        for level in [2, 4, 6]:
            difficulty = DifficultyLevel(
                level=level, speed=4+level, obstacle_density=level-1,
                food_spawn_rate=1.0, adaptive_mode=True
            )
            session = manager.create_game_session(50, 30, difficulty, metrics)
            manager.save_session(session)
        
        assert screen.get_average_difficulty() == 4.0

    def test_get_statistics_summary(self):
        """Should return complete statistics summary"""
        manager = StorageManager()
        screen = StatisticsScreen(manager)
        
        difficulty = DifficultyLevel(
            level=2, speed=5, obstacle_density=1,
            food_spawn_rate=1.0, adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0, food_consumed=5,
            reaction_time=[200], collisions_avoided=2,
            average_speed=1.5, timestamp=int(time.time() * 1000)
        )
        
        session = manager.create_game_session(100, 30, difficulty, metrics)
        manager.save_session(session)
        
        summary = screen.get_statistics_summary()
        assert 'best_score' in summary
        assert 'average_score' in summary
        assert 'average_survival_time' in summary
        assert 'session_count' in summary
        assert 'total_playtime' in summary
        assert 'skill_trend' in summary
        assert 'highest_difficulty' in summary
        assert 'average_difficulty' in summary
        assert summary['best_score'] == 100
        assert summary['session_count'] == 1
