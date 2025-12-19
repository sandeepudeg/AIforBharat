# How to Play - Snake Adaptive AI

## 🎮 Play the Game

The implementation includes a **text-based demo** that shows the game in action. This is NOT a full UI, but demonstrates how the game engine works.

### Run the Demo

```bash
python src/game_demo.py
```

### Demo Options

When you run the demo, you'll see:

```
1. Run Demo (auto-play)
2. Play Interactive Game

Select option (1 or 2):
```

---

## 🤖 Option 1: Auto-Play Demo

**Command:** Select `1`

This runs an automated demo where the game plays itself for 20 moves.

**What you'll see:**
- Game board with snake (●), body (○), food (✱), obstacles (█)
- Score and game statistics
- Snake length and food count
- Difficulty level (1-10)
- AI skill assessment every 5 moves
- Adaptive difficulty adjustments

**Example Output:**
```
==================================================
  SNAKE ADAPTIVE AI - TEXT DEMO
==================================================
┌────────────────────────────┐
│.....●...................│
│.....○...................│
│.....○...................│
│.....✱...................│
│.....█...................│
│.......................│
│.......................│
│.......................│
│.......................│
│.......................│
└────────────────────────────┘

📊 GAME STATS
  Score: 10
  Snake Length: 3
  Food: 1
  Obstacles: 1
  Game Over: False

⚙️  DIFFICULTY
  Level: 1/10
  Speed: 5/10
  Obstacles: 1/5
  Food Rate: 1.0x
  Adaptive Mode: ON

📈 METRICS
  Survival Time: 5.2s
  Food Consumed: 1
  Avg Speed: 0.19 moves/s
  Reaction Times: 5

🤖 AI ASSESSMENT
  Skill Level: 45/100
  Trend: stable
  Confidence: 65.0%
  Adjustment: Average performance - maintaining difficulty
```

---

## 👤 Option 2: Interactive Game

**Command:** Select `2`

Play the game yourself using keyboard controls.

**Controls:**
- `up` - Move snake up
- `down` - Move snake down
- `left` - Move snake left
- `right` - Move snake right
- `q` - Quit game

**How to Play:**
1. Run `python src/game_demo.py`
2. Select option `2`
3. Type a direction and press Enter
4. Watch the snake move
5. Eat food (✱) to grow and score points
6. Avoid obstacles (█) and walls
7. Type `q` to quit

**Example Gameplay:**
```
==================================================
  SNAKE ADAPTIVE AI - INTERACTIVE GAME
==================================================
┌────────────────────────────┐
│.....●...................│
│.....○...................│
│.....○...................│
│.....✱...................│
│.....█...................│
│.......................│
│.......................│
│.......................│
│.......................│
│.......................│
└────────────────────────────┘

📊 GAME STATS
  Score: 0
  Snake Length: 3
  Food: 1
  Obstacles: 1
  Game Over: False

⚙️  DIFFICULTY
  Level: 1/10
  Speed: 5/10
  Obstacles: 1/5
  Food Rate: 1.0x
  Adaptive Mode: ON

📈 METRICS
  Survival Time: 0.1s
  Food Consumed: 0
  Avg Speed: 0.00 moves/s
  Reaction Times: 0

➡️  Enter direction (up/down/left/right) or 'q' to quit: right
```

---

## 🎯 Game Mechanics

### Scoring
- **10 points** per food consumed
- Snake grows by 1 segment per food

### Collisions
- **Self collision**: Snake hits its own body → Game Over
- **Obstacle collision**: Snake hits obstacle → Game Over
- **Boundary collision**: Snake goes off board → Game Over

### Difficulty Levels (1-10)
- **Level 1**: Easy (slow speed, few obstacles)
- **Level 5**: Medium (moderate speed, some obstacles)
- **Level 10**: Hard (fast speed, many obstacles)

### Adaptive AI
The game watches your performance and adjusts difficulty:
- **Playing well?** → Difficulty increases
- **Struggling?** → Difficulty decreases
- **Consistent?** → Difficulty stays the same

---

## 📊 What the Demo Shows

### Game Board
```
┌────────────────────────────┐
│●  = Snake head
│○  = Snake body
│✱  = Food
│█  = Obstacle
│.  = Empty space
└────────────────────────────┘
```

