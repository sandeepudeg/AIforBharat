# Design Document: Snake with Adaptive Difficulty AI

## Overview

The Snake Adaptive AI system is a modern recreation of the classic Snake game with an intelligent difficulty adaptation engine. The architecture separates concerns into three primary layers:

1. **Game Engine**: Handles core Snake mechanics (movement, collision, scoring)
2. **Adaptation Engine**: Analyzes player performance and adjusts difficulty parameters
3. **UI/Presentation Layer**: Renders the game state and displays adaptation feedback

The system uses a performance-based skill assessment model that continuously monitors player behavior and adjusts game parameters (speed, obstacle density, food spawn rate) to maintain an optimal challenge level. All adaptation decisions are logged and explainable, enabling both players and developers to understand why the game is changing.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UI/Presentation Layer                    │
│  (Game Board, Score Display, Difficulty Indicator, Menus)   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Game Engine Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Snake Logic  │  │ Collision    │  │ Food/Obstacle│      │
│  │ & Movement   │  │ Detection    │  │ Management   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Adaptation Engine Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Performance  │  │ Skill        │  │ Difficulty   │      │
│  │ Metrics      │  │ Assessment   │  │ Adjustment   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Storage & Persistence Layer                     │
│  (Local Storage for Game History, Settings, Metrics)        │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Game Engine

**GameState Interface**
```typescript
interface GameState {
  snake: Segment[];           // Array of snake segments
  food: Position[];           // Array of food positions
  obstacles: Obstacle[];      // Array of obstacles
  score: number;              // Current score
  gameOver: boolean;          // Game status
  difficulty: DifficultyLevel; // Current difficulty parameters
  timestamp: number;          // Game tick timestamp
}

interface Segment {
  x: number;
  y: number;
}

interface Position {
  x: number;
  y: number;
}

interface Obstacle {
  x: number;
  y: number;
  type: 'static' | 'dynamic';
}
```

**GameEngine Class**
- `update(input: Direction): void` - Process player input and update game state
- `checkCollisions(): CollisionResult` - Detect snake collisions with food, obstacles, self
- `spawnFood(): void` - Generate new food at random position
- `spawnObstacles(count: number): void` - Generate obstacles based on difficulty
- `getGameState(): GameState` - Return current game state
- `reset(): void` - Initialize new game session

### 2. Adaptation Engine

**PerformanceMetrics Interface**
```typescript
interface PerformanceMetrics {
  survivalTime: number;       // Seconds survived in last session
  foodConsumed: number;       // Number of food items eaten
  reactionTime: number[];     // Array of reaction times (ms) for each move
  collisionsAvoided: number;  // Number of near-misses
  averageSpeed: number;       // Average movement speed
  timestamp: number;          // When metrics were recorded
}

interface SkillAssessment {
  skillLevel: number;         // 0-100 scale
  trend: 'improving' | 'stable' | 'declining';
  confidence: number;         // 0-1 confidence in assessment
  lastUpdated: number;        // Timestamp of last assessment
}
```

**AdaptationEngine Class**
- `assessPlayerSkill(metrics: PerformanceMetrics): SkillAssessment` - Evaluate player ability
- `calculateDifficultyAdjustment(assessment: SkillAssessment): DifficultyDelta` - Determine parameter changes
- `applyDifficultyAdjustment(delta: DifficultyDelta): void` - Update game parameters smoothly
- `getAdaptationRationale(): string` - Explain recent adaptation decisions
- `recordMetrics(metrics: PerformanceMetrics): void` - Store performance data

### 3. Difficulty System

**DifficultyLevel Interface**
```typescript
interface DifficultyLevel {
  level: number;              // 1-10 difficulty scale
  speed: number;              // 1-10 (game ticks per move)
  obstacleDensity: number;    // 0-5 (number of obstacles)
  foodSpawnRate: number;      // 0.5-2.0 (multiplier on spawn frequency)
  adaptiveMode: boolean;      // Whether AI is controlling difficulty
}

interface DifficultyDelta {
  speedDelta: number;
  obstacleDensityDelta: number;
  foodSpawnRateDelta: number;
  reason: string;             // Explanation for changes
}
```

**DifficultyManager Class**
- `getCurrentDifficulty(): DifficultyLevel` - Get current parameters
- `setManualDifficulty(level: DifficultyLevel): void` - Set manual parameters
- `enableAdaptiveMode(): void` - Activate AI-driven adjustment
- `disableAdaptiveMode(): void` - Freeze parameters
- `validateParameters(level: DifficultyLevel): boolean` - Ensure parameters are within bounds

### 4. Storage & Persistence

**GameSession Interface**
```typescript
interface GameSession {
  id: string;
  score: number;
  duration: number;
  difficulty: DifficultyLevel;
  metrics: PerformanceMetrics;
  timestamp: number;
}

interface PlayerProfile {
  sessions: GameSession[];
  bestScore: number;
  averageSurvivalTime: number;
  skillProgression: SkillAssessment[];
}
```

**StorageManager Class**
- `saveSession(session: GameSession): void` - Persist game session
- `loadPlayerProfile(): PlayerProfile` - Retrieve player history
- `getRecentSessions(count: number): GameSession[]` - Get last N sessions
- `calculateSkillTrend(): 'improving' | 'stable' | 'declining'` - Analyze progression

## Data Models

