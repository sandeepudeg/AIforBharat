"""
Unit tests for type definitions and interface validation
Requirements: 1.1
"""

import pytest
from game_types import (
    Segment,
    Position,
    Obstacle,
    Direction,
    DifficultyLevel,
    GameState,
    PerformanceMetrics,
    SkillAssessment,
    DifficultyDelta,
    AdaptationDecision,
    GameSession,
    PlayerProfile,
    CollisionResult,
)
import time


class TestSegment:
    """Tests for Segment type"""

    def test_instantiate_valid_segment(self):
        """Should instantiate a valid segment"""
        segment = Segment(x=10, y=10)
        assert segment.x == 10
        assert segment.y == 10

    def test_allow_zero_coordinates(self):
        """Should allow zero coordinates"""
        segment = Segment(x=0, y=0)
        assert segment.x == 0
        assert segment.y == 0


class TestPosition:
    """Tests for Position type"""

    def test_instantiate_valid_position(self):
        """Should instantiate a valid position"""
        position = Position(x=5, y=15)
        assert position.x == 5
        assert position.y == 15


class TestObstacle:
    """Tests for Obstacle type"""

    def test_instantiate_static_obstacle(self):
        """Should instantiate a static obstacle"""
        obstacle = Obstacle(x=8, y=8, type='static')
        assert obstacle.x == 8
        assert obstacle.y == 8
        assert obstacle.type == 'static'

    def test_instantiate_dynamic_obstacle(self):
        """Should instantiate a dynamic obstacle"""
        obstacle = Obstacle(x=12, y=12, type='dynamic')
        assert obstacle.type == 'dynamic'


class TestDirection:
    """Tests for Direction type"""

    def test_accept_all_valid_directions(self):
        """Should accept all valid directions"""
        directions = ['up', 'down', 'left', 'right']
        for direction in directions:
            assert direction in ['up', 'down', 'left', 'right']


class TestDifficultyLevel:
    """Tests for DifficultyLevel type"""

    def test_instantiate_valid_difficulty_level(self):
        """Should instantiate a valid difficulty level"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        assert difficulty.level == 5
        assert difficulty.speed == 5
        assert difficulty.obstacle_density == 2
        assert difficulty.food_spawn_rate == 1.0
        assert difficulty.adaptive_mode is True

    def test_instantiate_difficulty_with_minimum_values(self):
        """Should instantiate difficulty with minimum values"""
        difficulty = DifficultyLevel(
            level=1,
            speed=1,
            obstacle_density=0,
            food_spawn_rate=0.5,
            adaptive_mode=False
        )
        assert difficulty.level == 1
        assert difficulty.speed == 1
        assert difficulty.obstacle_density == 0
        assert difficulty.food_spawn_rate == 0.5

    def test_instantiate_difficulty_with_maximum_values(self):
        """Should instantiate difficulty with maximum values"""
        difficulty = DifficultyLevel(
            level=10,
            speed=10,
            obstacle_density=5,
            food_spawn_rate=2.0,
            adaptive_mode=True
        )
        assert difficulty.level == 10
        assert difficulty.speed == 10
        assert difficulty.obstacle_density == 5
        assert difficulty.food_spawn_rate == 2.0


class TestGameState:
    """Tests for GameState type"""

    def test_instantiate_valid_game_state(self):
        """Should instantiate a valid game state"""
        game_state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=10, y=11), Segment(x=10, y=12)],
            food=[Position(x=5, y=5)],
            obstacles=[Obstacle(x=15, y=15, type='static')],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1,
                speed=5,
                obstacle_density=1,
                food_spawn_rate=1.0,
                adaptive_mode=True
            ),
            timestamp=int(time.time() * 1000)
        )
        assert len(game_state.snake) == 3
        assert len(game_state.food) == 1
        assert len(game_state.obstacles) == 1
        assert game_state.score == 0
        assert game_state.game_over is False

    def test_instantiate_game_state_with_empty_food_and_obstacles(self):
        """Should instantiate game state with empty food and obstacles"""
        game_state = GameState(
            snake=[Segment(x=10, y=10)],
            food=[],
            obstacles=[],
            score=100,
            game_over=True,
            difficulty=DifficultyLevel(
                level=5,
                speed=7,
                obstacle_density=3,
                food_spawn_rate=1.5,
                adaptive_mode=False
            ),
            timestamp=int(time.time() * 1000)
        )
        assert len(game_state.food) == 0
        assert len(game_state.obstacles) == 0
        assert game_state.score == 100
        assert game_state.game_over is True


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics type"""

    def test_instantiate_valid_performance_metrics(self):
        """Should instantiate valid performance metrics"""
        metrics = PerformanceMetrics(
            survival_time=45.5,
            food_consumed=8,
            reaction_time=[150, 160, 155, 170],
            collisions_avoided=3,
            average_speed=5.2,
            timestamp=int(time.time() * 1000)
        )
        assert metrics.survival_time == 45.5
        assert metrics.food_consumed == 8
        assert len(metrics.reaction_time) == 4
        assert metrics.collisions_avoided == 3
        assert metrics.average_speed == 5.2

    def test_instantiate_metrics_with_zero_values(self):
        """Should instantiate metrics with zero values"""
        metrics = PerformanceMetrics(
            survival_time=0,
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0,
            timestamp=int(time.time() * 1000)
        )
        assert metrics.survival_time == 0
        assert metrics.food_consumed == 0
        assert len(metrics.reaction_time) == 0


