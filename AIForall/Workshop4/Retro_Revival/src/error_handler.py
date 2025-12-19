"""
Error handling and validation utilities
Provides error handling for invalid game states, metrics validation, and parameter bounds checking
Requirements: 6.3, 6.4
"""

from typing import Optional, Tuple
from game_types import GameState, PerformanceMetrics, DifficultyLevel


class GameStateError(Exception):
    """Raised when game state is invalid"""
    pass


class MetricsValidationError(Exception):
    """Raised when metrics validation fails"""
    pass


class DifficultyParameterError(Exception):
    """Raised when difficulty parameters are invalid"""
    pass


class ErrorHandler:
    """Handles error detection and recovery for the game system"""

    # Validation bounds
    BOARD_WIDTH = 20
    BOARD_HEIGHT = 20
    MAX_SNAKE_LENGTH = 400  # Maximum possible snake length on 20x20 board
    MAX_OBSTACLES = 100
    MAX_FOOD = 100

    # Metrics bounds
    MAX_SURVIVAL_TIME = 3600.0  # 1 hour
    MAX_FOOD_CONSUMED = 1000
    MAX_REACTION_TIME = 5000  # 5 seconds
    MAX_COLLISIONS_AVOIDED = 1000
    MAX_AVERAGE_SPEED = 100.0

    # Difficulty bounds
    SPEED_MIN = 1
    SPEED_MAX = 10
    OBSTACLE_DENSITY_MIN = 0
    OBSTACLE_DENSITY_MAX = 5
    FOOD_SPAWN_RATE_MIN = 0.5
    FOOD_SPAWN_RATE_MAX = 2.0
    DIFFICULTY_LEVEL_MIN = 1
    DIFFICULTY_LEVEL_MAX = 10

    @staticmethod
    def validate_game_state(state: GameState) -> Tuple[bool, Optional[str]]:
        """
        Validate game state for consistency and correctness
        Returns (is_valid, error_message)
        """
        if state is None:
            return False, "Game state is None"

        # Validate snake
        if not state.snake:
            return False, "Snake list is empty"

        if len(state.snake) > ErrorHandler.MAX_SNAKE_LENGTH:
            return False, f"Snake length {len(state.snake)} exceeds maximum {ErrorHandler.MAX_SNAKE_LENGTH}"

        # Check for duplicate snake segments
        snake_positions = set()
        for segment in state.snake:
            if segment is None:
                return False, "Snake contains None segment"

            if not isinstance(segment.x, int) or not isinstance(segment.y, int):
                return False, "Snake segment coordinates must be integers"

            pos = (segment.x, segment.y)
            if pos in snake_positions:
                return False, f"Duplicate snake segment at position {pos}"

            snake_positions.add(pos)

        # Validate snake head is within bounds
        head = state.snake[0]
        if not (0 <= head.x < ErrorHandler.BOARD_WIDTH and 0 <= head.y < ErrorHandler.BOARD_HEIGHT):
            return False, f"Snake head at ({head.x}, {head.y}) is out of bounds"

        # Validate food
        if state.food is None:
            return False, "Food list is None"

        if len(state.food) > ErrorHandler.MAX_FOOD:
            return False, f"Food count {len(state.food)} exceeds maximum {ErrorHandler.MAX_FOOD}"

        for food in state.food:
            if food is None:
                return False, "Food list contains None"

            if not isinstance(food.x, int) or not isinstance(food.y, int):
                return False, "Food coordinates must be integers"

            if not (0 <= food.x < ErrorHandler.BOARD_WIDTH and 0 <= food.y < ErrorHandler.BOARD_HEIGHT):
                return False, f"Food at ({food.x}, {food.y}) is out of bounds"

            # Food should not overlap with snake
            if (food.x, food.y) in snake_positions:
                return False, f"Food overlaps with snake at ({food.x}, {food.y})"

        # Validate obstacles
        if state.obstacles is None:
            return False, "Obstacles list is None"

        if len(state.obstacles) > ErrorHandler.MAX_OBSTACLES:
            return False, f"Obstacle count {len(state.obstacles)} exceeds maximum {ErrorHandler.MAX_OBSTACLES}"

        obstacle_positions = set()
        for obstacle in state.obstacles:
            if obstacle is None:
                return False, "Obstacles list contains None"

            if not isinstance(obstacle.x, int) or not isinstance(obstacle.y, int):
                return False, "Obstacle coordinates must be integers"

            if not (0 <= obstacle.x < ErrorHandler.BOARD_WIDTH and 0 <= obstacle.y < ErrorHandler.BOARD_HEIGHT):
                return False, f"Obstacle at ({obstacle.x}, {obstacle.y}) is out of bounds"

            pos = (obstacle.x, obstacle.y)
            if pos in obstacle_positions:
                return False, f"Duplicate obstacle at position {pos}"

            obstacle_positions.add(pos)

            # Obstacle should not overlap with snake
            if pos in snake_positions:
                return False, f"Obstacle overlaps with snake at {pos}"

        # Validate score
        if not isinstance(state.score, int):
            return False, "Score must be an integer"

        if state.score < 0:
            return False, f"Score {state.score} cannot be negative"

        # Validate game_over flag
        if not isinstance(state.game_over, bool):
            return False, "game_over must be a boolean"

        # Validate difficulty
        if state.difficulty is None:
            return False, "Difficulty is None"

        is_valid, error = ErrorHandler.validate_difficulty_level(state.difficulty)
        if not is_valid:
            return False, f"Invalid difficulty: {error}"

        # Validate timestamp
        if not isinstance(state.timestamp, int):
            return False, "Timestamp must be an integer"

        if state.timestamp < 0:
            return False, f"Timestamp {state.timestamp} cannot be negative"

        return True, None

    @staticmethod
    def validate_metrics(metrics: PerformanceMetrics) -> Tuple[bool, Optional[str]]:
        """
        Validate performance metrics for correctness
        Returns (is_valid, error_message)
        """
        if metrics is None:
            return False, "Metrics is None"

        # Validate survival time
        if not isinstance(metrics.survival_time, (int, float)):
            return False, "Survival time must be numeric"

        if metrics.survival_time < 0:
            return False, f"Survival time {metrics.survival_time} cannot be negative"

        if metrics.survival_time > ErrorHandler.MAX_SURVIVAL_TIME:
            return False, f"Survival time {metrics.survival_time} exceeds maximum {ErrorHandler.MAX_SURVIVAL_TIME}"

        # Validate food consumed
        if not isinstance(metrics.food_consumed, int):
            return False, "Food consumed must be an integer"

        if metrics.food_consumed < 0:
            return False, f"Food consumed {metrics.food_consumed} cannot be negative"

        if metrics.food_consumed > ErrorHandler.MAX_FOOD_CONSUMED:
            return False, f"Food consumed {metrics.food_consumed} exceeds maximum {ErrorHandler.MAX_FOOD_CONSUMED}"

        # Validate reaction times
        if metrics.reaction_time is None:
            return False, "Reaction time list is None"

        if not isinstance(metrics.reaction_time, list):
            return False, "Reaction time must be a list"

        for rt in metrics.reaction_time:
            if not isinstance(rt, int):
                return False, "Reaction time values must be integers"

            if rt < 0:
                return False, f"Reaction time {rt} cannot be negative"

            if rt > ErrorHandler.MAX_REACTION_TIME:
                return False, f"Reaction time {rt} exceeds maximum {ErrorHandler.MAX_REACTION_TIME}"

        # Validate collisions avoided
        if not isinstance(metrics.collisions_avoided, int):
            return False, "Collisions avoided must be an integer"

        if metrics.collisions_avoided < 0:
            return False, f"Collisions avoided {metrics.collisions_avoided} cannot be negative"

        if metrics.collisions_avoided > ErrorHandler.MAX_COLLISIONS_AVOIDED:
            return False, f"Collisions avoided {metrics.collisions_avoided} exceeds maximum {ErrorHandler.MAX_COLLISIONS_AVOIDED}"

        # Validate average speed
        if not isinstance(metrics.average_speed, (int, float)):
            return False, "Average speed must be numeric"

        if metrics.average_speed < 0:
            return False, f"Average speed {metrics.average_speed} cannot be negative"

        if metrics.average_speed > ErrorHandler.MAX_AVERAGE_SPEED:
            return False, f"Average speed {metrics.average_speed} exceeds maximum {ErrorHandler.MAX_AVERAGE_SPEED}"

        # Validate timestamp
        if not isinstance(metrics.timestamp, int):
            return False, "Timestamp must be an integer"

        if metrics.timestamp < 0:
            return False, f"Timestamp {metrics.timestamp} cannot be negative"

        return True, None

    @staticmethod
    def validate_difficulty_level(difficulty: DifficultyLevel) -> Tuple[bool, Optional[str]]:
        """
        Validate difficulty level parameters
        Returns (is_valid, error_message)
        """
        if difficulty is None:
            return False, "Difficulty is None"

        # Validate level
        if not isinstance(difficulty.level, int):
            return False, "Difficulty level must be an integer"

        if not (ErrorHandler.DIFFICULTY_LEVEL_MIN <= difficulty.level <= ErrorHandler.DIFFICULTY_LEVEL_MAX):
            return False, f"Difficulty level {difficulty.level} out of range [{ErrorHandler.DIFFICULTY_LEVEL_MIN}, {ErrorHandler.DIFFICULTY_LEVEL_MAX}]"

        # Validate speed
        if not isinstance(difficulty.speed, (int, float)):
            return False, "Speed must be numeric"

        if not (ErrorHandler.SPEED_MIN <= difficulty.speed <= ErrorHandler.SPEED_MAX):
            return False, f"Speed {difficulty.speed} out of range [{ErrorHandler.SPEED_MIN}, {ErrorHandler.SPEED_MAX}]"

        # Validate obstacle density
        if not isinstance(difficulty.obstacle_density, (int, float)):
            return False, "Obstacle density must be numeric"

        if not (ErrorHandler.OBSTACLE_DENSITY_MIN <= difficulty.obstacle_density <= ErrorHandler.OBSTACLE_DENSITY_MAX):
            return False, f"Obstacle density {difficulty.obstacle_density} out of range [{ErrorHandler.OBSTACLE_DENSITY_MIN}, {ErrorHandler.OBSTACLE_DENSITY_MAX}]"

        # Validate food spawn rate
        if not isinstance(difficulty.food_spawn_rate, (int, float)):
            return False, "Food spawn rate must be numeric"

        if not (ErrorHandler.FOOD_SPAWN_RATE_MIN <= difficulty.food_spawn_rate <= ErrorHandler.FOOD_SPAWN_RATE_MAX):
            return False, f"Food spawn rate {difficulty.food_spawn_rate} out of range [{ErrorHandler.FOOD_SPAWN_RATE_MIN}, {ErrorHandler.FOOD_SPAWN_RATE_MAX}]"

        # Validate adaptive mode
        if not isinstance(difficulty.adaptive_mode, bool):
            return False, "Adaptive mode must be a boolean"

        return True, None

    @staticmethod
    def detect_anomalies(metrics: PerformanceMetrics) -> list:
        """
        Detect anomalies in metrics data
        Returns list of anomaly descriptions
        """
        anomalies = []

        # Check for unusually high reaction times
        if metrics.reaction_time:
            avg_reaction = sum(metrics.reaction_time) / len(metrics.reaction_time)
            if avg_reaction > 1000:  # > 1 second average
                anomalies.append(f"Unusually high average reaction time: {avg_reaction:.0f}ms")

        # Check for inconsistent food consumption vs survival time
        if metrics.survival_time > 0:
            food_rate = metrics.food_consumed / (metrics.survival_time / 60.0)
            if food_rate > 20:  # > 20 food per minute
                anomalies.append(f"Unusually high food consumption rate: {food_rate:.1f} items/min")

        # Check for zero survival time with food consumed
        if metrics.survival_time == 0 and metrics.food_consumed > 0:
            anomalies.append("Food consumed but zero survival time")

        # Check for zero average speed with positive survival time
        if metrics.survival_time > 0 and metrics.average_speed == 0:
            anomalies.append("Positive survival time but zero average speed")

        return anomalies

    @staticmethod
    def recover_corrupted_state(state: GameState) -> GameState:
        """
        Attempt to recover from corrupted game state
        Returns recovered state or raises GameStateError if unrecoverable
        """
        if state is None:
            raise GameStateError("Cannot recover from None state")

        # Remove duplicate snake segments (keep first occurrence)
        if state.snake:
            seen = set()
            unique_snake = []
            for segment in state.snake:
                pos = (segment.x, segment.y)
                if pos not in seen:
                    unique_snake.append(segment)
                    seen.add(pos)
            state.snake = unique_snake

        # Remove food that overlaps with snake
        if state.food and state.snake:
            snake_positions = {(s.x, s.y) for s in state.snake}
            state.food = [f for f in state.food if (f.x, f.y) not in snake_positions]

        # Remove obstacles that overlap with snake
        if state.obstacles and state.snake:
            snake_positions = {(s.x, s.y) for s in state.snake}
            state.obstacles = [o for o in state.obstacles if (o.x, o.y) not in snake_positions]

        # Clamp score to non-negative
        if state.score < 0:
            state.score = 0

        # Validate the recovered state
        is_valid, error = ErrorHandler.validate_game_state(state)
        if not is_valid:
            raise GameStateError(f"Cannot recover corrupted state: {error}")

        return state
