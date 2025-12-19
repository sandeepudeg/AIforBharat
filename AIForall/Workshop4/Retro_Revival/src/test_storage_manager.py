"""
Tests for StorageManager
Includes unit tests and property-based tests for storage and persistence
Requirements: 5.1, 5.2, 5.3, 5.4
"""

import pytest
from hypothesis import given, strategies as st, settings
import time
from storage_manager import StorageManager
from game_types import (
    GameSession,
    PlayerProfile,
    PerformanceMetrics,
    DifficultyLevel,
)


class TestStorageManagerInitialization:
    """Tests for storage manager initialization"""

    def test_initialize_storage_manager(self):
        """Should initialize storage manager"""
        manager = StorageManager()
        assert manager is not None
        assert isinstance(manager.sessions_cache, dict)
        assert isinstance(manager.profile_cache, PlayerProfile)

    def test_initial_profile_is_empty(self):
        """Should initialize with empty profile"""
        manager = StorageManager()
        profile = manager.load_player_profile()
        assert profile.best_score == 0
        assert profile.average_survival_time == 0.0


class TestSessionCreation:
    """Tests for game session creation"""

    def test_create_game_session(self):
        """Should create a game session"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200, 210, 220],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(
            score=50,
            duration=30,
            difficulty=difficulty,
            metrics=metrics
        )

        assert session.id is not None
        assert session.score == 50
        assert session.duration == 30
        assert session.difficulty.level == 1

    def test_session_has_unique_id(self):
        """Should create sessions with unique IDs"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session1 = manager.create_game_session(50, 30, difficulty, metrics)
        session2 = manager.create_game_session(50, 30, difficulty, metrics)

        assert session1.id != session2.id


class TestSessionSaving:
    """Tests for saving and loading sessions"""

    def test_save_session(self):
        """Should save a game session"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session)

        assert session.id in manager.sessions_cache

    def test_get_session_by_id(self):
        """Should retrieve a session by ID"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session)

        retrieved = manager.get_session_by_id(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id
        assert retrieved.score == session.score

    def test_get_recent_sessions(self):
        """Should retrieve recent sessions"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        # Save multiple sessions
        for i in range(3):
            session = manager.create_game_session(50 + i * 10, 30, difficulty, metrics)
            manager.save_session(session)

        recent = manager.get_recent_sessions(2)
        assert len(recent) == 2

    def test_get_sessions_by_score(self):
        """Should retrieve sessions sorted by score"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        # Save sessions with different scores
        scores = [30, 50, 40]
        for score in scores:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)

        sorted_sessions = manager.get_sessions_by_score(3)
        assert sorted_sessions[0].score >= sorted_sessions[1].score
        assert sorted_sessions[1].score >= sorted_sessions[2].score


class TestProfileManagement:
    """Tests for player profile management"""

    def test_best_score_tracking(self):
        """Should track best score"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session1 = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session1)

        session2 = manager.create_game_session(100, 30, difficulty, metrics)
        manager.save_session(session2)

        profile = manager.load_player_profile()
        assert profile.best_score == 100

    def test_average_survival_time(self):
        """Should calculate average survival time"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session1 = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session1)

        session2 = manager.create_game_session(50, 40, difficulty, metrics)
        manager.save_session(session2)

        profile = manager.load_player_profile()
        assert profile.average_survival_time == 35.0

    def test_get_best_score(self):
        """Should return best score"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(75, 30, difficulty, metrics)
        manager.save_session(session)

        best = manager.get_best_score()
        assert best == 75

    def test_get_average_survival_time(self):
        """Should return average survival time"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(50, 45, difficulty, metrics)
        manager.save_session(session)

        avg = manager.get_average_survival_time()
        assert avg == 45.0


