"""
Core type definitions for Snake Adaptive AI game
"""

from dataclasses import dataclass, field
from typing import List, Literal, Optional
from enum import Enum


# ============================================================================
# Game Engine Types
# ============================================================================

@dataclass
class Segment:
    """Represents a segment of the snake"""
    x: int
    y: int


@dataclass
class Position:
    """Represents a position on the game board"""
    x: int
    y: int


@dataclass
class Obstacle:
    """Represents an obstacle on the game board"""
    x: int
    y: int
    type: Literal['static', 'dynamic']


Direction = Literal['up', 'down', 'left', 'right']


@dataclass
class DifficultyLevel:
    """Represents the current difficulty settings"""
    level: int                  # 1-10 difficulty scale
    speed: int                  # 1-10 (game ticks per move)
    obstacle_density: int       # 0-5 (number of obstacles)
    food_spawn_rate: float      # 0.5-2.0 (multiplier on spawn frequency)
    adaptive_mode: bool         # Whether AI is controlling difficulty


@dataclass
class GameState:
    """Represents the complete state of the game"""
    snake: List[Segment]        # Array of snake segments
    food: List[Position]        # Array of food positions
    obstacles: List[Obstacle]   # Array of obstacles
    score: int                  # Current score
    game_over: bool             # Game status
    difficulty: DifficultyLevel # Current difficulty parameters
    timestamp: int              # Game tick timestamp


# ============================================================================
# Performance Metrics Types
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Represents player performance data"""
    survival_time: float        # Seconds survived in last session
    food_consumed: int          # Number of food items eaten
    reaction_time: List[int]    # Array of reaction times (ms) for each move
    collisions_avoided: int     # Number of near-misses
    average_speed: float        # Average movement speed
    timestamp: int              # When metrics were recorded


@dataclass
class SkillAssessment:
    """Represents the AI's assessment of player skill"""
    skill_level: int            # 0-100 scale
    trend: Literal['improving', 'stable', 'declining']
    confidence: float           # 0-1 confidence in assessment
    last_updated: int           # Timestamp of last assessment


# ============================================================================
# Adaptation Engine Types
# ============================================================================

@dataclass
class DifficultyDelta:
    """Represents a change in difficulty parameters"""
    speed_delta: float
    obstacle_density_delta: float
    food_spawn_rate_delta: float
    reason: str                 # Explanation for changes


@dataclass
class AdaptationDecision:
    """Represents a decision made by the adaptation engine"""
    timestamp: int
    metrics: PerformanceMetrics
    skill_assessment: SkillAssessment
    difficulty_delta: DifficultyDelta
    rationale: str


# ============================================================================
# Storage & Persistence Types
# ============================================================================

@dataclass
class GameSession:
    """Represents a complete game session"""
    id: str
    score: int
    duration: int
    difficulty: DifficultyLevel
    metrics: PerformanceMetrics
    timestamp: int


@dataclass
class PlayerProfile:
    """Represents a player's profile and history"""
    sessions: List[GameSession] = field(default_factory=list)
    best_score: int = 0
    average_survival_time: float = 0.0
    skill_progression: List[SkillAssessment] = field(default_factory=list)


# ============================================================================
# Collision Detection Types
# ============================================================================

@dataclass
class CollisionResult:
    """Represents the result of a collision check"""
    has_collision: bool
    type: Optional[Literal['self', 'obstacle', 'boundary']] = None
    position: Optional[Position] = None