class TestSkillAssessment:
    """Tests for SkillAssessment type"""

    def test_instantiate_valid_skill_assessment(self):
        """Should instantiate a valid skill assessment"""
        assessment = SkillAssessment(
            skill_level=65,
            trend='improving',
            confidence=0.85,
            last_updated=int(time.time() * 1000)
        )
        assert assessment.skill_level == 65
        assert assessment.trend == 'improving'
        assert assessment.confidence == 0.85

    def test_instantiate_skill_assessment_with_all_trend_types(self):
        """Should instantiate skill assessment with all trend types"""
        trends = ['improving', 'stable', 'declining']
        for trend in trends:
            assessment = SkillAssessment(
                skill_level=50,
                trend=trend,
                confidence=0.5,
                last_updated=int(time.time() * 1000)
            )
            assert assessment.trend == trend

    def test_instantiate_skill_assessment_with_boundary_confidence_values(self):
        """Should instantiate skill assessment with boundary confidence values"""
        low_confidence = SkillAssessment(
            skill_level=30,
            trend='stable',
            confidence=0,
            last_updated=int(time.time() * 1000)
        )
        high_confidence = SkillAssessment(
            skill_level=80,
            trend='improving',
            confidence=1,
            last_updated=int(time.time() * 1000)
        )
        assert low_confidence.confidence == 0
        assert high_confidence.confidence == 1


class TestDifficultyDelta:
    """Tests for DifficultyDelta type"""

    def test_instantiate_valid_difficulty_delta(self):
        """Should instantiate a valid difficulty delta"""
        delta = DifficultyDelta(
            speed_delta=1,
            obstacle_density_delta=0.5,
            food_spawn_rate_delta=0.1,
            reason='Player performing well'
        )
        assert delta.speed_delta == 1
        assert delta.obstacle_density_delta == 0.5
        assert delta.food_spawn_rate_delta == 0.1
        assert delta.reason == 'Player performing well'

    def test_instantiate_delta_with_negative_values(self):
        """Should instantiate delta with negative values"""
        delta = DifficultyDelta(
            speed_delta=-1,
            obstacle_density_delta=-1,
            food_spawn_rate_delta=-0.2,
            reason='Player struggling'
        )
        assert delta.speed_delta == -1
        assert delta.obstacle_density_delta == -1
        assert delta.food_spawn_rate_delta == -0.2


