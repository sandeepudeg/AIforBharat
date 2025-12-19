"""
Tkinter GUI for Snake Adaptive AI
Provides a graphical interface for playing the game
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_loop import GameLoop
from game_types import DifficultyLevel, Direction
from game_engine import GameEngine


class SnakeGameGUI:
    """Tkinter GUI for Snake Adaptive AI game"""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI"""
        self.root = root
        self.root.title("Snake Adaptive AI")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Game variables
        self.game_loop: Optional[GameLoop] = None
        self.running = False
        self.cell_size = 20
        self.board_width = 20
        self.board_height = 20
        
        # Create UI
        self.create_widgets()
        self.setup_game()
        
        # Bind keyboard events
        self.root.bind('<w>', lambda e: self.handle_input('up'))
        self.root.bind('<W>', lambda e: self.handle_input('up'))
        self.root.bind('<s>', lambda e: self.handle_input('down'))
        self.root.bind('<S>', lambda e: self.handle_input('down'))
        self.root.bind('<a>', lambda e: self.handle_input('left'))
        self.root.bind('<A>', lambda e: self.handle_input('left'))
        self.root.bind('<d>', lambda e: self.handle_input('right'))
        self.root.bind('<D>', lambda e: self.handle_input('right'))
        self.root.bind('<Up>', lambda e: self.handle_input('up'))
        self.root.bind('<Down>', lambda e: self.handle_input('down'))
        self.root.bind('<Left>', lambda e: self.handle_input('left'))
        self.root.bind('<Right>', lambda e: self.handle_input('right'))
        self.root.bind('<q>', lambda e: self.quit_game())
        self.root.bind('<Q>', lambda e: self.quit_game())

    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🐍 Snake Adaptive AI 🐍",
            font=("Arial", 20, "bold"),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack(pady=10)
        
        # Game canvas
        canvas_frame = tk.Frame(main_frame, bg='#34495e')
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.board_width * self.cell_size,
            height=self.board_height * self.cell_size,
            bg='#1a1a1a',
            highlightthickness=2,
            highlightbackground='#ecf0f1'
        )
        self.canvas.pack()
        
        # Stats frame
        stats_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Left stats
        left_stats = tk.Frame(stats_frame, bg='#34495e')
        left_stats.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        tk.Label(left_stats, text="Score:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W)
        self.score_label = tk.Label(left_stats, text="0", font=("Arial", 14, "bold"), bg='#34495e', fg='#2ecc71')
        self.score_label.pack(anchor=tk.W)
        
        tk.Label(left_stats, text="Snake Length:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W, pady=(10, 0))
        self.length_label = tk.Label(left_stats, text="3", font=("Arial", 14, "bold"), bg='#34495e', fg='#3498db')
        self.length_label.pack(anchor=tk.W)
        
        # Middle stats
        middle_stats = tk.Frame(stats_frame, bg='#34495e')
        middle_stats.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        tk.Label(middle_stats, text="Difficulty:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W)
        self.difficulty_label = tk.Label(middle_stats, text="1/10", font=("Arial", 14, "bold"), bg='#34495e', fg='#e74c3c')
        self.difficulty_label.pack(anchor=tk.W)
        
        tk.Label(middle_stats, text="Survival Time:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W, pady=(10, 0))
        self.time_label = tk.Label(middle_stats, text="0.0s", font=("Arial", 14, "bold"), bg='#34495e', fg='#f39c12')
        self.time_label.pack(anchor=tk.W)
        
        # Right stats
        right_stats = tk.Frame(stats_frame, bg='#34495e')
        right_stats.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        tk.Label(right_stats, text="Food Consumed:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W)
        self.food_label = tk.Label(right_stats, text="0", font=("Arial", 14, "bold"), bg='#34495e', fg='#9b59b6')
        self.food_label.pack(anchor=tk.W)
        
        tk.Label(right_stats, text="Adaptive Mode:", font=("Arial", 10, "bold"), bg='#34495e', fg='#ecf0f1').pack(anchor=tk.W, pady=(10, 0))
        self.adaptive_label = tk.Label(right_stats, text="ON", font=("Arial", 14, "bold"), bg='#34495e', fg='#1abc9c')
        self.adaptive_label.pack(anchor=tk.W)
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg='#2c3e50')
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(
            control_frame,
            text="Start Game",
            command=self.start_game,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = tk.Button(
            control_frame,
            text="Pause",
            command=self.pause_game,
            font=("Arial", 12, "bold"),
            bg='#f39c12',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.resume_button = tk.Button(
            control_frame,
            text="Resume",
            command=self.resume_game,
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.resume_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            control_frame,
            text="Reset",
            command=self.reset_game,
            font=("Arial", 12, "bold"),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = tk.Button(
            control_frame,
            text="Close",
            command=self.quit_game,
            font=("Arial", 12, "bold"),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=10
        )
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(
            main_frame,
            text="Use WASD or Arrow Keys to move. Press Q to quit.",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        self.info_label.pack(pady=5)

    def setup_game(self):
        """Setup the game"""
        initial_difficulty = DifficultyLevel(
            level=1,
            speed=5,
            obstacle_density=1,
            food_spawn_rate=1.0,
            adaptive_mode=True
        )
        
        self.game_loop = GameLoop(difficulty_manager=None)
        self.game_loop.difficulty_manager.set_manual_difficulty(initial_difficulty)

    def start_game(self):
        """Start a new game"""
        if self.running:
            return
        
        self.game_loop.start_game()
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)
        self.info_label.config(text="Game started! Use WASD or Arrow Keys to move.")
        
        self.update_game()

    def pause_game(self):
        """Pause the game"""
        if not self.running:
            return
        
        self.game_loop.pause_game()
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
        self.info_label.config(text="Game paused. Click Resume to continue.")

    def resume_game(self):
        """Resume the game"""
        if self.running:
            self.game_loop.resume_game()
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.info_label.config(text="Game resumed!")
            self.update_game()

    def reset_game(self):
        """Reset the game"""
        self.running = False
        self.setup_game()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.info_label.config(text="Game reset. Click Start Game to begin.")
        self.draw_board()
        self.update_stats()

    def handle_input(self, direction: str):
        """Handle keyboard input"""
        if self.running and self.game_loop:
            self.game_loop.queue_input(direction)

    def update_game(self):
        """Update game state"""
        if not self.running or not self.game_loop:
            return
        
        # Update game
        if not self.game_loop.update():
            self.end_game()
            return
        
        # Draw board
        self.draw_board()
        
        # Update stats
        self.update_stats()
        
        # Schedule next update
        self.root.after(50, self.update_game)

    def draw_board(self):
        """Draw the game board"""
        if not self.game_loop:
            return
        
        self.canvas.delete("all")
        
        state = self.game_loop.get_game_state()
        
        # Draw grid
        for x in range(self.board_width + 1):
            self.canvas.create_line(
                x * self.cell_size, 0,
                x * self.cell_size, self.board_height * self.cell_size,
                fill='#444444', width=0.5
            )
        
        for y in range(self.board_height + 1):
            self.canvas.create_line(
                0, y * self.cell_size,
                self.board_width * self.cell_size, y * self.cell_size,
                fill='#444444', width=0.5
            )
        
        # Draw snake
        for i, segment in enumerate(state.snake):
            x = segment.x * self.cell_size
            y = segment.y * self.cell_size
            
            if i == 0:  # Head
                self.canvas.create_oval(
                    x + 2, y + 2,
                    x + self.cell_size - 2, y + self.cell_size - 2,
                    fill='#2ecc71', outline='#27ae60', width=2
                )
            else:  # Body
                self.canvas.create_rectangle(
                    x + 2, y + 2,
                    x + self.cell_size - 2, y + self.cell_size - 2,
                    fill='#27ae60', outline='#229954', width=1
                )
        
        # Draw food
        for food in state.food:
            x = food.x * self.cell_size
            y = food.y * self.cell_size
            self.canvas.create_oval(
                x + 5, y + 5,
                x + self.cell_size - 5, y + self.cell_size - 5,
                fill='#e74c3c', outline='#c0392b', width=2
            )
        
        # Draw obstacles
        for obstacle in state.obstacles:
            x = obstacle.x * self.cell_size
            y = obstacle.y * self.cell_size
            self.canvas.create_rectangle(
                x + 2, y + 2,
                x + self.cell_size - 2, y + self.cell_size - 2,
                fill='#95a5a6', outline='#7f8c8d', width=1
            )

    def update_stats(self):
        """Update statistics display"""
        if not self.game_loop:
            return
        
        state = self.game_loop.get_game_state()
        metrics = self.game_loop.get_metrics()
        difficulty = self.game_loop.get_current_difficulty()
        
        self.score_label.config(text=str(state.score))
        self.length_label.config(text=str(len(state.snake)))
        self.difficulty_label.config(text=f"{difficulty.level}/10")
        
        if metrics:
            self.time_label.config(text=f"{metrics.survival_time:.1f}s")
            self.food_label.config(text=str(metrics.food_consumed))
        
        adaptive_text = "ON" if difficulty.adaptive_mode else "OFF"
        self.adaptive_label.config(text=adaptive_text)

    def end_game(self):
        """Handle game over"""
        self.running = False
        state = self.game_loop.get_game_state()
        metrics = self.game_loop.get_metrics()
        
        message = f"Game Over!\n\n"
        message += f"Final Score: {state.score}\n"
        message += f"Snake Length: {len(state.snake)}\n"
        
        if metrics:
            message += f"Survival Time: {metrics.survival_time:.1f}s\n"
            message += f"Food Consumed: {metrics.food_consumed}\n"
        
        message += f"Difficulty: {state.difficulty.level}/10"
        
        messagebox.showinfo("Game Over", message)
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)
        self.info_label.config(text="Game over! Click Start Game to play again.")

    def quit_game(self):
        """Quit the game"""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()


def main():
    """Main function"""
    root = tk.Tk()
    gui = SnakeGameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
