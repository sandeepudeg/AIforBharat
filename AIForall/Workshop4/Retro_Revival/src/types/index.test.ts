/**
 * Unit tests for type definitions and interface validation
 * Requirements: 1.1
 */

import {
  Segment,
  Position,
  Obstacle,
  Direction,
  DifficultyLevel,
  GameState,
  PerformanceMetrics,
  SkillAssessment,
  DifficultyDelta,
  AdaptationDecision,
  GameSession,
  PlayerProfile,
  CollisionResult
} from './index';

describe('Type Definitions - Interface Instantiation', () => {
  describe('Segment', () => {
    it('should instantiate a valid segment', () => {
      const segment: Segment = { x: 10, y: 10 };
      expect(segment.x).toBe(10);
      expect(segment.y).toBe(10);
    });

    it('should allow zero coordinates', () => {
      const segment: Segment = { x: 0, y: 0 };
      expect(segment.x).toBe(0);
      expect(segment.y).toBe(0);
    });
  });

  describe('Position', () => {
    it('should instantiate a valid position', () => {
      const position: Position = { x: 5, y: 15 };
      expect(position.x).toBe(5);
      expect(position.y).toBe(15);
    });
  });

  describe('Obstacle', () => {
    it('should instantiate a static obstacle', () => {
      const obstacle: Obstacle = { x: 8, y: 8, type: 'static' };
      expect(obstacle.x).toBe(8);
      expect(obstacle.y).toBe(8);
      expect(obstacle.type).toBe('static');
    });

    it('should instantiate a dynamic obstacle', () => {
      const obstacle: Obstacle = { x: 12, y: 12, type: 'dynamic' };
      expect(obstacle.type).toBe('dynamic');
    });
  });

  describe('Direction', () => {
    it('should accept all valid directions', () => {
      const directions: Direction[] = ['up', 'down', 'left', 'right'];
      directions.forEach(dir => {
        expect(['up', 'down', 'left', 'right']).toContain(dir);
      });
    });
  });

  describe('DifficultyLevel', () => {
    it('should instantiate a valid difficulty level', () => {
      const difficulty: DifficultyLevel = {
        level: 5,
        speed: 5,
        obstacleDensity: 2,
        foodSpawnRate: 1.0,
        adaptiveMode: true
      };
      expect(difficulty.level).toBe(5);
      expect(difficulty.speed).toBe(5);
      expect(difficulty.obstacleDensity).toBe(2);
      expect(difficulty.foodSpawnRate).toBe(1.0);
      expect(difficulty.adaptiveMode).toBe(true);
    });

    it('should instantiate difficulty with minimum values', () => {
      const difficulty: DifficultyLevel = {
        level: 1,
        speed: 1,
        obstacleDensity: 0,
        foodSpawnRate: 0.5,
        adaptiveMode: false
      };
      expect(difficulty.level).toBe(1);
      expect(difficulty.speed).toBe(1);
      expect(difficulty.obstacleDensity).toBe(0);
      expect(difficulty.foodSpawnRate).toBe(0.5);
    });

    it('should instantiate difficulty with maximum values', () => {
      const difficulty: DifficultyLevel = {
        level: 10,
        speed: 10,
        obstacleDensity: 5,
        foodSpawnRate: 2.0,
        adaptiveMode: true
      };
      expect(difficulty.level).toBe(10);
      expect(difficulty.speed).toBe(10);
      expect(difficulty.obstacleDensity).toBe(5);
      expect(difficulty.foodSpawnRate).toBe(2.0);
    });
  });

  describe('GameState', () => {
    it('should instantiate a valid game state', () => {
      const gameState: GameState = {
        snake: [{ x: 10, y: 10 }, { x: 10, y: 11 }, { x: 10, y: 12 }],
        food: [{ x: 5, y: 5 }],
        obstacles: [{ x: 15, y: 15, type: 'static' }],
        score: 0,
        gameOver: false,
        difficulty: {
          level: 1,
          speed: 5,
          obstacleDensity: 1,
          foodSpawnRate: 1.0,
          adaptiveMode: true
        },
        timestamp: Date.now()
      };
      expect(gameState.snake.length).toBe(3);
      expect(gameState.food.length).toBe(1);
      expect(gameState.obstacles.length).toBe(1);
      expect(gameState.score).toBe(0);
      expect(gameState.gameOver).toBe(false);
    });

    it('should instantiate game state with empty food and obstacles', () => {
      const gameState: GameState = {
        snake: [{ x: 10, y: 10 }],
        food: [],
        obstacles: [],
        score: 100,
        gameOver: true,
        difficulty: {
          level: 5,
          speed: 7,
          obstacleDensity: 3,
          foodSpawnRate: 1.5,
          adaptiveMode: false
        },
        timestamp: Date.now()
      };
      expect(gameState.food.length).toBe(0);
      expect(gameState.obstacles.length).toBe(0);
      expect(gameState.score).toBe(100);
      expect(gameState.gameOver).toBe(true);
    });
  });

  describe('PerformanceMetrics', () => {
    it('should instantiate valid performance metrics', () => {
      const metrics: PerformanceMetrics = {
        survivalTime: 45.5,
        foodConsumed: 8,
        reactionTime: [150, 160, 155, 170],
        collisionsAvoided: 3,
        averageSpeed: 5.2,
        timestamp: Date.now()
      };
      expect(metrics.survivalTime).toBe(45.5);
      expect(metrics.foodConsumed).toBe(8);
      expect(metrics.reactionTime.length).toBe(4);
      expect(metrics.collisionsAvoided).toBe(3);
      expect(metrics.averageSpeed).toBe(5.2);
    });

    it('should instantiate metrics with zero values', () => {
      const metrics: PerformanceMetrics = {
        survivalTime: 0,
        foodConsumed: 0,
        reactionTime: [],
        collisionsAvoided: 0,
        averageSpeed: 0,
        timestamp: Date.now()
      };
      expect(metrics.survivalTime).toBe(0);
      expect(metrics.foodConsumed).toBe(0);
      expect(metrics.reactionTime.length).toBe(0);
    });
  });

  describe('SkillAssessment', () => {
    it('should instantiate a valid skill assessment', () => {
      const assessment: SkillAssessment = {
        skillLevel: 65,
        trend: 'improving',
        confidence: 0.85,
        lastUpdated: Date.now()
      };
      expect(assessment.skillLevel).toBe(65);
      expect(assessment.trend).toBe('improving');
      expect(assessment.confidence).toBe(0.85);
    });

    it('should instantiate skill assessment with all trend types', () => {
      const trends: Array<'improving' | 'stable' | 'declining'> = ['improving', 'stable', 'declining'];
      trends.forEach(trend => {
        const assessment: SkillAssessment = {
          skillLevel: 50,
          trend,
          confidence: 0.5,
          lastUpdated: Date.now()
        };
        expect(assessment.trend).toBe(trend);
      });
    });

    it('should instantiate skill assessment with boundary confidence values', () => {
      const lowConfidence: SkillAssessment = {
        skillLevel: 30,
        trend: 'stable',
        confidence: 0,
        lastUpdated: Date.now()
      };
      const highConfidence: SkillAssessment = {
        skillLevel: 80,
        trend: 'improving',
        confidence: 1,
        lastUpdated: Date.now()
      };
      expect(lowConfidence.confidence).toBe(0);
      expect(highConfidence.confidence).toBe(1);
    });
  });

  describe('DifficultyDelta', () => {
    it('should instantiate a valid difficulty delta', () => {
      const delta: DifficultyDelta = {
        speedDelta: 1,
        obstacleDensityDelta: 0.5,
        foodSpawnRateDelta: 0.1,
        reason: 'Player performing well'
      };
      expect(delta.speedDelta).toBe(1);
      expect(delta.obstacleDensityDelta).toBe(0.5);
      expect(delta.foodSpawnRateDelta).toBe(0.1);
      expect(delta.reason).toBe('Player performing well');
    });

    it('should instantiate delta with negative values', () => {
      const delta: DifficultyDelta = {
        speedDelta: -1,
        obstacleDensityDelta: -1,
        foodSpawnRateDelta: -0.2,
        reason: 'Player struggling'
      };
      expect(delta.speedDelta).toBe(-1);
      expect(delta.obstacleDensityDelta).toBe(-1);
      expect(delta.foodSpawnRateDelta).toBe(-0.2);
    });
  });

  describe('AdaptationDecision', () => {
    it('should instantiate a valid adaptation decision', () => {
      const decision: AdaptationDecision = {
        timestamp: Date.now(),
        metrics: {
          survivalTime: 30,
          foodConsumed: 5,
          reactionTime: [150, 160],
          collisionsAvoided: 2,
          averageSpeed: 5,
          timestamp: Date.now()
        },
        skillAssessment: {
          skillLevel: 60,
          trend: 'improving',
          confidence: 0.8,
          lastUpdated: Date.now()
        },
        difficultyDelta: {
          speedDelta: 1,
          obstacleDensityDelta: 0.5,
          foodSpawnRateDelta: 0.1,
          reason: 'Increasing difficulty'
        },
        rationale: 'Player is improving steadily'
      };
      expect(decision.metrics.foodConsumed).toBe(5);
      expect(decision.skillAssessment.skillLevel).toBe(60);
      expect(decision.difficultyDelta.speedDelta).toBe(1);
      expect(decision.rationale).toBe('Player is improving steadily');
    });
  });

  describe('GameSession', () => {
    it('should instantiate a valid game session', () => {
      const session: GameSession = {
        id: 'session-001',
        score: 150,
        duration: 120,
        difficulty: {
          level: 5,
          speed: 6,
          obstacleDensity: 2,
          foodSpawnRate: 1.2,
          adaptiveMode: true
        },
        metrics: {
          survivalTime: 120,
          foodConsumed: 15,
          reactionTime: [150, 160, 155],
          collisionsAvoided: 5,
          averageSpeed: 6,
          timestamp: Date.now()
        },
        timestamp: Date.now()
      };
      expect(session.id).toBe('session-001');
      expect(session.score).toBe(150);
      expect(session.duration).toBe(120);
      expect(session.metrics.foodConsumed).toBe(15);
    });
  });

  describe('PlayerProfile', () => {
    it('should instantiate a valid player profile', () => {
      const profile: PlayerProfile = {
        sessions: [
          {
            id: 'session-001',
            score: 100,
            duration: 60,
            difficulty: {
              level: 1,
              speed: 5,
              obstacleDensity: 1,
              foodSpawnRate: 1.0,
              adaptiveMode: true
            },
            metrics: {
              survivalTime: 60,
              foodConsumed: 10,
              reactionTime: [150],
              collisionsAvoided: 2,
              averageSpeed: 5,
              timestamp: Date.now()
            },
            timestamp: Date.now()
          }
        ],
        bestScore: 100,
        averageSurvivalTime: 60,
        skillProgression: [
          {
            skillLevel: 50,
            trend: 'stable',
            confidence: 0.7,
            lastUpdated: Date.now()
          }
        ]
      };
      expect(profile.sessions.length).toBe(1);
      expect(profile.bestScore).toBe(100);
      expect(profile.averageSurvivalTime).toBe(60);
      expect(profile.skillProgression.length).toBe(1);
    });

    it('should instantiate an empty player profile', () => {
      const profile: PlayerProfile = {
        sessions: [],
        bestScore: 0,
        averageSurvivalTime: 0,
        skillProgression: []
      };
      expect(profile.sessions.length).toBe(0);
      expect(profile.bestScore).toBe(0);
      expect(profile.skillProgression.length).toBe(0);
    });
  });

  describe('CollisionResult', () => {
    it('should instantiate a collision result with no collision', () => {
      const result: CollisionResult = {
        hasCollision: false
      };
      expect(result.hasCollision).toBe(false);
      expect(result.type).toBeUndefined();
    });

    it('should instantiate a collision result with self collision', () => {
      const result: CollisionResult = {
        hasCollision: true,
        type: 'self',
        position: { x: 10, y: 10 }
      };
      expect(result.hasCollision).toBe(true);
      expect(result.type).toBe('self');
      expect(result.position).toEqual({ x: 10, y: 10 });
    });

    it('should instantiate a collision result with obstacle collision', () => {
      const result: CollisionResult = {
        hasCollision: true,
        type: 'obstacle',
        position: { x: 15, y: 15 }
      };
      expect(result.type).toBe('obstacle');
    });

    it('should instantiate a collision result with boundary collision', () => {
      const result: CollisionResult = {
        hasCollision: true,
        type: 'boundary',
        position: { x: 20, y: 20 }
      };
      expect(result.type).toBe('boundary');
    });
  });
});
