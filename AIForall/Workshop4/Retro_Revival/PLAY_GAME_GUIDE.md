# How to Play Snake Adaptive AI

## Quick Start

### Step 1: Run the Game
```bash
python src/game_demo.py
```

### Step 2: Wait for the Game to Start
The game will display:
- A game board with your snake, food, and obstacles
- Game statistics (score, snake length, etc.)
- Difficulty settings
- Performance metrics

### Step 3: Play!
Use keyboard controls to move your snake and eat food.

---

## Game Display

When you run the game, you'll see something like this:

```
==================================================SNAKE ADAPTIVE AI - INTERACTIVE GAME==================================================
┌────────────────────┐
│....................│
│....................│
│....................│
│........○○●......█..│  
│....................│
└────────────────────┘

GAME STATS
  Score: 0
  Snake Length: 3
  Food: 1
  Obstacles: 1
  Game Over: False

DIFFICULTY
  Level: 1/10
  Speed: 5/10
  Obstacles: 1/5
  Food Rate: 1.0x
  Adaptive Mode: ON

METRICS
  Survival Time: 0.0s
  Food Consumed: 0
  Avg Speed: 0.00 moves/s
  Reaction Times: 0
```

### Legend
- `●` = Snake head
- `○` = Snake body
- `*` = Food (eat this!)
- `█` = Obstacles (avoid!)
- `.` = Empty space

---

## Controls

### Movement
| Key | Action |
|-----|--------|
| `w` | Move UP |
| `s` | Move DOWN |
| `a` | Move LEFT |
| `d` | Move RIGHT |
| Arrow Keys | Also work for movement |

### Game Control
| Key | Action |
|-----|--------|
| `q` | QUIT game |
| `Ctrl+C` | Force quit |

---

## Game Rules

### Objective
1. **Eat food** (✱) to grow and gain points
2. **Avoid obstacles** (█) and walls
3. **Survive as long as possible**

### Scoring
- **+10 points** for each food eaten
- **+1 segment** to snake length per food

### Game Over Conditions
The game ends if your snake:
- Hits a **wall** (board edge)
- Hits an **obstacle** (█)
- Hits **itself** (its own body)

### Difficulty Adaptation
The game automatically adjusts difficulty based on your performance:
- **Playing well?** → Difficulty increases (faster speed, more obstacles)
- **Struggling?** → Difficulty decreases (slower speed, fewer obstacles)
- **Consistent?** → Difficulty stays the same

---

## Game Statistics

### Displayed During Game
- **Score**: Total points earned
- **Snake Length**: Current snake size
- **Food**: Number of food items on board
- **Obstacles**: Number of obstacles on board
- **Game Over**: Whether the game has ended

### Difficulty Info
- **Level**: 1-10 (1=easy, 10=hard)
- **Speed**: 1-10 (how fast the snake moves)
- **Obstacles**: 0-5 (number of obstacles)
- **Food Rate**: 0.5-2.0x (how often food spawns)
- **Adaptive Mode**: ON/OFF (whether AI adjusts difficulty)

### Performance Metrics
- **Survival Time**: How long you've been playing
- **Food Consumed**: Total food eaten
- **Avg Speed**: Average movement speed
- **Reaction Times**: Number of inputs made

---

## Tips for Playing

### Beginner Tips
1. **Start at Level 1** - Get comfortable with controls
2. **Move slowly** - Don't rush, plan your moves
3. **Avoid corners** - They're dangerous!
4. **Watch for obstacles** - They appear randomly

### Intermediate Tips
1. **Plan ahead** - Look 2-3 moves ahead
2. **Use walls strategically** - Create barriers for yourself
3. **Eat efficiently** - Go for nearby food first
4. **Watch the difficulty** - It adapts to your skill

### Advanced Tips
1. **Create loops** - Use your body to trap food
2. **Manage space** - Keep room to maneuver
3. **Predict spawns** - Food spawns in empty spaces
4. **Master timing** - React quickly to obstacles

---

## Difficulty Levels

### Level 1-3: Easy
- Slow snake speed
- Few obstacles
- Lots of food
- **Best for:** Learning the game

### Level 4-6: Medium
- Normal speed
- Moderate obstacles
- Regular food spawning
- **Best for:** Casual play

### Level 7-10: Hard
- Fast snake speed
- Many obstacles
- Challenging gameplay
- **Best for:** Experienced players

---

## Adaptive Mode

### How It Works
The game learns from your performance:

1. **Tracks your metrics:**
   - How long you survive
   - How much food you eat
   - Your reaction time
   - How many obstacles you avoid

2. **Assesses your skill:**
   - Calculates a skill level (0-100)
   - Determines if you're improving/declining/stable

3. **Adjusts difficulty:**
   - Improving? → Increase difficulty
   - Declining? → Decrease difficulty
   - Stable? → Keep difficulty same

### Manual Mode
You can disable adaptive mode and manually control difficulty:
- Adjust speed slider
- Adjust obstacle density
- Adjust food spawn rate
- Changes apply immediately

---

## Example Gameplay

### Session 1: Learning
```
Starting Level: 1
Moves: w, w, d, d, s, s, a, a
Food Eaten: 2
Final Score: 20
Survival Time: 15 seconds
Difficulty: Level 1 (no change)
```

### Session 2: Improving
```
Starting Level: 1
Moves: w, d, d, s, a, w, d, d, s, a
Food Eaten: 5
Final Score: 50
Survival Time: 45 seconds
Difficulty: Level 2 (increased!)
```

### Session 3: Challenging
```
Starting Level: 2
Moves: w, d, s, a, w, d, s, a, w, d
Food Eaten: 3
Final Score: 30
Survival Time: 20 seconds
Difficulty: Level 1 (decreased)
```

---

## Troubleshooting

### Game doesn't respond to input
- Make sure the terminal window is focused
- Try pressing keys slowly
- Check that Caps Lock is off

### Game closes immediately
- Check for error messages
- Run `python -m pytest src/ -q` to verify installation
- Try `python test_game_quick.py` for a quick test

### Can't see the board clearly
- Maximize your terminal window
- Use a larger font size
- Try a different terminal application

### Game is too easy/hard
- The game adapts automatically
- Play more games to let it learn your skill
- Or manually adjust difficulty in settings

---

## After Playing

### When You Quit
You'll see a summary:
```
Game Over!
Final Score: 150
Survival Time: 45.2s
Food Consumed: 15
Final Difficulty: Level 5
```

### Play Again
Simply run the game again:
```bash
python src/game_demo.py
```

The game will remember your skill level and start at an appropriate difficulty!

---

## Advanced Features

### Debug Mode
See real-time metrics and AI decisions:
```bash
python src/game_demo.py --debug
```

### Statistics
View your game history and progress:
```bash
python src/game_demo.py --stats
```

### Settings
Customize game parameters:
```bash
python src/game_demo.py --settings
```

---

## Performance Tracking

The game tracks:
- **Best Score**: Your highest score ever
- **Average Survival Time**: How long you typically survive
- **Skill Progression**: How your skill improves over time
- **Difficulty Evolution**: How difficulty changes across games

View your stats after playing to see your progress!

---

## Have Fun! 🎮

The Snake Adaptive AI game is designed to:
- ✅ Challenge you appropriately
- ✅ Adapt to your skill level
- ✅ Provide engaging gameplay
- ✅ Track your progress

**Ready to play?** Run: `python src/game_demo.py`

Good luck! 🐍
