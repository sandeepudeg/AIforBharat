"""
Performance metrics collection system
Tracks player performance data for skill assessment
Requirements: 2.1
"""

import time
from typing import List, Optional
from game_types import PerformanceMetrics


class MetricsCollector:
    """Collects and manages performance metrics during gameplay"""

    def __init__(self):
        """Initialize metrics collector"""
        self.session_start_time: Optional[int] = None
        self.pause_start_time: Optional[int] = None
        self.total_pause_time: int = 0
        self.reaction_times: List[int] = []
        self.food_consumed: int = 0
        self.collisions_avoided: int = 0
        self.last_input_time: Optional[int] = None
        self.total_distance: int = 0
        self.move_count: int = 0

    def start_session(self) -> None:
        """Start a new metrics collection session"""
        self.session_start_time = int(time.time() * 1000)
        self.pause_start_time = None
        self.total_pause_time = 0
        self.reaction_times = []
        self.food_consumed = 0
        self.collisions_avoided = 0
        self.last_input_time = None
        self.total_distance = 0
        self.move_count = 0

    def record_input(self) -> None:
        """Record player input for reaction time measurement"""
        current_time = int(time.time() * 1000)
        
        if self.last_input_time is not None:
            reaction_time = current_time - self.last_input_time
            self.reaction_times.append(reaction_time)
        
        self.last_input_time = current_time

    def record_food_consumption(self) -> None:
        """Record food consumption"""
        self.food_consumed += 1

    def record_collision_avoided(self) -> None:
        """Record a collision that was avoided"""
        self.collisions_avoided += 1

    def record_movement(self, distance: int = 1) -> None:
        """Record snake movement"""
        self.total_distance += distance
        self.move_count += 1

    def pause_session(self) -> None:
        """Pause the metrics collection session"""
        if self.pause_start_time is None:
            self.pause_start_time = int(time.time() * 1000)

    def resume_session(self) -> None:
        """Resume the metrics collection session"""
        if self.pause_start_time is not None:
            pause_duration = int(time.time() * 1000) - self.pause_start_time
            self.total_pause_time += pause_duration
            self.pause_start_time = None

    def get_survival_time(self) -> float:
        """Get survival time in seconds (excluding pause time)"""
        if self.session_start_time is None:
            return 0.0
        
        current_time = int(time.time() * 1000)
        total_elapsed = current_time - self.session_start_time
        
        # If currently paused, add the current pause duration
        current_pause_duration = 0
        if self.pause_start_time is not None:
            current_pause_duration = current_time - self.pause_start_time
        
        # Subtract all pause time from total elapsed
        active_time = total_elapsed - self.total_pause_time - current_pause_duration
        return max(0.0, active_time / 1000.0)

    def get_average_reaction_time(self) -> float:
        """Get average reaction time in milliseconds"""
        if not self.reaction_times:
            return 0.0
        
        return sum(self.reaction_times) / len(self.reaction_times)

    def get_food_consumption_rate(self) -> float:
        """Get food consumption rate (items per minute)"""
        survival_time = self.get_survival_time()
        if survival_time == 0:
            return 0.0
        
        minutes = survival_time / 60.0
        return self.food_consumed / minutes if minutes > 0 else 0.0

    def get_average_speed(self) -> float:
        """Get average speed (moves per second)"""
        survival_time = self.get_survival_time()
        if survival_time == 0:
            return 0.0
        
        return self.move_count / survival_time

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return PerformanceMetrics(
            survival_time=self.get_survival_time(),
            food_consumed=self.food_consumed,
            reaction_time=self.reaction_times.copy(),
            collisions_avoided=self.collisions_avoided,
            average_speed=self.get_average_speed(),
            timestamp=int(time.time() * 1000)
        )

    def validate_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Validate metrics are within acceptable ranges"""
        # Survival time should be non-negative
        if metrics.survival_time < 0:
            return False
        
        # Food consumed should be non-negative
        if metrics.food_consumed < 0:
            return False
        
        # Reaction times should be positive
        for rt in metrics.reaction_time:
            if rt < 0:
                return False
        
        # Collisions avoided should be non-negative
        if metrics.collisions_avoided < 0:
            return False
        
        # Average speed should be non-negative
        if metrics.average_speed < 0:
            return False
        
        return True
