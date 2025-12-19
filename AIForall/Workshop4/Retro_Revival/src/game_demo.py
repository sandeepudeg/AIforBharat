"""
Simple text-based demo of Snake Adaptive AI
Shows how the game engine works with a basic UI
"""

import time
import os
from game_engine import GameEngine
from adaptation_engine import AdaptationEngine
from difficulty_manager import DifficultyManager
from metrics_collector import MetricsCollector
from game_types import DifficultyLevel


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_board(engine):
    """Draw the game board in text format"""
    board = [['.' for _ in range(engine.BOARD_WIDTH)] for _ in range(engine.BOARD_HEIGHT)]
    
    # Draw snake
    for i, segment in enumerate(engine.game_state.snake):
        if 0 <= segment.x < engine.BOARD_WIDTH and 0 <= segment.y < engine.BOARD_HEIGHT:
            if i == 0:
                board[segment.y][segment.x] = '●'  # Head
            else:
                board[segment.y][segment.x] = '○'  # Body
    
    # Draw food
    for food in engine.game_state.food:
        if 0 <= food.x < engine.BOARD_WIDTH and 0 <= food.y < engine.BOARD_HEIGHT:
            board[food.y][food.x] = '✱'
    
    # Draw obstacles
    for obstacle in engine.game_state.obstacles:
        if 0 <= obstacle.x < engine.BOARD_WIDTH and 0 <= obstacle.y < engine.BOARD_HEIGHT:
            board[obstacle.y][obstacle.x] = '█'
    
    # Print board
    print("┌" + "─" * engine.BOARD_WIDTH + "┐")
    for row in board:
        print("│" + "".join(row) + "│")
    print("└" + "─" * engine.BOARD_WIDTH + "┘")


def print_stats(engine, metrics, adaptation, difficulty):
    """Print game statistics"""
    print(f"\n📊 GAME STATS")
    print(f"  Score: {engine.game_state.score}")
    print(f"  Snake Length: {len(engine.game_state.snake)}")
    print(f"  Food: {len(engine.game_state.food)}")
    print(f"  Obstacles: {len(engine.game_state.obstacles)}")
    print(f"  Game Over: {engine.game_state.game_over}")
    
    print(f"\n⚙️  DIFFICULTY")
    diff = difficulty.get_current_difficulty()
    print(f"  Level: {diff.level}/10")
    print(f"  Speed: {diff.speed}/10")
    print(f"  Obstacles: {diff.obstacle_density}/5")
    print(f"  Food Rate: {diff.food_spawn_rate:.1f}x")
    print(f"  Adaptive Mode: {'ON' if diff.adaptive_mode else 'OFF'}")
    
    print(f"\nMETRICS")
    print(f"  Survival Time: {metrics.get_survival_time():.1f}s")
    print(f"  Food Consumed: {metrics.food_consumed}")
    print(f"  Avg Speed: {metrics.get_average_speed():.2f} moves/s")
    print(f"  Reaction Times: {len(metrics.reaction_times)}")


