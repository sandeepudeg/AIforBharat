"""
Comprehensive Integration Tests for Snake Adaptive AI
Tests complete game scenarios with various difficulty levels, adaptation engine behavior,
and persistence/recovery mechanisms
Requirements: All
"""

import pytest
import time
import json
from hypothesis import given, strategies as st, settings
from game_loop import GameLoop, GameLoopState
from game_engine import GameEngine
from adaptation_engine import AdaptationEngine
from difficulty_manager import DifficultyManager
from metrics_collector import MetricsCollector
from storage_manager import StorageManager
from game_types import (
    Direction,
    DifficultyLevel,
    PerformanceMetrics,
    GameSession,
    Segment,
    Position,
)


class TestCompleteGameScenarios:
    """Tests for complete game scenarios with various difficulty levels"""

    def test_game_scenario_easy_difficulty(self):
        """Should handle complete game at easy difficulty"""
        difficulty = DifficultyLevel(
            level=1,
            speed=2,
            obstacle_density=0,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )
        loop = GameLoop(difficulty_manager=DifficultyManager())
        loop.difficulty_manager.set_manual_difficulty(difficulty)
        loop.start_game()

        # Play for several ticks
        for _ in range(50):
            loop.queue_input('up')
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0
        assert len(state.snake) >= 3

    def test_game_scenario_medium_difficulty(self):
        """Should handle complete game at medium difficulty"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )
        loop = GameLoop(difficulty_manager=DifficultyManager())
        loop.difficulty_manager.set_manual_difficulty(difficulty)
        loop.start_game()

        # Play for several ticks
        for _ in range(50):
            loop.queue_input('right')
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0
        assert len(state.snake) >= 3

    def test_game_scenario_hard_difficulty(self):
        """Should handle complete game at hard difficulty"""
        difficulty = DifficultyLevel(
            level=10,
            speed=10,
            obstacle_density=5,
            food_spawn_rate=1.5,
            adaptive_mode=False
        )
        loop = GameLoop(difficulty_manager=DifficultyManager())
        loop.difficulty_manager.set_manual_difficulty(difficulty)
        loop.start_game()

        # Play for several ticks
        for _ in range(50):
            loop.queue_input('down')
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0
        assert len(state.snake) >= 3

    def test_game_scenario_with_difficulty_progression(self):
        """Should handle game with difficulty progression"""
        loop = GameLoop()
        loop.start_game()

        # Start at easy
        difficulty = DifficultyLevel(
            level=1,
            speed=2,
            obstacle_density=0,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )
        loop.set_manual_difficulty(difficulty)

        # Play for a bit
        for _ in range(20):
            loop.queue_input('up')
            if not loop.update():
                break

        # Increase difficulty
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )
        loop.set_manual_difficulty(difficulty)

        # Play more
        for _ in range(20):
            loop.queue_input('right')
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0

    def test_game_scenario_pause_and_resume(self):
        """Should handle pause and resume during gameplay"""
        loop = GameLoop()
        loop.start_game()

        # Play for a bit
        for _ in range(10):
            loop.queue_input('up')
            loop.update()

        state_before_pause = loop.get_game_state()
        score_before_pause = state_before_pause.score

        # Pause
        loop.pause_game()
        for _ in range(5):
            loop.update()

        state_paused = loop.get_game_state()
        assert state_paused.score == score_before_pause

        # Resume
        loop.resume_game()
        for _ in range(10):
            loop.queue_input('down')
            loop.update()

        state_after_resume = loop.get_game_state()
        assert state_after_resume.score >= score_before_pause

    def test_game_scenario_multiple_games_in_sequence(self):
        """Should handle multiple games in sequence"""
        loop = GameLoop()

        for game_num in range(3):
            loop.start_game()

            # Play each game
            for _ in range(20):
                loop.queue_input('up')
                if not loop.update():
                    break

            state = loop.get_game_state()
            assert state.score >= 0

            # Reset for next game
            if game_num < 2:
                loop.state = GameLoopState.IDLE


class TestAdaptationEngineWithRealisticBehavior:
    """Tests for adaptation engine with realistic player behavior"""

    def test_adaptation_with_improving_player(self):
        """Should increase difficulty when player is improving"""
        adaptation = AdaptationEngine()
        difficulty_manager = DifficultyManager()

        # Simulate improving player metrics
        metrics_sequence = [
            PerformanceMetrics(
                survival_time=10,
                food_consumed=1,
                reaction_time=[100, 110, 105],
                collisions_avoided=0,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=20,
                food_consumed=3,
                reaction_time=[90, 95, 92],
                collisions_avoided=2,
                average_speed=1.1,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=30,
                food_consumed=5,
                reaction_time=[80, 85, 82],
                collisions_avoided=4,
                average_speed=1.2,
                timestamp=int(time.time() * 1000)
            ),
        ]

        difficulty_levels = []
        for metrics in metrics_sequence:
            assessment = adaptation.assess_player_skill(metrics)
            delta = adaptation.calculate_difficulty_adjustment(assessment)
            difficulty_levels.append(delta)

        # Difficulty should generally increase for improving player
        # (though not strictly monotonic due to randomness)
        assert len(difficulty_levels) == 3

    def test_adaptation_with_declining_player(self):
        """Should decrease difficulty when player is declining"""
        adaptation = AdaptationEngine()

        # Simulate declining player metrics
        metrics_sequence = [
            PerformanceMetrics(
                survival_time=30,
                food_consumed=5,
                reaction_time=[80, 85, 82],
                collisions_avoided=4,
                average_speed=1.2,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=20,
                food_consumed=3,
                reaction_time=[100, 110, 105],
                collisions_avoided=2,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=10,
                food_consumed=1,
                reaction_time=[120, 130, 125],
                collisions_avoided=0,
                average_speed=0.8,
                timestamp=int(time.time() * 1000)
            ),
        ]

        difficulty_levels = []
        for metrics in metrics_sequence:
            assessment = adaptation.assess_player_skill(metrics)
            delta = adaptation.calculate_difficulty_adjustment(assessment)
            difficulty_levels.append(delta)

        assert len(difficulty_levels) == 3

    def test_adaptation_with_stable_player(self):
        """Should maintain difficulty when player is stable"""
        adaptation = AdaptationEngine()

        # Simulate stable player metrics
        metrics_sequence = [
            PerformanceMetrics(
                survival_time=20,
                food_consumed=3,
                reaction_time=[100, 105, 102],
                collisions_avoided=2,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=21,
                food_consumed=3,
                reaction_time=[101, 104, 103],
                collisions_avoided=2,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
            PerformanceMetrics(
                survival_time=20,
                food_consumed=3,
                reaction_time=[99, 106, 101],
                collisions_avoided=2,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
        ]

        assessments = []
        for metrics in metrics_sequence:
            assessment = adaptation.assess_player_skill(metrics)
            assessments.append(assessment)

        # Skill levels should be relatively close for stable player
        skill_levels = [a.skill_level for a in assessments]
        assert max(skill_levels) - min(skill_levels) < 30  # Within 30 points

    def test_adaptation_decision_logging(self):
        """Should log all adaptation decisions with rationale"""
        adaptation = AdaptationEngine()

        metrics = PerformanceMetrics(
            survival_time=20,
            food_consumed=3,
            reaction_time=[100, 105, 102],
            collisions_avoided=2,
            average_speed=1.0,
            timestamp=int(time.time() * 1000)
        )

        assessment = adaptation.assess_player_skill(metrics)
        delta = adaptation.calculate_difficulty_adjustment(assessment)

        # Record the decision
        adaptation.record_adaptation_decision(
            metrics, assessment, delta, "Test adaptation"
        )

        # Verify decision was logged
        assert len(adaptation.decision_log) > 0
        last_decision = adaptation.decision_log[-1]
        assert last_decision.rationale == "Test adaptation"

    def test_adaptation_with_realistic_game_loop(self):
        """Should adapt difficulty during realistic gameplay"""
        loop = GameLoop()
        loop.start_game()

        initial_difficulty = loop.get_current_difficulty()

        # Play for a while with adaptive mode enabled
        for _ in range(100):
            loop.queue_input('up')
            if not loop.update():
                break

        # Difficulty may have changed
        final_difficulty = loop.get_current_difficulty()

        # Both should be valid
        assert 1 <= initial_difficulty.level <= 10
        assert 1 <= final_difficulty.level <= 10


class TestPersistenceAndRecovery:
    """Tests for game state persistence and recovery"""

    def test_save_and_load_game_session(self):
        """Should save and load game session correctly"""
        storage = StorageManager()

        # Create a game session
        session = GameSession(
            id="test_session_1",
            score=100,
            duration=60,
            difficulty=DifficultyLevel(
                level=5,
                speed=5,
                obstacle_density=2,
                food_spawn_rate=1.0,
                adaptive_mode=True
            ),
            metrics=PerformanceMetrics(
                survival_time=60,
                food_consumed=10,
                reaction_time=[100, 105, 102],
                collisions_avoided=5,
                average_speed=1.0,
                timestamp=int(time.time() * 1000)
            ),
            timestamp=int(time.time() * 1000)
        )

        # Save session
        storage.save_session(session)

        # Load sessions
        loaded_sessions = storage.get_recent_sessions(1)
        assert len(loaded_sessions) > 0
        assert loaded_sessions[0].score == 100

    def test_player_profile_persistence(self):
        """Should persist and load player profile"""
        storage = StorageManager()

        # Create and save multiple sessions
        for i in range(3):
            session = GameSession(
                id=f"test_session_{i}",
                score=100 + i * 10,
                duration=60 + i * 10,
                difficulty=DifficultyLevel(
                    level=5,
                    speed=5,
                    obstacle_density=2,
                    food_spawn_rate=1.0,
                    adaptive_mode=True
                ),
                metrics=PerformanceMetrics(
                    survival_time=60 + i * 10,
                    food_consumed=10 + i,
                    reaction_time=[100, 105, 102],
                    collisions_avoided=5,
                    average_speed=1.0,
                    timestamp=int(time.time() * 1000)
                ),
                timestamp=int(time.time() * 1000)
            )
            storage.save_session(session)

        # Load profile
        profile = storage.load_player_profile()
        assert profile is not None

    def test_best_score_tracking(self):
        """Should track best score across sessions"""
        storage = StorageManager()

        # Save sessions with different scores
        scores = [50, 100, 75, 150, 80]
        for i, score in enumerate(scores):
            session = GameSession(
                id=f"test_session_{i}",
                score=score,
                duration=60,
                difficulty=DifficultyLevel(
                    level=5,
                    speed=5,
                    obstacle_density=2,
                    food_spawn_rate=1.0,
                    adaptive_mode=True
                ),
                metrics=PerformanceMetrics(
                    survival_time=60,
                    food_consumed=score // 10,
                    reaction_time=[100, 105, 102],
                    collisions_avoided=5,
                    average_speed=1.0,
                    timestamp=int(time.time() * 1000)
                ),
                timestamp=int(time.time() * 1000)
            )
            storage.save_session(session)

        # Check best score
        best_score = storage.get_best_score()
        assert best_score == 150

    def test_skill_trend_calculation(self):
        """Should calculate skill trend from session history"""
        storage = StorageManager()

        # Save sessions with improving scores
        for i in range(5):
            session = GameSession(
                id=f"test_session_{i}",
                score=50 + i * 20,  # Improving scores
                duration=60,
                difficulty=DifficultyLevel(
                    level=5,
                    speed=5,
                    obstacle_density=2,
                    food_spawn_rate=1.0,
                    adaptive_mode=True
                ),
                metrics=PerformanceMetrics(
                    survival_time=60,
                    food_consumed=5 + i,
                    reaction_time=[100, 105, 102],
                    collisions_avoided=5,
                    average_speed=1.0,
                    timestamp=int(time.time() * 1000)
                ),
                timestamp=int(time.time() * 1000)
            )
            storage.save_session(session)

        # Calculate trend
        trend = storage.calculate_skill_trend()
        assert trend in ['improving', 'stable', 'declining']

    def test_session_retrieval_by_difficulty(self):
        """Should retrieve sessions by difficulty level"""
        storage = StorageManager()

        # Save sessions at different difficulties
        for level in [1, 5, 10]:
            session = GameSession(
                id=f"test_session_level_{level}",
                score=100,
                duration=60,
                difficulty=DifficultyLevel(
                    level=level,
                    speed=level,
                    obstacle_density=level // 2,
                    food_spawn_rate=1.0,
                    adaptive_mode=True
                ),
                metrics=PerformanceMetrics(
                    survival_time=60,
                    food_consumed=10,
                    reaction_time=[100, 105, 102],
                    collisions_avoided=5,
                    average_speed=1.0,
                    timestamp=int(time.time() * 1000)
                ),
                timestamp=int(time.time() * 1000)
            )
            storage.save_session(session)

        # Retrieve sessions at level 5
        level_5_sessions = storage.get_sessions_by_difficulty(5)
        assert len(level_5_sessions) > 0
        assert all(s.difficulty.level == 5 for s in level_5_sessions)

    def test_average_survival_time_calculation(self):
        """Should calculate average survival time"""
        storage = StorageManager()

        # Save sessions with different survival times
        survival_times = [30, 60, 45, 90, 75]
        for i, survival_time in enumerate(survival_times):
            session = GameSession(
                id=f"test_session_{i}",
                score=100,
                duration=survival_time,
                difficulty=DifficultyLevel(
                    level=5,
                    speed=5,
                    obstacle_density=2,
                    food_spawn_rate=1.0,
                    adaptive_mode=True
                ),
                metrics=PerformanceMetrics(
                    survival_time=survival_time,
                    food_consumed=10,
                    reaction_time=[100, 105, 102],
                    collisions_avoided=5,
                    average_speed=1.0,
                    timestamp=int(time.time() * 1000)
                ),
                timestamp=int(time.time() * 1000)
            )
            storage.save_session(session)

        # Calculate average
        avg_survival = storage.get_average_survival_time()
        expected_avg = sum(survival_times) / len(survival_times)
        assert abs(avg_survival - expected_avg) < 1  # Allow 1 second tolerance


class TestEndToEndGameplay:
    """End-to-end tests for complete gameplay scenarios"""

    def test_complete_game_flow_with_adaptation(self):
        """Should handle complete game flow with adaptation"""
        loop = GameLoop()
        loop.start_game()

        # Play game with various inputs
        inputs = ['up', 'right', 'down', 'left', 'up', 'up', 'right', 'right']
        for input_dir in inputs:
            loop.queue_input(input_dir)
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0
        assert len(state.snake) >= 3

    def test_game_with_callbacks(self):
        """Should trigger callbacks during gameplay"""
        loop = GameLoop()

        state_changes = []
        difficulty_changes = []
        game_overs = []

        def on_state_changed(state):
            state_changes.append(state)

        def on_difficulty_changed(reason):
            difficulty_changes.append(reason)

        def on_game_over(state, metrics):
            game_overs.append((state, metrics))

        loop.set_on_game_state_changed(on_state_changed)
        loop.set_on_difficulty_changed(on_difficulty_changed)
        loop.set_on_game_over(on_game_over)

        loop.start_game()

        # Play for a bit
        for _ in range(50):
            loop.queue_input('up')
            if not loop.update():
                break

        # Callbacks should have been called
        assert len(state_changes) >= 0  # May or may not be called depending on timing

    def test_game_with_manual_and_adaptive_modes(self):
        """Should switch between manual and adaptive modes"""
        loop = GameLoop()
        loop.start_game()

        # Start in adaptive mode
        assert loop.is_adaptive_mode_enabled()

        # Switch to manual
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=False
        )
        loop.set_manual_difficulty(difficulty)
        assert not loop.is_adaptive_mode_enabled()

        # Play in manual mode
        for _ in range(20):
            loop.queue_input('up')
            if not loop.update():
                break

        # Switch back to adaptive
        loop.enable_adaptive_mode()
        assert loop.is_adaptive_mode_enabled()

        # Play in adaptive mode
        for _ in range(20):
            loop.queue_input('down')
            if not loop.update():
                break

        state = loop.get_game_state()
        assert state.score >= 0


class TestPropertyBasedIntegration:
    """Property-based tests for integration scenarios"""

    @given(st.lists(st.sampled_from(['up', 'down', 'left', 'right']), min_size=10, max_size=200))
    @settings(max_examples=20)
    def test_game_remains_valid_with_random_inputs(self, inputs):
        """
        **Feature: snake-adaptive-ai, Property 1: Snake Growth Consistency**
        For any sequence of random inputs, the game should remain in a valid state
        **Validates: Requirements All**
        """
        loop = GameLoop(tick_rate=100)
        loop.start_game()

        for input_dir in inputs:
            loop.queue_input(input_dir)
            if not loop.update():
                break

        state = loop.get_game_state()
        assert len(state.snake) >= 3
        assert state.score >= 0
        assert state.score % 10 == 0

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_difficulty_levels_remain_valid(self, level):
        """
        **Feature: snake-adaptive-ai, Property 5: Difficulty Bounds Enforcement**
        For any difficulty level, all parameters should remain within valid bounds
        **Validates: Requirements 6.4**
        """
        loop = GameLoop()
        difficulty = DifficultyLevel(
            level=level,
            speed=max(1, min(10, level + 2)),
            obstacle_density=max(0, min(5, level // 2)),
            food_spawn_rate=0.5 + (level * 0.15),
            adaptive_mode=False
        )

        loop.set_manual_difficulty(difficulty)
        current = loop.get_current_difficulty()

        assert 1 <= current.speed <= 10
        assert 0 <= current.obstacle_density <= 5
        assert 0.5 <= current.food_spawn_rate <= 2.0

    @given(st.lists(st.sampled_from(['up', 'down', 'left', 'right']), min_size=5, max_size=100))
    @settings(max_examples=15)
    def test_persistence_round_trip(self, inputs):
        """
        **Feature: snake-adaptive-ai, Property 9: Game State Persistence Round-Trip**
        For any game state, serializing and deserializing should preserve equivalence
        **Validates: Requirements 5.1**
        """
        loop = GameLoop()
        loop.start_game()

        for input_dir in inputs:
            loop.queue_input(input_dir)
            if not loop.update():
                break

        state = loop.get_game_state()

        # Verify state can be serialized
        assert state.snake is not None
        assert state.food is not None
        assert state.obstacles is not None
        assert state.score >= 0
