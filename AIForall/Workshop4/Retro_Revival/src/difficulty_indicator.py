"""
Difficulty Indicator UI Component
Displays the current difficulty level (1-10) with visual representation
Requirements: 3.1
"""

from game_types import DifficultyLevel


class DifficultyIndicator:
    """Displays the current difficulty level with visual representation"""

    def __init__(self):
        """Initialize the difficulty indicator"""
        self.current_difficulty: DifficultyLevel | None = None

    def update_difficulty(self, difficulty: DifficultyLevel) -> None:
        """Update the difficulty display"""
        self.current_difficulty = difficulty

    def get_difficulty_display(self) -> str:
        """Get a string representation of the difficulty"""
        if not self.current_difficulty:
            return "No difficulty set"

        level = self.current_difficulty.level
        mode = "Adaptive" if self.current_difficulty.adaptive_mode else "Manual"
        
        # Create visual bar
        bar_length = 20
        filled = int((level / 10) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"Difficulty: {level}/10 [{bar}] {mode}"

    def get_difficulty_color(self) -> str:
        """Get color code based on difficulty level"""
        if not self.current_difficulty:
            return "NEUTRAL"
        
        level = self.current_difficulty.level
        if level <= 3:
            return "GREEN"  # Easy
        elif level <= 6:
            return "YELLOW"  # Medium
        elif level <= 8:
            return "ORANGE"  # Hard
        else:
            return "RED"  # Very Hard

    def get_difficulty_category(self) -> str:
        """Get difficulty category name"""
        if not self.current_difficulty:
            return "Unknown"
        
        level = self.current_difficulty.level
        if level <= 3:
            return "Easy"
        elif level <= 6:
            return "Medium"
        elif level <= 8:
            return "Hard"
        else:
            return "Very Hard"

    def get_current_difficulty(self) -> DifficultyLevel | None:
        """Get the current difficulty level"""
        return self.current_difficulty

    def get_difficulty_info(self) -> dict:
        """Get complete difficulty information"""
        if not self.current_difficulty:
            return {}
        
        return {
            "level": self.current_difficulty.level,
            "speed": self.current_difficulty.speed,
            "obstacle_density": self.current_difficulty.obstacle_density,
            "food_spawn_rate": self.current_difficulty.food_spawn_rate,
            "adaptive_mode": self.current_difficulty.adaptive_mode,
            "category": self.get_difficulty_category(),
            "color": self.get_difficulty_color(),
            "display": self.get_difficulty_display()
        }

    def is_adaptive_mode(self) -> bool:
        """Check if adaptive mode is enabled"""
        if not self.current_difficulty:
            return False
        return self.current_difficulty.adaptive_mode

    def get_difficulty_level(self) -> int:
        """Get the numeric difficulty level"""
        if not self.current_difficulty:
            return 0
        return self.current_difficulty.level

    def get_speed(self) -> int:
        """Get the current speed setting"""
        if not self.current_difficulty:
            return 0
        return self.current_difficulty.speed

    def get_obstacle_density(self) -> int:
        """Get the current obstacle density"""
        if not self.current_difficulty:
            return 0
        return self.current_difficulty.obstacle_density

    def get_food_spawn_rate(self) -> float:
        """Get the current food spawn rate"""
        if not self.current_difficulty:
            return 0.0
        return self.current_difficulty.food_spawn_rate
