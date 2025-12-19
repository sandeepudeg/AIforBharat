"""
Core game engine for Snake Adaptive AI
Handles movement, collision detection, and food spawning
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

import random
import time
from typing import Optional, Tuple
from game_types import (
    Segment,
    Position,
    Obstacle,
    Direction,
    DifficultyLevel,
    GameState,
    CollisionResult,
)


class GameEngine:
    """Manages core Snake game mechanics"""

    BOARD_WIDTH = 20
    BOARD_HEIGHT = 20
    INITIAL_SNAKE_LENGTH = 3
    POINTS_PER_FOOD = 10

    def __init__(self, difficulty: Optional[DifficultyLevel] = None):
        """Initialize the game engine with optional difficulty settings"""
        if difficulty is None:
            difficulty = DifficultyLevel(
                level=1,
                speed=5,
                obstacle_density=1,
                food_spawn_rate=1.0,
                adaptive_mode=True
            )
        
        self.difficulty = difficulty
        self.game_state = self._initialize_game_state()
        self.current_direction = 'right'
        self.next_direction = 'right'

    def _initialize_game_state(self) -> GameState:
        """Initialize a new game state"""
        # Create initial snake at center
        center_x = self.BOARD_WIDTH // 2
        center_y = self.BOARD_HEIGHT // 2
        
        snake = [
            Segment(x=center_x, y=center_y),
            Segment(x=center_x - 1, y=center_y),
            Segment(x=center_x - 2, y=center_y),
        ]
        
        game_state = GameState(
            snake=snake,
            food=[],
            obstacles=[],
            score=0,
            game_over=False,
            difficulty=self.difficulty,
            timestamp=int(time.time() * 1000)
        )
        
        # Spawn initial food and obstacles
        self._spawn_food(game_state)
        self._spawn_obstacles(game_state)
        
        return game_state

    def _get_occupied_cells(self, game_state: GameState) -> set:
        """Get all occupied cells on the board"""
        occupied = set()
        
        # Add snake segments
        for segment in game_state.snake:
            occupied.add((segment.x, segment.y))
        
        # Add food
        for food in game_state.food:
            occupied.add((food.x, food.y))
        
        # Add obstacles
        for obstacle in game_state.obstacles:
            occupied.add((obstacle.x, obstacle.y))
        
        return occupied

    def _spawn_food(self, game_state: GameState) -> None:
        """Spawn food at a random unoccupied position"""
        occupied = self._get_occupied_cells(game_state)
        
        # Find an unoccupied cell
        while True:
            x = random.randint(0, self.BOARD_WIDTH - 1)
            y = random.randint(0, self.BOARD_HEIGHT - 1)
            
            if (x, y) not in occupied:
                game_state.food.append(Position(x=x, y=y))
                break

    def _spawn_obstacles(self, game_state: GameState) -> None:
        """Spawn obstacles based on difficulty level"""
        obstacle_count = int(game_state.difficulty.obstacle_density)
        occupied = self._get_occupied_cells(game_state)
        
        for _ in range(obstacle_count):
            # Find an unoccupied cell
            attempts = 0
            while attempts < 100:
                x = random.randint(0, self.BOARD_WIDTH - 1)
                y = random.randint(0, self.BOARD_HEIGHT - 1)
                
                if (x, y) not in occupied:
                    game_state.obstacles.append(
                        Obstacle(x=x, y=y, type='static')
                    )
                    occupied.add((x, y))
                    break
                
                attempts += 1

    def update(self, input_direction: Optional[Direction] = None) -> None:
        """Update game state with player input and game logic"""
        if self.game_state.game_over:
            return
        
        # Update direction if valid input provided
        if input_direction is not None:
            if self._is_valid_direction_change(input_direction):
                self.next_direction = input_direction
        
        # Move snake
        self.current_direction = self.next_direction
        self._move_snake()
        
        # Check collisions
        collision = self.check_collisions()
        if collision.has_collision:
            self.game_state.game_over = True
            return
        
        # Check food consumption
        self._check_food_consumption()
        
        # Update timestamp
        self.game_state.timestamp = int(time.time() * 1000)

    def _is_valid_direction_change(self, new_direction: Direction) -> bool:
        """Check if direction change is valid (not reversing into self)"""
        opposite_directions = {
            'up': 'down',
            'down': 'up',
            'left': 'right',
            'right': 'left'
        }
        
        return new_direction != opposite_directions[self.current_direction]

    def _move_snake(self) -> None:
        """Move the snake in the current direction"""
        head = self.game_state.snake[0]
        
        # Calculate new head position
        new_x, new_y = head.x, head.y
        
        if self.current_direction == 'up':
            new_y -= 1
        elif self.current_direction == 'down':
            new_y += 1
        elif self.current_direction == 'left':
            new_x -= 1
        elif self.current_direction == 'right':
            new_x += 1
        
        # Add new head
        new_head = Segment(x=new_x, y=new_y)
        self.game_state.snake.insert(0, new_head)
        
        # Remove tail (unless food was consumed, which is handled separately)
        self.game_state.snake.pop()

    def _check_food_consumption(self) -> None:
        """Check if snake head is on food and handle consumption"""
        head = self.game_state.snake[0]
        
        for i, food in enumerate(self.game_state.food):
            if head.x == food.x and head.y == food.y:
                # Remove consumed food
                self.game_state.food.pop(i)
                
                # Grow snake by adding back the tail
                tail = self.game_state.snake[-1]
                self.game_state.snake.append(tail)
                
                # Update score
                self.game_state.score += self.POINTS_PER_FOOD
                
                # Spawn new food
                self._spawn_food(self.game_state)
                
                break

    def check_collisions(self) -> CollisionResult:
        """Check for collisions with self, obstacles, or boundaries"""
        head = self.game_state.snake[0]
        
        # Check boundary collision
        if (head.x < 0 or head.x >= self.BOARD_WIDTH or
            head.y < 0 or head.y >= self.BOARD_HEIGHT):
            return CollisionResult(
                has_collision=True,
                type='boundary',
                position=Position(x=head.x, y=head.y)
            )
        
        # Check self collision (skip first segment which is the head)
        for segment in self.game_state.snake[1:]:
            if head.x == segment.x and head.y == segment.y:
                return CollisionResult(
                    has_collision=True,
                    type='self',
                    position=Position(x=head.x, y=head.y)
                )
        
        # Check obstacle collision
        for obstacle in self.game_state.obstacles:
            if head.x == obstacle.x and head.y == obstacle.y:
                return CollisionResult(
                    has_collision=True,
                    type='obstacle',
                    position=Position(x=head.x, y=head.y)
                )
        
        return CollisionResult(has_collision=False)

    def get_game_state(self) -> GameState:
        """Return current game state"""
        return self.game_state

    def reset(self) -> None:
        """Reset the game to initial state"""
        self.game_state = self._initialize_game_state()
        self.current_direction = 'right'
        self.next_direction = 'right'

    def get_snake_length(self) -> int:
        """Get current snake length"""
        return len(self.game_state.snake)

    def get_food_count(self) -> int:
        """Get current number of food items on board"""
        return len(self.game_state.food)

    def get_obstacle_count(self) -> int:
        """Get current number of obstacles on board"""
        return len(self.game_state.obstacles)