def demo_game():
    """Run a simple demo game"""
    print("=" * 50)
    print("  SNAKE ADAPTIVE AI - TEXT DEMO")
    print("=" * 50)
    
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
    
    print("\n🎮 GAME STARTED!")
    print("Controls: up, down, left, right, or 'q' to quit")
    print("Press Enter to auto-play demo...\n")
    
    # Demo: Auto-play for a few moves
    moves = 0
    max_moves = 20
    directions = ['right', 'right', 'down', 'down', 'left', 'left', 'up', 'up', 'right']
    direction_index = 0
    
    while not engine.game_state.game_over and moves < max_moves:
        clear_screen()
        
        print("=" * 50)
        print("  SNAKE ADAPTIVE AI - TEXT DEMO")
        print("=" * 50)
        
        # Draw board
        draw_board(engine)
        
        # Print stats
        print_stats(engine, metrics, adaptation, difficulty)
        
        # Auto-play
        direction = directions[direction_index % len(directions)]
        direction_index += 1
        
        print(f"\n➡️  Moving: {direction.upper()}")
        
        # Update game
        engine.update(direction)
        metrics.record_movement()
        metrics.record_input()
        
        # Check for food consumption
        if len(engine.game_state.food) < 1:
            metrics.record_food_consumption()
        
        moves += 1
        
        # Assess skill every 5 moves
        if moves % 5 == 0:
            perf_metrics = metrics.get_metrics()
            skill = adaptation.assess_player_skill(perf_metrics)
            delta = adaptation.calculate_difficulty_adjustment(skill)
            
            print(f"\n🤖 AI ASSESSMENT")
            print(f"  Skill Level: {skill.skill_level}/100")
            print(f"  Trend: {skill.trend}")
            print(f"  Confidence: {skill.confidence:.1%}")
            print(f"  Adjustment: {delta.reason}")
            
            if delta.speed_delta != 0 or delta.obstacle_density_delta != 0:
                difficulty.apply_difficulty_adjustment(delta)
                adaptation.record_adaptation_decision(perf_metrics, skill, delta, delta.reason)
        
        time.sleep(1)
    
    # Game over
    clear_screen()
    print("=" * 50)
    print("  GAME OVER!")
    print("=" * 50)
    draw_board(engine)
    print_stats(engine, metrics, adaptation, difficulty)
    
    print(f"\n🏆 FINAL RESULTS")
    print(f"  Final Score: {engine.game_state.score}")
    print(f"  Moves: {moves}")
    print(f"  Total Time: {metrics.get_survival_time():.1f}s")
    print(f"  Food Eaten: {metrics.food_consumed}")
    
    print("\n✅ Demo complete!")


def interactive_game():
    """Run an interactive game (requires manual input)"""
    print("=" * 50)
    print("  SNAKE ADAPTIVE AI - INTERACTIVE GAME")
    print("=" * 50)
    
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
    
    print("\n🎮 GAME STARTED!")
    print("Controls: up, down, left, right, or 'q' to quit\n")
    
    moves = 0
    
    while not engine.game_state.game_over:
        clear_screen()
        
        print("=" * 50)
        print("  SNAKE ADAPTIVE AI - INTERACTIVE GAME")
        print("=" * 50)
        
        # Draw board
        draw_board(engine)
        
        # Print stats
        print_stats(engine, metrics, adaptation, difficulty)
        
        # Get input
        direction = input("\n➡️  Enter direction (up/down/left/right) or 'q' to quit: ").lower().strip()
        
        if direction == 'q':
            print("Game quit!")
            break
        
        if direction not in ['up', 'down', 'left', 'right']:
            print("Invalid direction!")
            continue
        
        # Update game
        engine.update(direction)
        metrics.record_movement()
        metrics.record_input()
        
        # Check for food consumption
        if len(engine.game_state.food) < 1:
            metrics.record_food_consumption()
        
        moves += 1
        
        # Assess skill every 5 moves
        if moves % 5 == 0:
            perf_metrics = metrics.get_metrics()
            skill = adaptation.assess_player_skill(perf_metrics)
            delta = adaptation.calculate_difficulty_adjustment(skill)
            
            print(f"\n🤖 AI ASSESSMENT")
            print(f"  Skill Level: {skill.skill_level}/100")
            print(f"  Trend: {skill.trend}")
            print(f"  Confidence: {skill.confidence:.1%}")
            print(f"  Adjustment: {delta.reason}")
            
            if delta.speed_delta != 0 or delta.obstacle_density_delta != 0:
                difficulty.apply_difficulty_adjustment(delta)
                adaptation.record_adaptation_decision(perf_metrics, skill, delta, delta.reason)
    
    # Game over
    clear_screen()
    print("=" * 50)
    print("  GAME OVER!")
    print("=" * 50)
    draw_board(engine)
    print_stats(engine, metrics, adaptation, difficulty)
    
    print(f"\n🏆 FINAL RESULTS")
    print(f"  Final Score: {engine.game_state.score}")
    print(f"  Moves: {moves}")
    print(f"  Total Time: {metrics.get_survival_time():.1f}s")
    print(f"  Food Eaten: {metrics.food_consumed}")


if __name__ == "__main__":
    print("\n1. Run Demo (auto-play)")
    print("2. Play Interactive Game")
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        demo_game()
    elif choice == "2":
        interactive_game()
    else:
        print("Invalid choice!")
