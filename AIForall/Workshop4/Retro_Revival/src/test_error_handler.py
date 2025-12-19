"""
Tests for error handling and validation
Requirements: 6.3, 6.4
"""

import pytest
from error_handler import (
    ErrorHandler,
    GameStateError,
    MetricsValidationError,
    DifficultyParameterError,
)
from game_types import (
    GameState,
    Segment,
    Position,
    Obstacle,
    DifficultyLevel,
    PerformanceMetrics,
)


class TestGameStateValidation:
    """Tests for game state validation"""

    def test_validate_valid_game_state(self):
        """Should validate a correct game state"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is True
        assert error is None

    def test_validate_none_game_state(self):
        """Should reject None game state"""
        is_valid, error = ErrorHandler.validate_game_state(None)
        assert is_valid is False
        assert "None" in error

    def test_validate_empty_snake(self):
        """Should reject empty snake"""
        state = GameState(
            snake=[],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_duplicate_snake_segments(self):
        """Should reject duplicate snake segments"""
        state = GameState(
            snake=[
                Segment(x=10, y=10),
                Segment(x=10, y=10),  # Duplicate
                Segment(x=8, y=10)
            ],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "duplicate" in error.lower()

    def test_validate_snake_head_out_of_bounds(self):
        """Should reject snake head out of bounds"""
        state = GameState(
            snake=[Segment(x=-1, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "out of bounds" in error.lower()

    def test_validate_food_out_of_bounds(self):
        """Should reject food out of bounds"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=25, y=25)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "out of bounds" in error.lower()

    def test_validate_food_overlaps_snake(self):
        """Should reject food that overlaps with snake"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=10, y=10)],  # Overlaps with snake head
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "overlaps" in error.lower()

    def test_validate_obstacle_out_of_bounds(self):
        """Should reject obstacle out of bounds"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[Obstacle(x=30, y=30, type='static')],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "out of bounds" in error.lower()

    def test_validate_obstacle_overlaps_snake(self):
        """Should reject obstacle that overlaps with snake"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[Obstacle(x=10, y=10, type='static')],  # Overlaps with snake head
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "overlaps" in error.lower()

    def test_validate_negative_score(self):
        """Should reject negative score"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=-10,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_invalid_difficulty(self):
        """Should reject invalid difficulty"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10), Segment(x=8, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=15,  # Out of range
                speed=5,
                obstacle_density=1,
                food_spawn_rate=1.0,
                adaptive_mode=True
            ),
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_game_state(state)
        assert is_valid is False
        assert "difficulty" in error.lower()


class TestMetricsValidation:
    """Tests for metrics validation"""

    def test_validate_valid_metrics(self):
        """Should validate correct metrics"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100, 150, 120],
            collisions_avoided=2,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is True
        assert error is None

    def test_validate_none_metrics(self):
        """Should reject None metrics"""
        is_valid, error = ErrorHandler.validate_metrics(None)
        assert is_valid is False
        assert "None" in error

    def test_validate_negative_survival_time(self):
        """Should reject negative survival time"""
        metrics = PerformanceMetrics(
            survival_time=-10.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_negative_food_consumed(self):
        """Should reject negative food consumed"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=-5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_negative_reaction_time(self):
        """Should reject negative reaction time"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100, -50],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_negative_collisions_avoided(self):
        """Should reject negative collisions avoided"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=-2,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_negative_average_speed(self):
        """Should reject negative average speed"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=-5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "negative" in error.lower()

    def test_validate_zero_metrics(self):
        """Should accept zero metrics"""
        metrics = PerformanceMetrics(
            survival_time=0.0,
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is True
        assert error is None

    def test_validate_excessive_survival_time(self):
        """Should reject excessive survival time"""
        metrics = PerformanceMetrics(
            survival_time=10000.0,  # > 1 hour
            food_consumed=5,
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "exceeds" in error.lower()

    def test_validate_excessive_reaction_time(self):
        """Should reject excessive reaction time"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[10000],  # > 5 seconds
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        is_valid, error = ErrorHandler.validate_metrics(metrics)
        assert is_valid is False
        assert "exceeds" in error.lower()


class TestDifficultyValidation:
    """Tests for difficulty level validation"""

    def test_validate_valid_difficulty(self):
        """Should validate correct difficulty"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is True
        assert error is None

    def test_validate_none_difficulty(self):
        """Should reject None difficulty"""
        is_valid, error = ErrorHandler.validate_difficulty_level(None)
        assert is_valid is False
        assert "None" in error

    def test_validate_level_too_low(self):
        """Should reject difficulty level too low"""
        difficulty = DifficultyLevel(
            level=0,  # Below minimum
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_level_too_high(self):
        """Should reject difficulty level too high"""
        difficulty = DifficultyLevel(
            level=15,  # Above maximum
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_speed_too_low(self):
        """Should reject speed too low"""
        difficulty = DifficultyLevel(
            level=5,
            speed=0,  # Below minimum
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_speed_too_high(self):
        """Should reject speed too high"""
        difficulty = DifficultyLevel(
            level=5,
            speed=15,  # Above maximum
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_obstacle_density_too_low(self):
        """Should reject obstacle density too low"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=-1,  # Below minimum
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_obstacle_density_too_high(self):
        """Should reject obstacle density too high"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=10,  # Above maximum
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_food_spawn_rate_too_low(self):
        """Should reject food spawn rate too low"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=0.1,  # Below minimum
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()

    def test_validate_food_spawn_rate_too_high(self):
        """Should reject food spawn rate too high"""
        difficulty = DifficultyLevel(
            level=5,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=3.0,  # Above maximum
            adaptive_mode=True
        )

        is_valid, error = ErrorHandler.validate_difficulty_level(difficulty)
        assert is_valid is False
        assert "out of range" in error.lower()


class TestAnomalyDetection:
    """Tests for anomaly detection in metrics"""

    def test_detect_high_reaction_time(self):
        """Should detect unusually high reaction time"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[2000, 2100, 2050],  # > 1 second average
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        anomalies = ErrorHandler.detect_anomalies(metrics)
        assert len(anomalies) > 0
        assert any("reaction time" in a.lower() for a in anomalies)

    def test_detect_high_food_consumption_rate(self):
        """Should detect unusually high food consumption rate"""
        metrics = PerformanceMetrics(
            survival_time=60.0,  # 1 minute
            food_consumed=100,  # 100 items per minute
            reaction_time=[100],
            collisions_avoided=0,
            average_speed=5.0,
            timestamp=1000
        )

        anomalies = ErrorHandler.detect_anomalies(metrics)
        assert len(anomalies) > 0
        assert any("consumption" in a.lower() for a in anomalies)

    def test_detect_zero_survival_with_food(self):
        """Should detect food consumed with zero survival time"""
        metrics = PerformanceMetrics(
            survival_time=0.0,
            food_consumed=5,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0.0,
            timestamp=1000
        )

        anomalies = ErrorHandler.detect_anomalies(metrics)
        assert len(anomalies) > 0
        assert any("survival" in a.lower() for a in anomalies)

    def test_detect_zero_speed_with_survival(self):
        """Should detect zero speed with positive survival time"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=0,
            reaction_time=[],
            collisions_avoided=0,
            average_speed=0.0,
            timestamp=1000
        )

        anomalies = ErrorHandler.detect_anomalies(metrics)
        assert len(anomalies) > 0
        assert any("speed" in a.lower() for a in anomalies)

    def test_no_anomalies_normal_metrics(self):
        """Should not detect anomalies in normal metrics"""
        metrics = PerformanceMetrics(
            survival_time=30.0,
            food_consumed=5,
            reaction_time=[100, 150, 120],
            collisions_avoided=2,
            average_speed=5.0,
            timestamp=1000
        )

        anomalies = ErrorHandler.detect_anomalies(metrics)
        assert len(anomalies) == 0


class TestStateRecovery:
    """Tests for corrupted state recovery"""

    def test_recover_duplicate_snake_segments(self):
        """Should remove duplicate snake segments"""
        state = GameState(
            snake=[
                Segment(x=10, y=10),
                Segment(x=10, y=10),  # Duplicate
                Segment(x=9, y=10)
            ],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        recovered = ErrorHandler.recover_corrupted_state(state)
        assert len(recovered.snake) == 2
        assert recovered.snake[0].x == 10 and recovered.snake[0].y == 10
        assert recovered.snake[1].x == 9 and recovered.snake[1].y == 10

    def test_recover_food_overlapping_snake(self):
        """Should remove food overlapping with snake"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10)],
            food=[
                Position(x=10, y=10),  # Overlaps with snake
                Position(x=15, y=15)   # Valid
            ],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        recovered = ErrorHandler.recover_corrupted_state(state)
        assert len(recovered.food) == 1
        assert recovered.food[0].x == 15 and recovered.food[0].y == 15

    def test_recover_obstacle_overlapping_snake(self):
        """Should remove obstacles overlapping with snake"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[
                Obstacle(x=10, y=10, type='static'),  # Overlaps with snake
                Obstacle(x=5, y=5, type='static')     # Valid
            ],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        recovered = ErrorHandler.recover_corrupted_state(state)
        assert len(recovered.obstacles) == 1
        assert recovered.obstacles[0].x == 5 and recovered.obstacles[0].y == 5

    def test_recover_negative_score(self):
        """Should clamp negative score to zero"""
        state = GameState(
            snake=[Segment(x=10, y=10), Segment(x=9, y=10)],
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=-100,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        recovered = ErrorHandler.recover_corrupted_state(state)
        assert recovered.score == 0

    def test_recover_none_state_raises_error(self):
        """Should raise error for None state"""
        with pytest.raises(GameStateError):
            ErrorHandler.recover_corrupted_state(None)

    def test_recover_unrecoverable_state_raises_error(self):
        """Should raise error if state cannot be recovered"""
        state = GameState(
            snake=[],  # Empty snake - unrecoverable
            food=[Position(x=15, y=15)],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=DifficultyLevel(
                level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
            ),
            timestamp=1000
        )

        with pytest.raises(GameStateError):
            ErrorHandler.recover_corrupted_state(state)


class TestInvalidDirectionRejection:
    """Tests for invalid direction rejection in game engine"""

    def test_reject_reverse_direction_right_to_left(self):
        """Should reject direction change from right to left"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'right'
        is_valid = engine._is_valid_direction_change('left')
        assert is_valid is False

    def test_reject_reverse_direction_left_to_right(self):
        """Should reject direction change from left to right"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'left'
        is_valid = engine._is_valid_direction_change('right')
        assert is_valid is False

    def test_reject_reverse_direction_up_to_down(self):
        """Should reject direction change from up to down"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'up'
        is_valid = engine._is_valid_direction_change('down')
        assert is_valid is False

    def test_reject_reverse_direction_down_to_up(self):
        """Should reject direction change from down to up"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'down'
        is_valid = engine._is_valid_direction_change('up')
        assert is_valid is False

    def test_allow_perpendicular_direction_right_to_up(self):
        """Should allow direction change from right to up"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'right'
        is_valid = engine._is_valid_direction_change('up')
        assert is_valid is True

    def test_allow_perpendicular_direction_right_to_down(self):
        """Should allow direction change from right to down"""
        from game_engine import GameEngine

        engine = GameEngine()
        engine.current_direction = 'right'
        is_valid = engine._is_valid_direction_change('down')
        assert is_valid is True


class TestOutOfBoundsPrevention:
    """Tests for out-of-bounds prevention"""

    def test_boundary_collision_prevents_movement(self):
        """Should detect boundary collision and end game"""
        from game_engine import GameEngine

        engine = GameEngine()
        # Move snake to right boundary
        for _ in range(15):
            engine.update('right')

        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'

    def test_boundary_collision_left(self):
        """Should detect left boundary collision"""
        from game_engine import GameEngine

        # Create engine with no obstacles to test boundary collision
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=0,  # No obstacles
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty=difficulty)
        engine.update('right')
        engine.update('up')
        engine.update('left')

        for _ in range(15):
            engine.update('left')

        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'

    def test_boundary_collision_top(self):
        """Should detect top boundary collision"""
        from game_engine import GameEngine

        # Create engine with no obstacles to test boundary collision
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=0,  # No obstacles
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty=difficulty)
        for _ in range(15):
            engine.update('up')

        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'

    def test_boundary_collision_bottom(self):
        """Should detect bottom boundary collision"""
        from game_engine import GameEngine

        # Create engine with no obstacles to test boundary collision
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=0,  # No obstacles
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty=difficulty)
        engine.update('right')
        for _ in range(15):
            engine.update('down')

        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'
        assert collision.type == 'boundary'
