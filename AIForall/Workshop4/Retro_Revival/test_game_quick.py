#!/usr/bin/env python
"""Quick test to verify the game runs without errors"""

import sys
sys.path.insert(0, 'src')

from game_loop import GameLoop
from game_types import DifficultyLevel

def test_game_quick():
    """Quick test of game functionality"""
    print("🎮 Starting quick game test...")
    
    # Create game loop
    loop = GameLoop()
    loop.start_game()
    
    print("✅ Game started successfully")
    
    # Play for a few ticks
    for i in range(20):
        loop.queue_input('up')
        if not loop.update():
            print("❌ Game ended unexpectedly")
            break
    
    # Get metrics
    metrics = loop.get_metrics()
    if metrics:
        print(f"✅ Metrics collected:")
        print(f"   - Survival Time: {metrics.survival_time:.1f}s")
        print(f"   - Food Consumed: {metrics.food_consumed}")
        print(f"   - Reaction Times: {len(metrics.reaction_time)}")
        print(f"   - Avg Speed: {metrics.average_speed:.2f} moves/s")
    
    # Get game state
    state = loop.get_game_state()
    print(f"✅ Game state:")
    print(f"   - Score: {state.score}")
    print(f"   - Snake Length: {len(state.snake)}")
    print(f"   - Game Over: {state.game_over}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_game_quick()