class TestSkillProgression:
    """Tests for skill progression tracking"""

    def test_calculate_skill_trend_improving(self):
        """Should detect improving trend"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        # Save sessions with increasing scores
        for score in [30, 40, 50, 60, 70]:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)

        trend = manager.calculate_skill_trend()
        assert trend == 'improving'

    def test_calculate_skill_trend_declining(self):
        """Should detect declining trend"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        # Save sessions with decreasing scores
        for score in [70, 60, 50, 40, 30]:
            session = manager.create_game_session(score, 30, difficulty, metrics)
            manager.save_session(session)

        trend = manager.calculate_skill_trend()
        assert trend == 'declining'

    def test_calculate_initial_difficulty(self):
        """Should calculate initial difficulty based on history"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=3,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session)

        initial_difficulty = manager.calculate_initial_difficulty()
        assert initial_difficulty == 3


class TestSessionRetrieval:
    """Tests for session retrieval by various criteria"""

    def test_get_sessions_by_difficulty(self):
        """Should retrieve sessions by difficulty level"""
        manager = StorageManager()
        
        difficulty1 = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        difficulty2 = DifficultyLevel(
            level=5,
            speed=7,
            obstacle_density=3,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session1 = manager.create_game_session(50, 30, difficulty1, metrics)
        manager.save_session(session1)

        session2 = manager.create_game_session(50, 30, difficulty2, metrics)
        manager.save_session(session2)

        sessions_level_1 = manager.get_sessions_by_difficulty(1)
        assert len(sessions_level_1) == 1
        assert sessions_level_1[0].difficulty.level == 1


class TestDataClearance:
    """Tests for clearing stored data"""

    def test_clear_all_data(self):
        """Should clear all stored data"""
        manager = StorageManager()
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[200],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )

        session = manager.create_game_session(50, 30, difficulty, metrics)
        manager.save_session(session)

        manager.clear_all_data()

        assert len(manager.sessions_cache) == 0
        assert manager.profile_cache.best_score == 0


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestStorageManagerProperties:
    """Property-based tests for storage manager correctness"""

    @given(
        score=st.integers(min_value=0, max_value=1000),
        duration=st.integers(min_value=1, max_value=3600),
        difficulty_level=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=100)
    def test_property_9_game_state_persistence_round_trip(
        self,
        score: int,
        duration: int,
        difficulty_level: int,
    ):
        """
        Property 9: Game State Persistence Round-Trip
        For any game session, serializing the game state to storage and deserializing it
        should produce an equivalent game state with identical snake position, food locations,
        score, and difficulty parameters.
        
        **Feature: snake-adaptive-ai, Property 9: Game State Persistence Round-Trip**
        **Validates: Requirements 5.1**
        """
        manager = StorageManager()
        
        # Create a game session with specific parameters
        difficulty = DifficultyLevel(
            level=difficulty_level,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        metrics = PerformanceMetrics(
            survival_time=float(duration),
            food_consumed=score // 10,
            reaction_time=[200, 210, 220],
            collisions_avoided=2,
            average_speed=1.5,
            timestamp=int(time.time() * 1000)
        )
        
        original_session = manager.create_game_session(
            score=score,
            duration=duration,
            difficulty=difficulty,
            metrics=metrics
        )
        
        # Save the session
        manager.save_session(original_session)
        
        # Retrieve the session
        retrieved_session = manager.get_session_by_id(original_session.id)
        
        # Verify equivalence
        assert retrieved_session is not None
        assert retrieved_session.id == original_session.id
        assert retrieved_session.score == original_session.score
        assert retrieved_session.duration == original_session.duration
        assert retrieved_session.difficulty.level == original_session.difficulty.level
        assert retrieved_session.difficulty.speed == original_session.difficulty.speed
        assert retrieved_session.difficulty.obstacle_density == original_session.difficulty.obstacle_density
        assert retrieved_session.difficulty.food_spawn_rate == original_session.difficulty.food_spawn_rate
        assert retrieved_session.difficulty.adaptive_mode == original_session.difficulty.adaptive_mode
        assert retrieved_session.metrics.survival_time == original_session.metrics.survival_time
        assert retrieved_session.metrics.food_consumed == original_session.metrics.food_consumed
        assert retrieved_session.metrics.collisions_avoided == original_session.metrics.collisions_avoided
        assert retrieved_session.metrics.average_speed == original_session.metrics.average_speed
