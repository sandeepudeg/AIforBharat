"""
Difficulty management system
Handles difficulty level tracking and parameter management
Requirements: 2.2, 2.3, 2.4, 4.2, 4.3, 6.4
"""

import time
from typing import Optional
from game_types import DifficultyLevel, DifficultyDelta


class DifficultyManager:
    """Manages game difficulty and parameter transitions"""

    # Parameter bounds
    SPEED_MIN = 1
    SPEED_MAX = 10
    OBSTACLE_DENSITY_MIN = 0
    OBSTACLE_DENSITY_MAX = 5
    FOOD_SPAWN_RATE_MIN = 0.5
    FOOD_SPAWN_RATE_MAX = 2.0
    DIFFICULTY_LEVEL_MIN = 1
    DIFFICULTY_LEVEL_MAX = 10

    # Transition settings
    TRANSITION_DURATION_MS = 2500  # 2.5 seconds for smooth transitions

    def __init__(self, initial_difficulty: Optional[DifficultyLevel] = None):
        """Initialize difficulty manager"""
        if initial_difficulty is None:
            initial_difficulty = DifficultyLevel(
                level=1,
                speed=5,
                obstacle_density=1,
                food_spawn_rate=1.0,
                adaptive_mode=True
            )

        self.current_difficulty = initial_difficulty
        self.target_difficulty = initial_difficulty
        self.transition_start_time: Optional[int] = None
        self.transition_in_progress = False

    def get_current_difficulty(self) -> DifficultyLevel:
        """Get current difficulty level"""
        if self.transition_in_progress:
            self._update_transition()

        return self.current_difficulty

    def set_manual_difficulty(self, difficulty: DifficultyLevel) -> bool:
        """
        Set manual difficulty level
        Returns True if successful, False if parameters are out of bounds
        """
        if not self.validate_parameters(difficulty):
            return False

        self.current_difficulty = difficulty
        self.target_difficulty = difficulty
        self.transition_in_progress = False
        return True

    def apply_difficulty_adjustment(self, delta: DifficultyDelta) -> bool:
        """
        Apply difficulty adjustment with smooth transition
        Returns True if adjustment was applied, False if it would exceed bounds
        """
        # Calculate new parameters
        new_speed = self.current_difficulty.speed + delta.speed_delta
        new_obstacle_density = (
            self.current_difficulty.obstacle_density + delta.obstacle_density_delta
        )
        new_food_spawn_rate = (
            self.current_difficulty.food_spawn_rate + delta.food_spawn_rate_delta
        )

        # Calculate new difficulty level
        new_level = self._calculate_difficulty_level(
            new_speed, new_obstacle_density, new_food_spawn_rate
        )

        # Create target difficulty
        target = DifficultyLevel(
            level=new_level,
            speed=new_speed,
            obstacle_density=new_obstacle_density,
            food_spawn_rate=new_food_spawn_rate,
            adaptive_mode=self.current_difficulty.adaptive_mode
        )

        # Validate before applying
        if not self.validate_parameters(target):
            return False

        # Set target and start transition
        self.target_difficulty = target
        self.transition_start_time = int(time.time() * 1000)
        self.transition_in_progress = True

        return True

    def _update_transition(self) -> None:
        """Update smooth transition between difficulties"""
        if not self.transition_in_progress or self.transition_start_time is None:
            return

        current_time = int(time.time() * 1000)
        elapsed = current_time - self.transition_start_time

        if elapsed >= self.TRANSITION_DURATION_MS:
            # Transition complete
            self.current_difficulty = self.target_difficulty
            self.transition_in_progress = False
            return

        # Calculate progress (0.0 to 1.0)
        progress = elapsed / self.TRANSITION_DURATION_MS

        # Interpolate parameters
        interpolated_speed = self._interpolate(
            self.current_difficulty.speed,
            self.target_difficulty.speed,
            progress
        )

        interpolated_obstacle_density = self._interpolate(
            self.current_difficulty.obstacle_density,
            self.target_difficulty.obstacle_density,
            progress
        )

        interpolated_food_spawn_rate = self._interpolate(
            self.current_difficulty.food_spawn_rate,
            self.target_difficulty.food_spawn_rate,
            progress
        )

        # Update current difficulty with interpolated values
        self.current_difficulty = DifficultyLevel(
            level=self.target_difficulty.level,
            speed=interpolated_speed,
            obstacle_density=interpolated_obstacle_density,
            food_spawn_rate=interpolated_food_spawn_rate,
            adaptive_mode=self.current_difficulty.adaptive_mode
        )

    def _interpolate(self, start: float, end: float, progress: float) -> float:
        """Linear interpolation between two values"""
        return start + (end - start) * progress

    def _calculate_difficulty_level(
        self, speed: float, obstacle_density: float, food_spawn_rate: float
    ) -> int:
        """Calculate overall difficulty level from parameters"""
        # Normalize parameters to 0-1 range
        speed_norm = (speed - self.SPEED_MIN) / (self.SPEED_MAX - self.SPEED_MIN)
        obstacle_norm = (
            (obstacle_density - self.OBSTACLE_DENSITY_MIN) /
            (self.OBSTACLE_DENSITY_MAX - self.OBSTACLE_DENSITY_MIN)
        )
        food_norm = (
            (food_spawn_rate - self.FOOD_SPAWN_RATE_MIN) /
            (self.FOOD_SPAWN_RATE_MAX - self.FOOD_SPAWN_RATE_MIN)
        )

        # Weighted average
        difficulty_norm = (
            speed_norm * 0.5 + obstacle_norm * 0.3 + food_norm * 0.2
        )

        # Convert to 1-10 scale
        level = int(
            self.DIFFICULTY_LEVEL_MIN +
            difficulty_norm * (self.DIFFICULTY_LEVEL_MAX - self.DIFFICULTY_LEVEL_MIN)
        )

        return max(self.DIFFICULTY_LEVEL_MIN, min(self.DIFFICULTY_LEVEL_MAX, level))

    def validate_parameters(self, difficulty: DifficultyLevel) -> bool:
        """Validate difficulty parameters are within bounds"""
        if not (self.DIFFICULTY_LEVEL_MIN <= difficulty.level <= self.DIFFICULTY_LEVEL_MAX):
            return False

        if not (self.SPEED_MIN <= difficulty.speed <= self.SPEED_MAX):
            return False

        if not (
            self.OBSTACLE_DENSITY_MIN <= difficulty.obstacle_density <=
            self.OBSTACLE_DENSITY_MAX
        ):
            return False

        if not (
            self.FOOD_SPAWN_RATE_MIN <= difficulty.food_spawn_rate <=
            self.FOOD_SPAWN_RATE_MAX
        ):
            return False

        return True

    def enable_adaptive_mode(self) -> None:
        """Enable adaptive difficulty mode"""
        self.current_difficulty.adaptive_mode = True
        self.target_difficulty.adaptive_mode = True

    def disable_adaptive_mode(self) -> None:
        """Disable adaptive difficulty mode"""
        self.current_difficulty.adaptive_mode = False
        self.target_difficulty.adaptive_mode = False

    def is_adaptive_mode_enabled(self) -> bool:
        """Check if adaptive mode is enabled"""
        return self.current_difficulty.adaptive_mode

    def clamp_parameters(self, difficulty: DifficultyLevel) -> DifficultyLevel:
        """Clamp difficulty parameters to valid bounds"""
        return DifficultyLevel(
            level=max(
                self.DIFFICULTY_LEVEL_MIN,
                min(self.DIFFICULTY_LEVEL_MAX, difficulty.level)
            ),
            speed=max(
                self.SPEED_MIN,
                min(self.SPEED_MAX, difficulty.speed)
            ),
            obstacle_density=max(
                self.OBSTACLE_DENSITY_MIN,
                min(self.OBSTACLE_DENSITY_MAX, difficulty.obstacle_density)
            ),
            food_spawn_rate=max(
                self.FOOD_SPAWN_RATE_MIN,
                min(self.FOOD_SPAWN_RATE_MAX, difficulty.food_spawn_rate)
            ),
            adaptive_mode=difficulty.adaptive_mode
        )