class TestAdaptationDecision:
    """Tests for AdaptationDecision type"""

    def test_instantiate_valid_adaptation_decision(self):
        """Should instantiate a valid adaptation decision"""
        timestamp = int(time.time() * 1000)
        decision = AdaptationDecision(
            timestamp=timestamp,
            metrics=PerformanceMetrics(
                survival_time=30,
                food_consumed=5,
                reaction_time=[150, 160],
                collisions_avoided=2,
                average_speed=5,
                timestamp=timestamp
            ),
            skill_assessment=SkillAssessment(
                skill_level=60,
                trend='improving',
                confidence=0.8,
                last_updated=timestamp
            ),
            difficulty_delta=DifficultyDelta(
                speed_delta=1,
                obstacle_density_delta=0.5,
                food_spawn_rate_delta=0.1,
                reason='Increasing difficulty'
            ),
            rationale='Player is improving steadily'
        )
        assert decision.metrics.food_consumed == 5
        assert decision.skill_assessment.skill_level == 60
        assert decision.difficulty_delta.speed_delta == 1
        assert decision.rationale == 'Player is improving steadily'


class TestGameSession:
    """Tests for GameSession type"""

    def test_instantiate_valid_game_session(self):
        """Should instantiate a valid game session"""
        timestamp = int(time.time() * 1000)
        session = GameSession(
            id='session-001',
            score=150,
            duration=120,
            difficulty=DifficultyLevel(
                level=5,
                speed=6,
                obstacle_density=2,
                food_spawn_rate=1.2,
                adaptive_mode=True
            ),
            metrics=PerformanceMetrics(
                survival_time=120,
                food_consumed=15,
                reaction_time=[150, 160, 155],
                collisions_avoided=5,
                average_speed=6,
                timestamp=timestamp
            ),
            timestamp=timestamp
        )
        assert session.id == 'session-001'
        assert session.score == 150
        assert session.duration == 120
        assert session.metrics.food_consumed == 15


class TestPlayerProfile:
    """Tests for PlayerProfile type"""

    def test_instantiate_valid_player_profile(self):
        """Should instantiate a valid player profile"""
        timestamp = int(time.time() * 1000)
        profile = PlayerProfile(
            sessions=[
                GameSession(
                    id='session-001',
                    score=100,
                    duration=60,
                    difficulty=DifficultyLevel(
                        level=1,
                        speed=5,
                        obstacle_density=1,
                        food_spawn_rate=1.0,
                        adaptive_mode=True
                    ),
                    metrics=PerformanceMetrics(
                        survival_time=60,
                        food_consumed=10,
                        reaction_time=[150],
                        collisions_avoided=2,
                        average_speed=5,
                        timestamp=timestamp
                    ),
                    timestamp=timestamp
                )
            ],
            best_score=100,
            average_survival_time=60,
            skill_progression=[
                SkillAssessment(
                    skill_level=50,
                    trend='stable',
                    confidence=0.7,
                    last_updated=timestamp
                )
            ]
        )
        assert len(profile.sessions) == 1
        assert profile.best_score == 100
        assert profile.average_survival_time == 60
        assert len(profile.skill_progression) == 1

    def test_instantiate_empty_player_profile(self):
        """Should instantiate an empty player profile"""
        profile = PlayerProfile()
        assert len(profile.sessions) == 0
        assert profile.best_score == 0
        assert len(profile.skill_progression) == 0


class TestCollisionResult:
    """Tests for CollisionResult type"""

    def test_instantiate_collision_result_with_no_collision(self):
        """Should instantiate a collision result with no collision"""
        result = CollisionResult(has_collision=False)
        assert result.has_collision is False
        assert result.type is None

    def test_instantiate_collision_result_with_self_collision(self):
        """Should instantiate a collision result with self collision"""
        result = CollisionResult(
            has_collision=True,
            type='self',
            position=Position(x=10, y=10)
        )
        assert result.has_collision is True
        assert result.type == 'self'
        assert result.position == Position(x=10, y=10)

    def test_instantiate_collision_result_with_obstacle_collision(self):
        """Should instantiate a collision result with obstacle collision"""
        result = CollisionResult(
            has_collision=True,
            type='obstacle',
            position=Position(x=15, y=15)
        )
        assert result.type == 'obstacle'

    def test_instantiate_collision_result_with_boundary_collision(self):
        """Should instantiate a collision result with boundary collision"""
        result = CollisionResult(
            has_collision=True,
            type='boundary',
            position=Position(x=20, y=20)
        )
        assert result.type == 'boundary'
