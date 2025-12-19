"""
Game Loop and Input Handler
Manages the main game loop, input handling, and component integration
Requirements: 1.2, 2.2, 2.3, 2.4
"""

import time
from typing import Optional, Callable, List
from enum import Enum
from game_types import Direction, GameState, PerformanceMetrics
from game_engine import GameEngine
from adaptation_engine import AdaptationEngine
from difficulty_manager import DifficultyManager
from metrics_collector import MetricsCollector


class GameLoopState(Enum):
    """Enumeration of game loop states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class InputHandler:
    """Handles player input for directional controls"""

    def __init__(self):
        """Initialize input handler"""
        self.pending_input: Optional[Direction] = None
        self.last_input_time: int = 0

    def queue_input(self, direction: Direction) -> None:
        """Queue a directional input from the player"""
        self.pending_input = direction
        self.last_input_time = int(time.time() * 1000)

    def get_pending_input(self) -> Optional[Direction]:
        """Get and clear the pending input"""
        input_dir = self.pending_input
        self.pending_input = None
        return input_dir

    def has_pending_input(self) -> bool:
        """Check if there's a pending input"""
        return self.pending_input is not None

    def clear_input(self) -> None:
        """Clear any pending input"""
        self.pending_input = None


class GameLoop:
    """Main game loop that integrates all components"""

    def __init__(
        self,
        game_engine: Optional[GameEngine] = None,
        adaptation_engine: Optional[AdaptationEngine] = None,
        difficulty_manager: Optional[DifficultyManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        tick_rate: int = 10
    ):
        """
        Initialize the game loop with all components
        
        Args:
            game_engine: The game engine (created if not provided)
            adaptation_engine: The adaptation engine (created if not provided)
            difficulty_manager: The difficulty manager (created if not provided)
            metrics_collector: The metrics collector (created if not provided)
            tick_rate: Game ticks per second (default 10)
        """
        self.game_engine = game_engine or GameEngine()
        self.adaptation_engine = adaptation_engine or AdaptationEngine()
        self.difficulty_manager = difficulty_manager or DifficultyManager()
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        self.input_handler = InputHandler()
        self.tick_rate = tick_rate
        self.tick_duration_ms = 1000 / tick_rate
        
        self.state = GameLoopState.IDLE
        self.last_tick_time: int = 0
        self.session_start_time: int = 0
        self.adaptation_interval_ms = 5000  # Adapt every 5 seconds
        self.last_adaptation_time: int = 0
        self.previous_score: int = 0
        
        # Callbacks for UI updates
        self.on_game_state_changed: Optional[Callable[[GameState], None]] = None
        self.on_difficulty_changed: Optional[Callable[[str], None]] = None
        self.on_game_over: Optional[Callable[[GameState, PerformanceMetrics], None]] = None

    def start_game(self) -> None:
        """Start a new game session"""
        self.game_engine.reset()
        self.metrics_collector.start_session()
        self.state = GameLoopState.RUNNING
        self.session_start_time = int(time.time() * 1000)
        self.last_tick_time = self.session_start_time
        self.last_adaptation_time = self.session_start_time
        self.previous_score = 0

    def pause_game(self) -> None:
        """Pause the current game"""
        if self.state == GameLoopState.RUNNING:
            self.state = GameLoopState.PAUSED
            self.metrics_collector.pause_session()

    def resume_game(self) -> None:
        """Resume a paused game"""
        if self.state == GameLoopState.PAUSED:
            self.state = GameLoopState.RUNNING
            self.metrics_collector.resume_session()
            self.last_tick_time = int(time.time() * 1000)

    def end_game(self) -> None:
        """End the current game session"""
        self.state = GameLoopState.GAME_OVER

    def is_running(self) -> bool:
        """Check if the game loop is running"""
        return self.state == GameLoopState.RUNNING

    def is_paused(self) -> bool:
        """Check if the game is paused"""
        return self.state == GameLoopState.PAUSED

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.state == GameLoopState.GAME_OVER

    def queue_input(self, direction: Direction) -> None:
        """Queue player input"""
        self.input_handler.queue_input(direction)

    def update(self) -> bool:
        """
        Update the game state for one tick
        Returns True if the game is still running, False if game over
        """
        if not self.is_running():
            return not self.is_game_over()

        current_time = int(time.time() * 1000)
        elapsed_since_last_tick = current_time - self.last_tick_time

        # Check if enough time has passed for a tick
        if elapsed_since_last_tick < self.tick_duration_ms:
            return True

        # Process input
        input_direction = self.input_handler.get_pending_input()
        if input_direction:
            self.metrics_collector.record_input()

        # Update game engine
        self.game_engine.update(input_direction)
        
        # Collect metrics
        game_state = self.game_engine.get_game_state()
        self.metrics_collector.record_movement()
        
        # Check for food consumption (score increases by 10 per food)
        current_score = game_state.score
        if current_score > self.previous_score:
            food_eaten = (current_score - self.previous_score) // 10
            for _ in range(food_eaten):
                self.metrics_collector.record_food_consumption()
        self.previous_score = current_score

        # Check for game over
        if game_state.game_over:
            self.end_game()
            self._handle_game_over()
            return False

        # Notify UI of state change
        if self.on_game_state_changed:
            self.on_game_state_changed(game_state)

        # Check if it's time to adapt difficulty
        if self.difficulty_manager.is_adaptive_mode_enabled():
            if current_time - self.last_adaptation_time >= self.adaptation_interval_ms:
                self._perform_adaptation()
                self.last_adaptation_time = current_time

        self.last_tick_time = current_time
        return True

    def _perform_adaptation(self) -> None:
        """Perform difficulty adaptation based on current metrics"""
        # Get current metrics
        metrics = self.metrics_collector.get_metrics()
        
        if metrics is None:
            return

        # Assess player skill
        assessment = self.adaptation_engine.assess_player_skill(metrics)

        # Calculate difficulty adjustment
        delta = self.adaptation_engine.calculate_difficulty_adjustment(assessment)

        # Record the decision
        rationale = f"Skill: {assessment.skill_level}/100 ({assessment.trend})"
        self.adaptation_engine.record_adaptation_decision(
            metrics, assessment, delta, rationale
        )

        # Apply the adjustment
        if self.difficulty_manager.apply_difficulty_adjustment(delta):
            # Update game engine with new difficulty
            new_difficulty = self.difficulty_manager.get_current_difficulty()
            self.game_engine.difficulty = new_difficulty
            self.game_engine.game_state.difficulty = new_difficulty

            # Notify UI
            if self.on_difficulty_changed:
                self.on_difficulty_changed(delta.reason)

    def _handle_game_over(self) -> None:
        """Handle game over event"""
        game_state = self.game_engine.get_game_state()
        metrics = self.metrics_collector.get_metrics()

        if self.on_game_over and metrics:
            self.on_game_over(game_state, metrics)

    def get_game_state(self) -> GameState:
        """Get the current game state"""
        return self.game_engine.get_game_state()

    def get_current_difficulty(self):
        """Get the current difficulty level"""
        return self.difficulty_manager.get_current_difficulty()

    def set_manual_difficulty(self, difficulty) -> bool:
        """Set manual difficulty (disables adaptive mode)"""
        # Create a copy with adaptive_mode disabled
        manual_difficulty = difficulty
        manual_difficulty.adaptive_mode = False
        self.difficulty_manager.disable_adaptive_mode()
        return self.difficulty_manager.set_manual_difficulty(manual_difficulty)

    def enable_adaptive_mode(self) -> None:
        """Enable adaptive difficulty mode"""
        self.difficulty_manager.enable_adaptive_mode()

    def disable_adaptive_mode(self) -> None:
        """Disable adaptive difficulty mode"""
        self.difficulty_manager.disable_adaptive_mode()

    def is_adaptive_mode_enabled(self) -> bool:
        """Check if adaptive mode is enabled"""
        return self.difficulty_manager.is_adaptive_mode_enabled()

    def get_session_duration(self) -> float:
        """Get the duration of the current session in seconds"""
        if self.session_start_time == 0:
            return 0.0
        current_time = int(time.time() * 1000)
        return (current_time - self.session_start_time) / 1000.0

    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        return self.metrics_collector.get_metrics()

    def set_on_game_state_changed(self, callback: Callable[[GameState], None]) -> None:
        """Set callback for game state changes"""
        self.on_game_state_changed = callback

    def set_on_difficulty_changed(self, callback: Callable[[str], None]) -> None:
        """Set callback for difficulty changes"""
        self.on_difficulty_changed = callback

    def set_on_game_over(self, callback: Callable[[GameState, PerformanceMetrics], None]) -> None:
        """Set callback for game over event"""
        self.on_game_over = callback
