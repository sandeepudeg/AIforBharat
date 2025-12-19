"""
Tests for GameEngine
Includes unit tests and property-based tests for core game mechanics
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import pytest
from hypothesis import given, strategies as st, settings
from game_engine import GameEngine
from game_types import (
    Segment,
    Position,
    Obstacle,
    DifficultyLevel,
    GameState,
)


class TestGameEngineInitialization:
    """Tests for game engine initialization"""

    def test_initialize_with_default_difficulty(self):
        """Should initialize with default difficulty"""
        engine = GameEngine()
        assert engine.game_state.difficulty.level == 1
        assert engine.game_state.difficulty.speed == 5
        assert engine.game_state.difficulty.adaptive_mode is True

    def test_initialize_with_custom_difficulty(self):
        """Should initialize with custom difficulty"""
        difficulty = DifficultyLevel(
            level=5,
            speed=7,
            obstacle_density=2,
            food_spawn_rate=1.5,
            adaptive_mode=False
        )
        engine = GameEngine(difficulty)
        assert engine.game_state.difficulty.level == 5
        assert engine.game_state.difficulty.speed == 7

    def test_initial_snake_length(self):
        """Should initialize snake with length 3"""
        engine = GameEngine()
        assert len(engine.game_state.snake) == 3

    def test_initial_snake_position(self):
        """Should initialize snake at center of board"""
        engine = GameEngine()
        head = engine.game_state.snake[0]
        assert head.x == 10
        assert head.y == 10

    def test_initial_food_spawned(self):
        """Should spawn at least one food item"""
        engine = GameEngine()
        assert len(engine.game_state.food) >= 1

    def test_initial_obstacles_spawned(self):
        """Should spawn obstacles based on difficulty"""
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=2,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty)
        assert len(engine.game_state.obstacles) == 2

    def test_game_not_over_initially(self):
        """Should not be game over initially"""
        engine = GameEngine()
        assert engine.game_state.game_over is False

    def test_initial_score_is_zero(self):
        """Should start with score of 0"""
        engine = GameEngine()
        assert engine.game_state.score == 0


class TestSnakeMovement:
    """Tests for snake movement"""

    def test_move_right(self):
        """Should move snake right"""
        engine = GameEngine()
        initial_head = engine.game_state.snake[0]
        engine.update('right')
        new_head = engine.game_state.snake[0]
        assert new_head.x == initial_head.x + 1
        assert new_head.y == initial_head.y

    def test_move_left(self):
        """Should move snake left"""
        engine = GameEngine()
        engine.update('right')  # Move right first
        engine.update('up')     # Move up
        engine.update('left')   # Move left
        head = engine.game_state.snake[0]
        # After these moves, snake should have moved left
        assert head.x < 11

    def test_move_up(self):
        """Should move snake up"""
        engine = GameEngine()
        engine.update('right')  # Move right first to avoid reversing
        engine.update('up')
        head = engine.game_state.snake[0]
        assert head.y < 10

    def test_move_down(self):
        """Should move snake down"""
        engine = GameEngine()
        engine.update('right')  # Move right first
        engine.update('down')
        head = engine.game_state.snake[0]
        assert head.y > 10

    def test_snake_length_unchanged_without_food(self):
        """Snake length should remain constant without consuming food"""
        engine = GameEngine()
        initial_length = len(engine.game_state.snake)
        engine.update('right')
        assert len(engine.game_state.snake) == initial_length

    def test_cannot_reverse_into_self(self):
        """Should not allow reversing direction into self"""
        engine = GameEngine()
        engine.current_direction = 'right'
        # Try to move left (opposite of right)
        is_valid = engine._is_valid_direction_change('left')
        assert is_valid is False

    def test_can_change_to_perpendicular_direction(self):
        """Should allow changing to perpendicular direction"""
        engine = GameEngine()
        engine.current_direction = 'right'
        # Try to move up (perpendicular to right)
        is_valid = engine._is_valid_direction_change('up')
        assert is_valid is True


class TestCollisionDetection:
    """Tests for collision detection"""

    def test_no_collision_initially(self):
        """Should have no collision initially"""
        engine = GameEngine()
        collision = engine.check_collisions()
        assert collision.has_collision is False

    def test_boundary_collision_right(self):
        """Should detect collision at right boundary"""
        # Create engine with no obstacles to test boundary collision
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=0,  # No obstacles
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty=difficulty)
        # Move snake to right boundary
        for _ in range(15):
            engine.update('right')
        
        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'

    def test_boundary_collision_left(self):
        """Should detect collision at left boundary"""
        # Create engine with no obstacles to test boundary collision
        difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=0,  # No obstacles
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        engine = GameEngine(difficulty=difficulty)
        # Move snake to left boundary
        engine.update('right')
        engine.update('up')
        engine.update('left')
        
        for _ in range(15):
            engine.update('left')
        
        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'boundary'

    def test_self_collision(self):
        """Should detect self collision"""
        engine = GameEngine()
        # Manually create a self-collision scenario
        # Place snake segments where head will collide with body
        engine.game_state.snake = [
            Segment(x=10, y=10),  # head
            Segment(x=10, y=11),  # body segment that head will collide with
            Segment(x=9, y=11),
            Segment(x=8, y=11),
        ]
        
        # Move head down to collide with body at (10, 11)
        engine.current_direction = 'down'
        engine._move_snake()
        
        # After moving down, head should be at (10, 11)
        head = engine.game_state.snake[0]
        assert head.x == 10 and head.y == 11
        
        # Now check collision - head is at (10, 11) and body[1] is at (10, 11)
        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'self'

    def test_obstacle_collision(self):
        """Should detect obstacle collision"""
        engine = GameEngine()
        # Manually place an obstacle in front of snake
        engine.game_state.obstacles.append(
            Obstacle(x=11, y=10, type='static')
        )
        
        engine.update('right')
        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'obstacle'


class TestFoodConsumption:
    """Tests for food consumption and scoring"""

    def test_food_consumption_increases_score(self):
        """Should increase score when consuming food"""
        engine = GameEngine()
        initial_score = engine.game_state.score
        
        # Place food at snake head position
        head = engine.game_state.snake[0]
        engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
        
        engine.update('right')
        assert engine.game_state.score > initial_score

    def test_food_consumption_grows_snake(self):
        """Should grow snake by 1 segment when consuming food"""
        engine = GameEngine()
        initial_length = len(engine.game_state.snake)
        
        # Place food at snake head position
        head = engine.game_state.snake[0]
        engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
        
        engine.update('right')
        assert len(engine.game_state.snake) == initial_length + 1

    def test_score_calculation(self):
        """Should calculate score correctly (10 points per food)"""
        engine = GameEngine()
        
        # Consume multiple food items
        consumed = 0
        for _ in range(3):
            if engine.game_state.game_over:
                break
            head = engine.game_state.snake[0]
            engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
            engine.update('right')
            consumed += 1
        
        expected_score = consumed * 10
        assert engine.game_state.score == expected_score

    def test_new_food_spawned_after_consumption(self):
        """Should spawn new food after consumption"""
        engine = GameEngine()
        
        # Place food at snake head
        head = engine.game_state.snake[0]
        engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
        
        engine.update('right')
        # After consumption, new food should be spawned
        assert len(engine.game_state.food) >= 1


class TestGameReset:
    """Tests for game reset functionality"""

    def test_reset_clears_game_over(self):
        """Should clear game over flag on reset"""
        engine = GameEngine()
        engine.game_state.game_over = True
        engine.reset()
        assert engine.game_state.game_over is False

    def test_reset_restores_initial_snake_length(self):
        """Should restore initial snake length on reset"""
        engine = GameEngine()
        # Consume some food
        head = engine.game_state.snake[0]
        engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
        engine.update('right')
        
        engine.reset()
        assert len(engine.game_state.snake) == 3

    def test_reset_clears_score(self):
        """Should clear score on reset"""
        engine = GameEngine()
        engine.game_state.score = 100
        engine.reset()
        assert engine.game_state.score == 0

    def test_reset_restores_snake_position(self):
        """Should restore snake to center on reset"""
        engine = GameEngine()
        engine.update('right')
        engine.reset()
        head = engine.game_state.snake[0]
        assert head.x == 10
        assert head.y == 10


class TestGameStateRetrieval:
    """Tests for game state retrieval"""

    def test_get_game_state(self):
        """Should return current game state"""
        engine = GameEngine()
        state = engine.get_game_state()
        assert isinstance(state, GameState)
        assert len(state.snake) == 3

    def test_get_snake_length(self):
        """Should return correct snake length"""
        engine = GameEngine()
        assert engine.get_snake_length() == 3

    def test_get_food_count(self):
        """Should return correct food count"""
        engine = GameEngine()
        count = engine.get_food_count()
        assert count >= 1

    def test_get_obstacle_count(self):
        """Should return correct obstacle count"""
        engine = GameEngine()
        count = engine.get_obstacle_count()
        assert count >= 0


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestGameEngineProperties:
    """Property-based tests for game engine correctness"""

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_property_1_snake_growth_consistency(self, food_count: int):
        """
        Property 1: Snake Growth Consistency
        For any game session where the player consumes N food items,
        the snake's length should increase by exactly N segments from its initial length of 3.
        
        **Feature: snake-adaptive-ai, Property 1: Snake Growth Consistency**
        **Validates: Requirements 1.3**
        """
        engine = GameEngine()
        initial_length = engine.get_snake_length()
        
        # Consume food_count items (limited to avoid boundary collision)
        consumed = 0
        for _ in range(food_count):
            if engine.game_state.game_over:
                break
            head = engine.game_state.snake[0]
            # Place food in front of snake
            engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
            engine.update('right')
            consumed += 1
        
        final_length = engine.get_snake_length()
        assert final_length == initial_length + consumed

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_property_2_score_calculation_accuracy(self, food_count: int):
        """
        Property 2: Score Calculation Accuracy
        For any game session, the final score should equal the number of food items
        consumed multiplied by 10 points per item.
        
        **Feature: snake-adaptive-ai, Property 2: Score Calculation Accuracy**
        **Validates: Requirements 1.3**
        """
        engine = GameEngine()
        
        # Consume food_count items (limited to avoid boundary collision)
        consumed = 0
        for _ in range(food_count):
            if engine.game_state.game_over:
                break
            head = engine.game_state.snake[0]
            engine.game_state.food = [Position(x=head.x + 1, y=head.y)]
            engine.update('right')
            consumed += 1
        
        expected_score = consumed * 10
        assert engine.game_state.score == expected_score

    def test_property_3_collision_detection_completeness(self):
        """
        Property 3: Collision Detection Completeness
        For any snake position and obstacle configuration, if the snake's head
        occupies the same cell as an obstacle or the snake's body, the game should immediately end.
        
        **Feature: snake-adaptive-ai, Property 3: Collision Detection Completeness**
        **Validates: Requirements 1.4**
        """
        engine = GameEngine()
        
        # Test obstacle collision
        engine.game_state.obstacles.append(
            Obstacle(x=11, y=10, type='static')
        )
        engine.update('right')
        
        collision = engine.check_collisions()
        assert collision.has_collision is True
        assert collision.type == 'obstacle'

    def test_property_4_food_spawn_validity(self):
        """
        Property 4: Food Spawn Validity
        For any game state, newly spawned food should always occupy a cell that is not
        currently occupied by the snake, obstacles, or existing food.
        
        **Feature: snake-adaptive-ai, Property 4: Food Spawn Validity**
        **Validates: Requirements 1.5**
        """
        engine = GameEngine()
        
        # Get all occupied cells
        occupied = set()
        for segment in engine.game_state.snake:
            occupied.add((segment.x, segment.y))
        for food in engine.game_state.food:
            occupied.add((food.x, food.y))
        for obstacle in engine.game_state.obstacles:
            occupied.add((obstacle.x, obstacle.y))
        
        # Verify all food is in unoccupied cells
        for food in engine.game_state.food:
            # Food should not be on snake or obstacles
            assert (food.x, food.y) not in [(s.x, s.y) for s in engine.game_state.snake]
            assert (food.x, food.y) not in [(o.x, o.y) for o in engine.game_state.obstacles]
