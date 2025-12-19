# 🎮 Snake Adaptive AI - Tkinter GUI Guide

## Quick Start

### Windows (Batch)
```bash
run_gui.bat
```

### Windows (PowerShell)
```powershell
.\run_gui.ps1
```

### All Platforms
```bash
python src/game_gui.py
```

---

## GUI Features

### Game Display
- **Visual Game Board** - 20x20 grid with colored cells
- **Snake** - Green circle (head) and rectangles (body)
- **Food** - Red circles to eat
- **Obstacles** - Gray squares to avoid
- **Grid Lines** - Dark gray grid for reference

### Statistics Panel
Real-time display of:
- **Score** - Current points (green)
- **Snake Length** - Current size (blue)
- **Difficulty** - Current level 1-10 (red)
- **Survival Time** - How long you've been playing (orange)
- **Food Consumed** - Total food eaten (purple)
- **Adaptive Mode** - ON/OFF status (cyan)

### Control Buttons
- **Start Game** - Begin a new game
- **Pause** - Pause the current game
- **Resume** - Resume a paused game
- **Reset** - Reset to initial state

---

## How to Play

### 1. Start the GUI
```bash
run_gui.bat  # Windows
python src/game_gui.py  # All platforms
```

### 2. Click "Start Game"
The game board will appear with your snake in the center.

### 3. Use Controls to Move
| Key | Action |
|-----|--------|
| `W` or `↑` | Move UP |
| `S` or `↓` | Move DOWN |
| `A` or `←` | Move LEFT |
| `D` or `→` | Move RIGHT |
| `Q` | QUIT |

### 4. Eat Food
- Move your snake to the red circles
- Each food eaten: +10 points, +1 segment

### 5. Avoid Obstacles
- Gray squares are obstacles
- Hitting them ends the game
- Also avoid walls (board edges)

### 6. Watch Difficulty Adapt
- The game learns from your performance
- Difficulty increases if you're doing well
- Difficulty decreases if you're struggling

---

## Game Mechanics

### Scoring
- **+10 points** per food eaten
- **+1 segment** to snake length per food

### Game Over Conditions
The game ends if your snake:
- Hits a **wall** (board edge)
- Hits an **obstacle** (gray square)
- Hits **itself** (its own body)

### Adaptive Difficulty
The AI adjusts:
- **Speed** - How fast the snake moves
- **Obstacles** - Number of obstacles on board
- **Food Spawn Rate** - How often food appears

---

## GUI Controls

### Buttons
- **Start Game** - Begin a new game (green)
- **Pause** - Pause the game (orange)
- **Resume** - Resume paused game (blue)
- **Reset** - Reset to initial state (red)

### Keyboard
- **WASD** - Move snake
- **Arrow Keys** - Move snake
- **Q** - Quit game

### Mouse
- Click buttons to control game

---

## Statistics Display

### Real-Time Updates
The statistics panel updates every game tick:

```
Score: 150              (Green - Points earned)
Snake Length: 15        (Blue - Current size)
Difficulty: 5/10        (Red - Current level)
Survival Time: 45.2s    (Orange - Time played)
Food Consumed: 15       (Purple - Total eaten)
Adaptive Mode: ON       (Cyan - AI status)
```

---

## Game States

### IDLE
- Game not started
- All buttons available
- Board shows initial state

### RUNNING
- Game is active
- Snake moves automatically
- Pause button available

### PAUSED
- Game is paused
- Snake doesn't move
- Resume button available

### GAME OVER
- Game has ended
- Message box shows final stats
- Can start new game

---

## Tips for Playing

### Beginner Tips
1. Start at Level 1 (easiest)
2. Move slowly and plan ahead
3. Avoid corners - they're dangerous
4. Watch for obstacles

### Intermediate Tips
1. Plan 2-3 moves ahead
2. Use walls strategically
3. Eat food efficiently
4. Watch the difficulty level

### Advanced Tips
1. Create loops with your body
2. Manage space carefully
3. Predict food spawns
4. Master timing

---

## Difficulty Levels

### Level 1-3: Easy
- Slow snake speed
- Few obstacles
- Lots of food
- **Best for:** Learning

### Level 4-6: Medium
- Normal speed
- Moderate obstacles
- Regular food
- **Best for:** Casual play

### Level 7-10: Hard
- Fast snake speed
- Many obstacles
- Challenging gameplay
- **Best for:** Experienced players

---

## Color Scheme

| Element | Color | Meaning |
|---------|-------|---------|
| Snake Head | Green | Your snake's head |
| Snake Body | Dark Green | Your snake's body |
| Food | Red | Eat this! |
| Obstacles | Gray | Avoid this! |
| Grid | Dark Gray | Board reference |
| Background | Black | Empty space |
| Score | Green | Points |
| Length | Blue | Size |
| Difficulty | Red | Level |
| Time | Orange | Duration |
| Food | Purple | Consumed |
| Adaptive | Cyan | AI status |

---

## Troubleshooting

### GUI doesn't open
1. Make sure Tkinter is installed
2. Try: `python -m tkinter` to test
3. On Linux: `sudo apt-get install python3-tk`

### Game doesn't respond
1. Click on the window to focus it
2. Try pressing keys slowly
3. Check that Caps Lock is off

### GUI is too small/large
1. Resize the window
2. The game board will scale automatically

### Performance issues
1. Close other applications
2. Reduce other background processes
3. Try the text version: `python src/game_demo.py`

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `W` | Move UP |
| `S` | Move DOWN |
| `A` | Move LEFT |
| `D` | Move RIGHT |
| `↑` | Move UP |
| `↓` | Move DOWN |
| `←` | Move LEFT |
| `→` | Move RIGHT |
| `Q` | QUIT |

---

## Game Flow

```
1. Start GUI
   ↓
2. Click "Start Game"
   ↓
3. Use WASD/Arrow Keys to move
   ↓
4. Eat food (red circles)
   ↓
5. Avoid obstacles (gray squares)
   ↓
6. Watch difficulty adapt
   ↓
7. Game Over (hit wall/obstacle/self)
   ↓
8. See final stats
   ↓
9. Click "Start Game" to play again
```

---

## Advanced Features

### Pause and Resume
- Click "Pause" to pause the game
- Click "Resume" to continue
- Useful for taking breaks

### Reset
- Click "Reset" to start fresh
- Clears all game data
- Returns to initial state

### Statistics
- Watch real-time stats update
- Track your performance
- See difficulty changes

---

## Have Fun! 🎮

The Tkinter GUI provides a complete graphical experience for playing Snake Adaptive AI!

**Start playing:**
```bash
run_gui.bat          # Windows
python src/game_gui.py  # All platforms
```

Enjoy! 🐍✨
