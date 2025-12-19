"""
Unit tests for GameBoard rendering component
Tests snake rendering with various lengths, food and obstacle rendering, and score display accuracy
Requirements: 1.1, 3.1
"""

import pytest
from game_board import GameBoard
from game_types import GameState, Segment, Position, Obstacle, DifficultyLevel


class TestGameBoardRendering:
    """Test suite for GameBoard rendering component"""

    @pytest.fixture
    def game_board(self):
        """Create a game board instance"""
        return GameBoard(cell_size=20, board_width=20, board_height=20)

    @pytest.fixture
    def default_difficulty(self):
        """Create default difficulty level"""
        return DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )

    def create_game_state(self, snake=None, food=None, obstacles=None, score=0, difficulty=None):
        """Helper to create a game state"""
        if difficulty is None:
            difficulty = DifficultyLevel(
                level=1,
                speed=5,
                obstacle_density=1,
                food_spawn_rate=1.0,
                adaptive_mode=True
            )

        # Use provided values, don't use defaults if None is explicitly passed
        if snake is None:
            snake = [Segment(x=10, y=10), Segment(x=10, y=11), Segment(x=10, y=12)]
        if food is None:
            food = [Position(x=5, y=5)]
        if obstacles is None:
            obstacles = [Obstacle(x=8, y=8, type='static')]

        return GameState(
            snake=snake,
            food=food,
            obstacles=obstacles,
            score=score,
            game_over=False,
            difficulty=difficulty,
            timestamp=0
        )

    # Canvas Initialization Tests
    def test_canvas_dimensions(self, game_board):
        """Test canvas dimensions are correct"""
        width, height = game_board.get_canvas_dimensions()
        assert width == 400  # 20 * 20
        assert height == 400  # 20 * 20

    def test_canvas_dimensions_custom(self):
        """Test canvas dimensions with custom sizes"""
        board = GameBoard(cell_size=10, board_width=30, board_height=25)
        width, height = board.get_canvas_dimensions()
        assert width == 300  # 30 * 10
        assert height == 250  # 25 * 10

    # Snake Rendering Tests
    def test_render_snake_length_3(self, game_board):
        """Test rendering snake with initial length of 3"""
        snake = [
            Segment(x=10, y=10),
            Segment(x=10, y=11),
            Segment(x=10, y=12)
        ]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_snake_length(game_state) == 3

    def test_render_snake_length_1(self, game_board):
        """Test rendering snake with length 1"""
        snake = [Segment(x=10, y=10)]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_snake_length(game_state) == 1

    def test_render_snake_length_5(self, game_board):
        """Test rendering snake with length 5"""
        snake = [
            Segment(x=10, y=10),
            Segment(x=10, y=11),
            Segment(x=10, y=12),
            Segment(x=10, y=13),
            Segment(x=10, y=14)
        ]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_snake_length(game_state) == 5

    def test_render_snake_length_10(self, game_board):
        """Test rendering snake with length 10"""
        snake = [Segment(x=10, y=10 + i) for i in range(10)]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_snake_length(game_state) == 10

    def test_render_snake_maximum_length(self, game_board):
        """Test rendering snake with maximum length (entire board)"""
        snake = [Segment(x=i % 20, y=i // 20) for i in range(400)]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_snake_length(game_state) == 400

    def test_render_snake_at_different_positions(self, game_board):
        """Test rendering snake at different board positions"""
        positions = [
            [Segment(x=0, y=0), Segment(x=0, y=1), Segment(x=0, y=2)],
            [Segment(x=19, y=19), Segment(x=19, y=18), Segment(x=19, y=17)],
            [Segment(x=5, y=5), Segment(x=5, y=6), Segment(x=5, y=7)]
        ]

        for snake in positions:
            game_state = self.create_game_state(snake=snake)
            assert game_board.validate_render(game_state)

    # Food Rendering Tests
    def test_render_single_food(self, game_board):
        """Test rendering single food item"""
        food = [Position(x=5, y=5)]
        game_state = self.create_game_state(food=food)
        assert game_board.get_food_count(game_state) == 1

    def test_render_multiple_food(self, game_board):
        """Test rendering multiple food items"""
        food = [
            Position(x=5, y=5),
            Position(x=10, y=10),
            Position(x=15, y=15)
        ]
        game_state = self.create_game_state(food=food)
        assert game_board.get_food_count(game_state) == 3

    def test_render_food_at_boundaries(self, game_board):
        """Test rendering food at board boundaries"""
        food = [
            Position(x=0, y=0),
            Position(x=19, y=19),
            Position(x=0, y=19),
            Position(x=19, y=0)
        ]
        game_state = self.create_game_state(food=food)
        assert game_board.get_food_count(game_state) == 4

    def test_render_no_food(self, game_board):
        """Test rendering with no food items"""
        snake = [Segment(x=10, y=10)]
        obstacles = [Obstacle(x=8, y=8, type='static')]
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = GameState(
            snake=snake, food=[], obstacles=obstacles, score=0, game_over=False,
            difficulty=difficulty, timestamp=0
        )
        assert game_board.get_food_count(game_state) == 0

    # Obstacle Rendering Tests
    def test_render_single_obstacle(self, game_board):
        """Test rendering single obstacle"""
        obstacles = [Obstacle(x=8, y=8, type='static')]
        game_state = self.create_game_state(obstacles=obstacles)
        assert game_board.get_obstacle_count(game_state) == 1

    def test_render_multiple_obstacles(self, game_board):
        """Test rendering multiple obstacles"""
        obstacles = [
            Obstacle(x=5, y=5, type='static'),
            Obstacle(x=10, y=10, type='static'),
            Obstacle(x=15, y=15, type='static')
        ]
        game_state = self.create_game_state(obstacles=obstacles)
        assert game_board.get_obstacle_count(game_state) == 3

    def test_render_obstacles_different_types(self, game_board):
        """Test rendering obstacles with different types"""
        obstacles = [
            Obstacle(x=5, y=5, type='static'),
            Obstacle(x=10, y=10, type='dynamic')
        ]
        game_state = self.create_game_state(obstacles=obstacles)
        assert game_board.get_obstacle_count(game_state) == 2

    def test_render_no_obstacles(self, game_board):
        """Test rendering with no obstacles"""
        snake = [Segment(x=10, y=10)]
        food = [Position(x=5, y=5)]
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = GameState(
            snake=snake, food=food, obstacles=[], score=0, game_over=False,
            difficulty=difficulty, timestamp=0
        )
        assert game_board.get_obstacle_count(game_state) == 0

    def test_render_maximum_obstacles(self, game_board):
        """Test rendering maximum obstacles (5)"""
        obstacles = [
            Obstacle(x=2, y=2, type='static'),
            Obstacle(x=5, y=5, type='static'),
            Obstacle(x=8, y=8, type='static'),
            Obstacle(x=11, y=11, type='static'),
            Obstacle(x=14, y=14, type='static')
        ]
        game_state = self.create_game_state(obstacles=obstacles)
        assert game_board.get_obstacle_count(game_state) == 5

    # Score Display Tests
    def test_display_score_0(self, game_board):
        """Test displaying score of 0"""
        game_state = self.create_game_state(score=0)
        assert game_board.get_score(game_state) == 0

    def test_display_score_100(self, game_board):
        """Test displaying score of 100"""
        game_state = self.create_game_state(score=100)
        assert game_board.get_score(game_state) == 100

    def test_display_score_1000(self, game_board):
        """Test displaying score of 1000"""
        game_state = self.create_game_state(score=1000)
        assert game_board.get_score(game_state) == 1000

    def test_display_large_score(self, game_board):
        """Test displaying large score values"""
        game_state = self.create_game_state(score=9999)
        assert game_board.get_score(game_state) == 9999

    def test_display_score_multiple_renders(self, game_board):
        """Test score display accuracy after multiple renders"""
        game_state1 = self.create_game_state(score=50)
        assert game_board.get_score(game_state1) == 50

        game_state2 = self.create_game_state(score=150)
        assert game_board.get_score(game_state2) == 150

    # Complete Game State Rendering Tests
    def test_render_complete_game_state(self, game_board):
        """Test rendering complete game state with all elements"""
        snake = [
            Segment(x=10, y=10),
            Segment(x=10, y=11),
            Segment(x=10, y=12)
        ]
        food = [Position(x=5, y=5), Position(x=15, y=15)]
        obstacles = [Obstacle(x=8, y=8, type='static')]

        game_state = self.create_game_state(
            snake=snake,
            food=food,
            obstacles=obstacles,
            score=100
        )

        assert game_board.get_snake_length(game_state) == 3
        assert game_board.get_food_count(game_state) == 2
        assert game_board.get_obstacle_count(game_state) == 1
        assert game_board.get_score(game_state) == 100

    def test_render_game_state_empty_food_obstacles(self, game_board):
        """Test rendering game state with empty food and obstacles"""
        snake = [Segment(x=10, y=10)]
        difficulty = DifficultyLevel(
            level=1, speed=5, obstacle_density=1, food_spawn_rate=1.0, adaptive_mode=True
        )
        game_state = GameState(
            snake=snake,
            food=[],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=difficulty,
            timestamp=0
        )

        assert game_board.get_food_count(game_state) == 0
        assert game_board.get_obstacle_count(game_state) == 0

    # Edge Cases Tests
    def test_render_snake_at_board_edges(self, game_board):
        """Test rendering with snake at board edges"""
        snake = [
            Segment(x=0, y=0),
            Segment(x=19, y=19)
        ]
        game_state = self.create_game_state(snake=snake)
        assert game_board.validate_render(game_state)

    def test_render_all_elements_same_location(self, game_board):
        """Test rendering with all elements at same location (edge case)"""
        snake = [Segment(x=10, y=10)]
        food = [Position(x=10, y=10)]
        obstacles = [Obstacle(x=10, y=10, type='static')]

        game_state = self.create_game_state(
            snake=snake,
            food=food,
            obstacles=obstacles,
            score=50
        )

        assert game_board.validate_render(game_state)

    # String Rendering Tests
    def test_render_to_string(self, game_board):
        """Test rendering game state to string"""
        snake = [Segment(x=10, y=10)]
        food = [Position(x=5, y=5)]
        obstacles = [Obstacle(x=8, y=8, type='static')]

        game_state = self.create_game_state(
            snake=snake,
            food=food,
            obstacles=obstacles,
            score=50
        )

        board_str = game_board.render_to_string(game_state)
        assert 'H' in board_str  # Snake head
        assert '*' in board_str  # Food
        assert '#' in board_str  # Obstacle
        assert 'Score: 50' in board_str

    def test_get_cell_content_snake_head(self, game_board):
        """Test getting cell content for snake head"""
        snake = [Segment(x=10, y=10)]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_cell_content(game_state, 10, 10) == 'H'

    def test_get_cell_content_snake_body(self, game_board):
        """Test getting cell content for snake body"""
        snake = [
            Segment(x=10, y=10),
            Segment(x=10, y=11)
        ]
        game_state = self.create_game_state(snake=snake)
        assert game_board.get_cell_content(game_state, 10, 11) == 'S'

    def test_get_cell_content_food(self, game_board):
        """Test getting cell content for food"""
        food = [Position(x=5, y=5)]
        game_state = self.create_game_state(food=food)
        assert game_board.get_cell_content(game_state, 5, 5) == '*'

    def test_get_cell_content_obstacle(self, game_board):
        """Test getting cell content for obstacle"""
        obstacles = [Obstacle(x=8, y=8, type='static')]
        game_state = self.create_game_state(obstacles=obstacles)
        assert game_board.get_cell_content(game_state, 8, 8) == '#'

    def test_get_cell_content_empty(self, game_board):
        """Test getting cell content for empty cell"""
        game_state = self.create_game_state()
        assert game_board.get_cell_content(game_state, 0, 0) == '.'

    def test_get_cell_content_out_of_bounds(self, game_board):
        """Test getting cell content for out of bounds"""
        game_state = self.create_game_state()
        assert game_board.get_cell_content(game_state, 20, 20) == 'X'
