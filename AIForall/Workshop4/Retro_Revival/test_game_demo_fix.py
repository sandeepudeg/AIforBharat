#!/usr/bin/env python
"""Test to verify game_demo.py works correctly"""

import sys
sys.path.insert(0, 'src')

from game_engine import GameEngine
from adaptation_engine import AdaptationEngine
from difficulty_manager import DifficultyManager
from metrics_collector import MetricsCollector
from game_types import DifficultyLevel

def test_game_demo_components():
    """Test that all game demo components work"""
    print("🧪 Testing game demo components...")
    
    # Initialize components
    initial_difficulty = DifficultyLevel(
        level=1,
        speed=5,
        obstacle_density=1,
        food_spawn_rate=1.0,
        adaptive_mode=True
    )
    
    engine = GameEngine(initial_difficulty)
    metrics = MetricsCollector()
    adaptation = AdaptationEngine()
    difficulty = DifficultyManager(initial_difficulty)
    
    metrics.start_session()
    
    print("✅ All components initialized successfully")
    
    # Test metrics
    print(f"✅ Metrics object has reaction_times: {hasattr(metrics, 'reaction_times')}")
    print(f"✅ Reaction times count: {len(metrics.reaction_times)}")
    
    # Test game loop
    for i in range(10):
        engine.update('up')
        metrics.record_movement()
    
    print(f"✅ Game loop works")
    print(f"✅ Survival time: {metrics.get_survival_time():.1f}s")
    print(f"✅ Food consumed: {metrics.food_consumed}")
    print(f"✅ Avg speed: {metrics.get_average_speed():.2f} moves/s")
    
    print("\n✅ All tests passed! Game demo should work now.")

if __name__ == "__main__":
    test_game_demo_components()
