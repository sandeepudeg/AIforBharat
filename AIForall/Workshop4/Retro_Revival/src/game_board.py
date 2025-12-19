"""
Game Board Rendering Component
Handles rendering of the game board, snake, food, obstacles, and score
Requirements: 1.1, 3.1
"""

from typing import Optional, List, Tuple
from game_types import GameState, Segment, Position, Obstacle


class GameBoard:
    """Renders the game board with snake, food, obstacles, and score"""

    BOARD_WIDTH = 20
    BOARD_HEIGHT = 20
    CELL_SIZE = 20

    def __init__(self, cell_size: int = 20, board_width: int = 20, board_height: int = 20):
        """Initialize the game board renderer"""
        self.cell_size = cell_size
        self.board_width = board_width
        self.board_height = board_height
        self.canvas_width = board_width * cell_size
        self.canvas_height = board_height * cell_size

    def render_to_string(self, game_state: GameState) -> str:
        """
        Render the game board to a string representation for testing
        Returns a visual representation of the board
        """
        # Create a 2D grid
        grid = [['.' for _ in range(self.board_width)] for _ in range(self.board_height)]

        # Place obstacles
        for obstacle in game_state.obstacles:
            if 0 <= obstacle.x < self.board_width and 0 <= obstacle.y < self.board_height:
                grid[obstacle.y][obstacle.x] = '#'

        # Place food
        for food in game_state.food:
            if 0 <= food.x < self.board_width and 0 <= food.y < self.board_height:
                grid[food.y][food.x] = '*'

        # Place snake (head is 'H', body is 'S')
        for i, segment in enumerate(game_state.snake):
            if 0 <= segment.x < self.board_width and 0 <= segment.y < self.board_height:
                if i == 0:
                    grid[segment.y][segment.x] = 'H'
                else:
                    grid[segment.y][segment.x] = 'S'

        # Convert grid to string
        board_str = '\n'.join([''.join(row) for row in grid])
        score_str = f"\nScore: {game_state.score}"
        return board_str + score_str

    def get_cell_content(self, game_state: GameState, x: int, y: int) -> str:
        """Get the content of a specific cell"""
        if not (0 <= x < self.board_width and 0 <= y < self.board_height):
            return 'X'  # Out of bounds

        # Check if snake head
        if game_state.snake and game_state.snake[0].x == x and game_state.snake[0].y == y:
            return 'H'

        # Check if snake body
        for segment in game_state.snake[1:]:
            if segment.x == x and segment.y == y:
                return 'S'

        # Check if food
        for food in game_state.food:
            if food.x == x and food.y == y:
                return '*'

        # Check if obstacle
        for obstacle in game_state.obstacles:
            if obstacle.x == x and obstacle.y == y:
                return '#'

        return '.'

    def get_canvas_dimensions(self) -> Tuple[int, int]:
        """Get the canvas dimensions"""
        return (self.canvas_width, self.canvas_height)

    def validate_render(self, game_state: GameState) -> bool:
        """Validate that the game state can be rendered"""
        # Check snake
        if not game_state.snake:
            return False

        # Check all snake segments are within bounds
        for segment in game_state.snake:
            if not (0 <= segment.x < self.board_width and 0 <= segment.y < self.board_height):
                return False

        # Check all food is within bounds
        for food in game_state.food:
            if not (0 <= food.x < self.board_width and 0 <= food.y < self.board_height):
                return False

        # Check all obstacles are within bounds
        for obstacle in game_state.obstacles:
            if not (0 <= obstacle.x < self.board_width and 0 <= obstacle.y < self.board_height):
                return False

        return True

    def get_snake_length(self, game_state: GameState) -> int:
        """Get the snake length from game state"""
        return len(game_state.snake)

    def get_food_count(self, game_state: GameState) -> int:
        """Get the number of food items"""
        return len(game_state.food)

    def get_obstacle_count(self, game_state: GameState) -> int:
        """Get the number of obstacles"""
        return len(game_state.obstacles)

    def get_score(self, game_state: GameState) -> int:
        """Get the current score"""
        return game_state.score
