# Quick Start - Play Snake Adaptive AI

## 🎮 Play the Game in 3 Steps

### Step 1: Run the Demo
```bash
python src/game_demo.py
```

### Step 2: Choose an Option
```
1. Run Demo (auto-play)
2. Play Interactive Game

Select option (1 or 2): 
```

### Step 3: Enjoy!
- **Option 1**: Watch the AI play for 20 moves
- **Option 2**: Control the snake yourself

---

## 🎯 Controls (Interactive Mode)

```
up     → Move snake up
down   → Move snake down
left   → Move snake left
right  → Move snake right
q      → Quit game
```

---

## 📊 Game Board

```
●  = Your snake (head)
○  = Snake body
✱  = Food (eat for points!)
█  = Obstacles (avoid!)
.  = Empty space
```

---

## 🎮 How to Play

1. **Move the snake** using arrow keys or direction names
2. **Eat food** (✱) to grow and score points
3. **Avoid obstacles** (█) and walls
4. **Watch the AI** adapt difficulty based on your skill
5. **Game ends** when you hit an obstacle or wall

---

## 📈 Scoring

- **10 points** per food eaten
- **Snake grows** by 1 segment per food
- **Difficulty increases** if you're doing well
- **Difficulty decreases** if you're struggling

---

## 🤖 AI Features

The game watches your performance and:
- Calculates your skill level (0-100)
- Detects if you're improving/stable/declining
- Adjusts difficulty automatically
- Shows you the reasoning

---

## 📚 Full Documentation

- **PLAY_GAME.md** - Detailed gameplay guide
- **GAME_UI_STATUS.md** - UI status and features
- **README.md** - Project overview
- **HOW_TO_TEST.md** - Testing guide

---

## ✅ What's Included

- ✅ Complete game engine
- ✅ AI skill assessment
- ✅ Adaptive difficulty
- ✅ Performance metrics
- ✅ Text-based demo
- ✅ 132 passing tests

---

## ⚠️ Note

This is a **text-based demo**, not a graphical UI. It runs in your terminal and shows:
- Game board in ASCII
- Real-time statistics
- AI assessments
- Difficulty adjustments

For a graphical UI, you would need to build it with Pygame or similar.

---

## 🚀 Try It Now!

```bash
python src/game_demo.py
```

Select option 1 or 2 and enjoy! 🎉
