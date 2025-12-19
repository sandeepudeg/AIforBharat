# Snake Adaptive AI - Testing Guide

## Quick Start

### Run All Tests
```bash
python -m pytest src/ -v
```

### Run Tests with Summary
```bash
python -m pytest src/ -q
```

### Run Specific Test File
```bash
python -m pytest src/test_game_engine.py -v
python -m pytest src/test_adaptation_engine.py -v
python -m pytest src/test_difficulty_manager.py -v
python -m pytest src/test_metrics_collector.py -v
python -m pytest src/test_types.py -v
```

### Run Specific Test Class
```bash
python -m pytest src/test_game_engine.py::TestGameEngineInitialization -v
python -m pytest src/test_adaptation_engine.py::TestSkillAssessment -v
```

### Run Specific Test
```bash
python -m pytest src/test_game_engine.py::TestGameEngineInitialization::test_initial_snake_length -v
```

---

## Test Organization

### 1. Type Tests (test_types.py) - 26 Tests
Tests all core data type definitions and instantiation.

**Run:**
```bash
python -m pytest src/test_types.py -v
```

**Test Classes:**
- `TestSegment` - Snake segment validation
- `TestPosition` - Board position validation
- `TestObstacle` - Obstacle type validation
- `TestDirection` - Direction type validation
- `TestDifficultyLevel` - Difficulty parameter validation
- `TestGameState` - Game state validation
- `TestPerformanceMetrics` - Metrics validation
- `TestSkillAssessment` - Skill assessment validation
- `TestDifficultyDelta` - Difficulty delta validation
- `TestAdaptationDecision` - Adaptation decision validation
- `TestGameSession` - Game session validation
- `TestPlayerProfile` - Player profile validation
- `TestCollisionResult` - Collision result validation

---

### 2. Game Engine Tests (test_game_engine.py) - 36 Tests
Tests core game mechanics: movement, collisions, food, scoring.

**Run:**
```bash
python -m pytest src/test_game_engine.py -v
```

**Test Classes:**
- `TestGameEngineInitialization` (8 tests)
  - Default/custom difficulty initialization
  - Initial snake length and position
  - Food and obstacle spawning
  - Initial game state

- `TestSnakeMovement` (7 tests)
  - Movement in all 4 directions
  - Direction validation
  - Snake length consistency

- `TestCollisionDetection` (5 tests)
  - Boundary collisions
  - Self collisions
  - Obstacle collisions

- `TestFoodConsumption` (4 tests)
  - Score increase
  - Snake growth
  - New food spawning

- `TestGameReset` (4 tests)
  - Game state reset
  - Score clearing
  - Snake position restoration

- `TestGameStateRetrieval` (4 tests)
  - State retrieval methods
  - Length/count getters

- `TestGameEngineProperties` (4 property-based tests)
  - **Property 1**: Snake growth consistency
  - **Property 2**: Score calculation accuracy
  - **Property 3**: Collision detection completeness
  - **Property 4**: Food spawn validity

---

### 3. Metrics Collector Tests (test_metrics_collector.py) - 24 Tests
Tests performance metrics collection and validation.

**Run:**
```bash
python -m pytest src/test_metrics_collector.py -v
```

**Test Classes:**
- `TestMetricsCollectorInitialization` (1 test)
- `TestSessionManagement` (2 tests)
- `TestReactionTimeTracking` (4 tests)
- `TestFoodConsumption` (2 tests)
- `TestCollisionAvoidance` (1 test)
- `TestMovementTracking` (3 tests)
- `TestSurvivalTime` (2 tests)
- `TestMetricsRetrieval` (2 tests)
- `TestMetricsValidation` (7 tests)

---

### 4. Adaptation Engine Tests (test_adaptation_engine.py) - 21 Tests
Tests skill assessment and difficulty adaptation logic.

**Run:**
```bash
python -m pytest src/test_adaptation_engine.py -v
```

**Test Classes:**
- `TestSkillAssessment` (5 tests)
  - Excellent/poor player assessment
  - Skill level range validation
  - Confidence scoring

- `TestTrendDetection` (3 tests)
  - Improving trend detection
  - Declining trend detection
  - Stable trend detection

- `TestDifficultyAdjustment` (5 tests)
  - Difficulty increase for good players
  - Difficulty decrease for poor players
  - Adjustment rationale

- `TestAdaptationDecisionLogging` (5 tests)
  - Decision recording
  - Log growth
  - Rationale generation
  - History retrieval

- `TestAdaptationEngineProperties` (3 property-based tests)
  - **Property 6**: Skill assessment consistency
  - **Property 7**: Difficulty adaptation monotonicity
  - **Property 8**: Adaptation decision logging

---

### 5. Difficulty Manager Tests (test_difficulty_manager.py) - 25 Tests
Tests difficulty management and smooth transitions.

**Run:**
```bash
python -m pytest src/test_difficulty_manager.py -v
```

**Test Classes:**
- `TestDifficultyManagerInitialization` (2 tests)
- `TestManualDifficultyControl` (3 tests)
- `TestAdaptiveModeToggle` (3 tests)
- `TestDifficultyAdjustment` (3 tests)
- `TestSmoothTransition` (3 tests)
- `TestParameterValidation` (6 tests)
- `TestDifficultyLevelCalculation` (3 tests)
- `TestDifficultyManagerProperties` (2 property-based tests)
  - **Property 5**: Difficulty bounds enforcement
  - **Property 10**: Difficulty parameter smoothness

---

## Property-Based Testing