### Statistics Displayed
- **Score**: Points earned
- **Snake Length**: Current size
- **Food**: Items on board
- **Obstacles**: Barriers on board
- **Difficulty Level**: 1-10 scale
- **Speed**: 1-10 (higher = faster)
- **Survival Time**: How long you've played
- **Skill Level**: AI's assessment of your ability (0-100)
- **Trend**: improving/stable/declining

### AI Assessment
Every 5 moves, the AI evaluates your performance:
- Calculates your skill level (0-100)
- Detects your trend (improving/stable/declining)
- Adjusts difficulty if needed
- Shows the reason for adjustment

---

## 🚀 Running the Demo

### Step 1: Open Terminal
```bash
cd /path/to/snake-adaptive-ai
```

### Step 2: Run the Demo
```bash
python src/game_demo.py
```

### Step 3: Select Option
```
1. Run Demo (auto-play)
2. Play Interactive Game

Select option (1 or 2): 1
```

### Step 4: Watch the Game
The auto-play demo runs for 20 moves, showing:
- Game board updates
- Score changes
- AI assessments
- Difficulty adjustments

---

## 📝 Example Session

### Auto-Play Demo (20 moves)
```
Move 1: Snake moves right
Move 2: Snake moves right
Move 3: Snake moves down
Move 4: Snake moves down
Move 5: AI Assessment - Skill: 45/100, Trend: stable
Move 6: Snake moves left
...
Move 20: Game Over - Final Score: 30
```

### Interactive Game
```
Move 1: You type "right" → Snake moves right
Move 2: You type "down" → Snake moves down
Move 3: You type "left" → Snake moves left
Move 4: You type "up" → Snake moves up
Move 5: AI Assessment - Skill: 55/100, Trend: improving
...
Game Over: You quit or hit obstacle
```

---

## ⚠️ Important Notes

### This is a Text-Based Demo
- **NOT a full graphical UI**
- Shows game logic and AI in action
- Demonstrates how components work together
- Good for testing and understanding the system

### For a Full UI, You Would Need:
- Graphics library (Pygame, Tkinter, etc.)
- Real-time rendering
- Smooth animations
- Mouse/keyboard input handling
- Game loop optimization

### Current Implementation Includes:
- ✅ Game engine (movement, collisions, scoring)
- ✅ Metrics collection
- ✅ Skill assessment
- ✅ Difficulty adaptation
- ✅ Text-based demo
- ❌ Graphical UI (not implemented)

---

## 🎓 What You Can Learn

By running the demo, you can see:

1. **How the game engine works**
   - Snake movement
   - Collision detection
   - Food consumption

2. **How metrics are collected**
   - Reaction time
   - Survival time
   - Food consumption rate

3. **How the AI adapts**
   - Skill assessment
   - Trend detection
   - Difficulty adjustment

4. **How the system integrates**
   - All components working together
   - Real-time adaptation
   - Decision logging

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
python src/game_demo.py
```

### Issue: Demo runs too fast
**Solution:**
The demo has 1-second delays between moves. You can modify `src/game_demo.py` and change:
```python
time.sleep(1)  # Change to time.sleep(2) for slower speed
```

### Issue: Board doesn't display correctly
**Solution:**
Make sure your terminal supports Unicode characters (●, ○, ✱, █)

---

## 📚 Next Steps

To build a full graphical UI, you would need to:

1. **Choose a graphics library**
   - Pygame (recommended for games)
   - Tkinter (built-in Python)
   - Arcade (modern Python game library)

2. **Implement rendering**
   - Draw game board
   - Render snake, food, obstacles
   - Display UI elements

3. **Handle input**
   - Keyboard controls
   - Real-time input processing

4. **Create game loop**
   - Update game state
   - Render graphics
   - Handle timing

5. **Add UI elements**
   - Score display
   - Difficulty indicator
   - Settings menu
   - Statistics screen

---

## 🎮 Summary

**To play the game:**
```bash
python src/game_demo.py
```

**Choose:**
- `1` for auto-play demo (watch the AI play)
- `2` for interactive game (you play)

**Enjoy!** 🎉