### Game Board
- **Dimensions**: 20x20 grid (configurable)
- **Coordinate System**: (0,0) at top-left, x increases right, y increases down
- **Occupancy**: Each cell can contain snake segment, food, or obstacle (mutually exclusive)

### Snake
- **Initial State**: 3 segments at center of board
- **Growth**: +1 segment per food consumed
- **Movement**: One cell per game tick in current direction
- **Collision**: Game ends if snake hits itself or obstacle

### Food
- **Spawn**: Random unoccupied cell
- **Consumption**: Increases score by 10 points, grows snake by 1 segment
- **Respawn**: New food spawns immediately after consumption

### Obstacles
- **Static**: Fixed positions that don't move
- **Dynamic**: Move in predictable patterns (future enhancement)
- **Density**: Controlled by difficulty level (0-5 obstacles)
- **Placement**: Random unoccupied cells, avoiding snake and food

### Performance Metrics Collection
- **Reaction Time**: Measured from game tick to player input
- **Survival Time**: Duration from game start to end
- **Food Consumption Rate**: Food items per minute
- **Collision Avoidance**: Near-misses detected when snake is adjacent to obstacle

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Snake Growth Consistency
*For any* game session where the player consumes N food items, the snake's length should increase by exactly N segments from its initial length of 3.

**Validates: Requirements 1.3**

### Property 2: Score Calculation Accuracy
*For any* game session, the final score should equal the number of food items consumed multiplied by 10 points per item.

**Validates: Requirements 1.3**

### Property 3: Collision Detection Completeness
*For any* snake position and obstacle configuration, if the snake's head occupies the same cell as an obstacle or the snake's body, the game should immediately end.

**Validates: Requirements 1.4**

### Property 4: Food Spawn Validity
*For any* game state, newly spawned food should always occupy a cell that is not currently occupied by the snake, obstacles, or existing food.

**Validates: Requirements 1.5**

### Property 5: Difficulty Bounds Enforcement
*For any* difficulty adjustment, all resulting parameters should remain within defined bounds: speed [1-10], obstacle density [0-5], food spawn rate [0.5-2.0].

**Validates: Requirements 6.4**

### Property 6: Skill Assessment Consistency
*For any* two identical performance metric sets, the skill assessment should produce identical skill level scores and trend classifications.

**Validates: Requirements 2.1**

### Property 7: Difficulty Adaptation Monotonicity
*For any* sequence of improving performance metrics, the difficulty level should never decrease; conversely, for declining metrics, difficulty should never increase.

**Validates: Requirements 2.2, 2.3**

### Property 8: Adaptation Decision Logging
*For any* difficulty adjustment made by the adaptation engine, a log entry should be created containing the decision rationale, input metrics, and calculated adjustment.

**Validates: Requirements 6.1**

### Property 9: Game State Persistence Round-Trip
*For any* game session, serializing the game state to storage and deserializing it should produce an equivalent game state with identical snake position, food locations, score, and difficulty parameters.

**Validates: Requirements 5.1**

### Property 10: Difficulty Parameter Smoothness
*For any* difficulty adjustment, the transition from old to new parameters should occur over 2-3 seconds without abrupt jumps in speed or obstacle density.

**Validates: Requirements 2.4**

## Error Handling

### Game Engine Errors
- **Invalid Direction**: Reject direction changes that would cause immediate self-collision (e.g., moving left when moving right)
- **Out of Bounds**: Prevent snake from moving outside board boundaries (wrap-around or collision)
- **Corrupted Game State**: Detect and recover from inconsistent state (duplicate segments, invalid positions)

### Adaptation Engine Errors
- **Invalid Metrics**: Reject performance metrics with out-of-range values
- **Skill Assessment Failure**: Fall back to neutral difficulty if assessment cannot be computed
- **Parameter Validation**: Clamp difficulty parameters to valid ranges before applying

### Storage Errors
- **Persistence Failure**: Log error and continue with in-memory state if storage is unavailable
- **Corrupted Data**: Validate loaded data and discard corrupted sessions
- **Storage Quota**: Implement session pruning if storage quota is exceeded

## Testing Strategy

### Unit Testing
- Test snake movement in all directions
- Test collision detection with obstacles and self
- Test food spawning and consumption
- Test difficulty parameter validation and bounds enforcement
- Test performance metrics calculation
- Test skill assessment logic with various metric combinations
- Test game state serialization/deserialization

### Property-Based Testing
- **Property 1**: Generate random food consumption sequences and verify snake length
- **Property 2**: Generate random food counts and verify score calculation
- **Property 3**: Generate random snake positions and obstacle placements, verify collision detection
- **Property 4**: Generate random game states and verify food spawns in valid locations
- **Property 5**: Generate random difficulty adjustments and verify all parameters stay in bounds
- **Property 6**: Generate identical performance metrics and verify consistent skill assessment
- **Property 7**: Generate improving/declining metric sequences and verify monotonic difficulty changes
- **Property 8**: Generate difficulty adjustments and verify log entries are created
- **Property 9**: Generate game sessions, serialize/deserialize, and verify equivalence
- **Property 10**: Generate difficulty transitions and verify smooth parameter changes over time

### Testing Framework
- **Unit Tests**: Jest (TypeScript/JavaScript)
- **Property-Based Tests**: fast-check (JavaScript/TypeScript)
- **Minimum Iterations**: 100 per property-based test
- **Coverage Target**: >85% code coverage for core game logic and adaptation engine