### What are Property-Based Tests?
Property-based tests use Hypothesis to generate random inputs and verify that properties hold across all cases.

### Run Only Property-Based Tests
```bash
python -m pytest src/ -k "property" -v
```

### Run with More Examples
```bash
python -m pytest src/ -v --hypothesis-seed=0
```

### Properties Tested

| # | Property | File | Test |
|---|----------|------|------|
| 1 | Snake Growth Consistency | test_game_engine.py | test_property_1_snake_growth_consistency |
| 2 | Score Calculation Accuracy | test_game_engine.py | test_property_2_score_calculation_accuracy |
| 3 | Collision Detection Completeness | test_game_engine.py | test_property_3_collision_detection_completeness |
| 4 | Food Spawn Validity | test_game_engine.py | test_property_4_food_spawn_validity |
| 5 | Difficulty Bounds Enforcement | test_difficulty_manager.py | test_property_5_difficulty_bounds_enforcement |
| 6 | Skill Assessment Consistency | test_adaptation_engine.py | test_property_6_skill_assessment_consistency |
| 7 | Difficulty Adaptation Monotonicity | test_adaptation_engine.py | test_property_7_difficulty_adaptation_monotonicity |
| 8 | Adaptation Decision Logging | test_adaptation_engine.py | test_property_8_adaptation_decision_logging |
| 10 | Difficulty Parameter Smoothness | test_difficulty_manager.py | test_property_10_difficulty_parameter_smoothness |

---

## Test Coverage Analysis

### Run with Coverage Report
```bash
python -m pytest src/ --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### View Coverage Summary
```bash
python -m pytest src/ --cov=src --cov-report=term-missing
```

---

## Testing Specific Features

### Test Game Mechanics Only
```bash
python -m pytest src/test_game_engine.py::TestSnakeMovement -v
python -m pytest src/test_game_engine.py::TestCollisionDetection -v
python -m pytest src/test_game_engine.py::TestFoodConsumption -v
```

### Test Adaptation System Only
```bash
python -m pytest src/test_adaptation_engine.py -v
python -m pytest src/test_difficulty_manager.py -v
```

### Test Metrics Collection Only
```bash
python -m pytest src/test_metrics_collector.py -v
```

### Test Type Safety Only
```bash
python -m pytest src/test_types.py -v
```

---

## Debugging Tests

### Run with Verbose Output
```bash
python -m pytest src/ -vv
```

### Run with Full Traceback
```bash
python -m pytest src/ -vv --tb=long
```

### Run Single Test with Debug
```bash
python -m pytest src/test_game_engine.py::TestSnakeMovement::test_move_right -vv --tb=short
```

### Stop on First Failure
```bash
python -m pytest src/ -x
```

### Show Print Statements
```bash
python -m pytest src/ -s
```

---

## Test Execution Examples

### Example 1: Run All Tests
```bash
$ python -m pytest src/ -q
132 passed in 12.00s
```

### Example 2: Run Game Engine Tests
```bash
$ python -m pytest src/test_game_engine.py -v
...
36 passed in 0.19s
```

### Example 3: Run Property Tests Only
```bash
$ python -m pytest src/ -k "property" -v
...
25 passed in 0.50s
```

### Example 4: Run with Coverage
```bash
$ python -m pytest src/ --cov=src --cov-report=term-missing
...
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
src/adaptation_engine.py        120      0   100%
src/difficulty_manager.py       110      0   100%
src/game_engine.py              140      0   100%
src/game_types.py               45       0   100%
src/metrics_collector.py         65      0   100%
-----------------------------------------------------------
TOTAL                           480      0   100%
```

---

## Continuous Testing

### Watch Mode (Auto-run on File Changes)
```bash
python -m pytest src/ --watch
```

### Run Tests on Save
Use pytest-watch:
```bash
pip install pytest-watch
ptw src/
```

---

## Test Results Summary

**Total Tests:** 132
- Unit Tests: 107
- Property-Based Tests: 25

**Pass Rate:** 100%

**Coverage:** 100% (all core modules)

**Execution Time:** ~12 seconds

---

## Troubleshooting

### Tests Fail with Import Error
```bash
# Ensure you're in the project root directory
cd /path/to/snake-adaptive-ai

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest src/ -v
```

### Hypothesis Tests Timeout
```bash
# Reduce number of examples
python -m pytest src/ --hypothesis-seed=0 -v
```

### Permission Denied
```bash
# On Windows, use python -m
python -m pytest src/ -v

# On Linux/Mac
chmod +x src/test_*.py
pytest src/ -v
```

---

## Best Practices

1. **Run all tests before committing**
   ```bash
   python -m pytest src/ -q
   ```

2. **Check coverage regularly**
   ```bash
   python -m pytest src/ --cov=src
   ```

3. **Run property tests with multiple seeds**
   ```bash
   python -m pytest src/ -k "property" --hypothesis-seed=0
   python -m pytest src/ -k "property" --hypothesis-seed=1
   ```

4. **Use verbose mode for debugging**
   ```bash
   python -m pytest src/test_file.py::TestClass::test_method -vv
   ```

5. **Keep tests isolated and independent**
   - Each test should be runnable independently
   - No test should depend on another test's state

---

## Next Steps

After testing, you can:

1. **Extend the implementation** with UI components (Tasks 7-10)
2. **Add integration tests** for end-to-end gameplay
3. **Performance testing** for game loop optimization
4. **Load testing** for metrics collection under stress

For more information, see `IMPLEMENTATION_SUMMARY.md`
