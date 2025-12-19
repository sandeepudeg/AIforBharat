/**
 * Core type definitions for Snake Adaptive AI game
 */

// ============================================================================
// Game Engine Types
// ============================================================================

export interface Segment {
  x: number;
  y: number;
}

export interface Position {
  x: number;
  y: number;
}

export interface Obstacle {
  x: number;
  y: number;
  type: 'static' | 'dynamic';
}

export type Direction = 'up' | 'down' | 'left' | 'right';

export interface DifficultyLevel {
  level: number;              // 1-10 difficulty scale
  speed: number;              // 1-10 (game ticks per move)
  obstacleDensity: number;    // 0-5 (number of obstacles)
  foodSpawnRate: number;      // 0.5-2.0 (multiplier on spawn frequency)
  adaptiveMode: boolean;      // Whether AI is controlling difficulty
}

export interface GameState {
  snake: Segment[];           // Array of snake segments
  food: Position[];           // Array of food positions
  obstacles: Obstacle[];      // Array of obstacles
  score: number;              // Current score
  gameOver: boolean;          // Game status
  difficulty: DifficultyLevel; // Current difficulty parameters
  timestamp: number;          // Game tick timestamp
}

// ============================================================================
// Performance Metrics Types
// ============================================================================

export interface PerformanceMetrics {
  survivalTime: number;       // Seconds survived in last session
  foodConsumed: number;       // Number of food items eaten
  reactionTime: number[];     // Array of reaction times (ms) for each move
  collisionsAvoided: number;  // Number of near-misses
  averageSpeed: number;       // Average movement speed
  timestamp: number;          // When metrics were recorded
}

export interface SkillAssessment {
  skillLevel: number;         // 0-100 scale
  trend: 'improving' | 'stable' | 'declining';
  confidence: number;         // 0-1 confidence in assessment
  lastUpdated: number;        // Timestamp of last assessment
}

// ============================================================================
// Adaptation Engine Types
// ============================================================================

export interface DifficultyDelta {
  speedDelta: number;
  obstacleDensityDelta: number;
  foodSpawnRateDelta: number;
  reason: string;             // Explanation for changes
}

export interface AdaptationDecision {
  timestamp: number;
  metrics: PerformanceMetrics;
  skillAssessment: SkillAssessment;
  difficultyDelta: DifficultyDelta;
  rationale: string;
}

// ============================================================================
// Storage & Persistence Types
// ============================================================================

export interface GameSession {
  id: string;
  score: number;
  duration: number;
  difficulty: DifficultyLevel;
  metrics: PerformanceMetrics;
  timestamp: number;
}

export interface PlayerProfile {
  sessions: GameSession[];
  bestScore: number;
  averageSurvivalTime: number;
  skillProgression: SkillAssessment[];
}

// ============================================================================
// Collision Detection Types
// ============================================================================

export interface CollisionResult {
  hasCollision: boolean;
  type?: 'self' | 'obstacle' | 'boundary';
  position?: Position;
}
