# 🎮 Tkinter GUI Now Available!

## ✅ GUI is Ready!

A full-featured Tkinter GUI has been created for Snake Adaptive AI!

---

## Quick Start

### Windows (Easiest)
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

## What's Included

### Visual Game Board
- 20x20 grid with colored cells
- Green snake (head and body)
- Red food circles
- Gray obstacles
- Dark grid lines

### Real-Time Statistics
- Score (green)
- Snake Length (blue)
- Difficulty Level (red)
- Survival Time (orange)
- Food Consumed (purple)
- Adaptive Mode Status (cyan)

### Control Buttons
- **Start Game** - Begin playing
- **Pause** - Pause the game
- **Resume** - Continue playing
- **Reset** - Start over

### Keyboard Controls
- `W/↑` - Move UP
- `S/↓` - Move DOWN
- `A/←` - Move LEFT
- `D/→` - Move RIGHT
- `Q` - QUIT

---

## Features

✅ **Visual Game Board** - See your snake move in real-time
✅ **Live Statistics** - Track score, length, difficulty, time
✅ **Smooth Animation** - 50ms update rate for smooth gameplay
✅ **Color Coded** - Easy to understand visual feedback
✅ **Responsive Controls** - Immediate snake movement
✅ **Game States** - Start, Pause, Resume, Reset
✅ **Adaptive Difficulty** - AI learns from your performance
✅ **Game Over Dialog** - Shows final statistics

---

## How to Play

1. **Run the GUI**
   ```bash
   run_gui.bat
   ```

2. **Click "Start Game"**
   - Snake appears in center
   - Food spawns randomly
   - Obstacles appear

3. **Move Your Snake**
   - Use WASD or Arrow Keys
   - Eat red food circles
   - Avoid gray obstacles

4. **Watch Difficulty Adapt**
   - Playing well? → Difficulty increases
   - Struggling? → Difficulty decreases
   - Consistent? → Difficulty stays same

5. **Game Over**
   - Hit wall, obstacle, or yourself
   - See final statistics
   - Play again!

---

## GUI vs Text Version

| Feature | GUI | Text |
|---------|-----|------|
| Visual Board | ✅ | ✅ |
| Real-Time Stats | ✅ | ✅ |
| Smooth Animation | ✅ | ✅ |
| Color Coded | ✅ | ✅ |
| Buttons | ✅ | ❌ |
| Keyboard Only | ❌ | ✅ |
| Pause/Resume | ✅ | ✅ |
| Game Over Dialog | ✅ | ❌ |

---

## System Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- Windows, Mac, or Linux

### Check Tkinter Installation
```bash
python -m tkinter
```

If a window appears, Tkinter is installed!

### Install Tkinter (if needed)

**Windows:**
- Usually included with Python

**Mac:**
```bash
brew install python-tk
```

**Linux:**
```bash
sudo apt-get install python3-tk
```

---

## File Structure

```
.
├── src/
│   ├── game_gui.py          # Tkinter GUI (NEW!)
│   ├── game_demo.py         # Text version
│   ├── game_loop.py         # Game loop
│   ├── game_engine.py       # Game engine
│   └── ...
├── run_gui.bat              # Windows launcher (NEW!)
├── run_gui.ps1              # PowerShell launcher (NEW!)
├── GUI_GUIDE.md             # GUI documentation (NEW!)
└── ...
```

---

## Documentation

- **GUI_GUIDE.md** - Detailed GUI guide
- **START_HERE.md** - Quick start
- **READY_TO_PLAY.md** - Game overview
- **PLAY_GAME_GUIDE.md** - Gameplay tips

---

## Comparison

### Text Version
```bash
python src/game_demo.py
```
- Terminal-based
- Simple controls
- Good for quick play

### GUI Version
```bash
run_gui.bat
```
- Graphical interface
- Visual feedback
- Better for extended play

---

## Ready to Play?

### Start the GUI
```bash
run_gui.bat          # Windows
python src/game_gui.py  # All platforms
```

### Or Play Text Version
```bash
python src/game_demo.py
```

---

## Features Comparison

### GUI Advantages
✅ Visual game board
✅ Colored elements
✅ Buttons for control
✅ Game over dialog
✅ Better for casual play

### Text Advantages
✅ Lightweight
✅ Works anywhere
✅ No GUI dependencies
✅ Good for testing

---

## Have Fun! 🎮

Choose your preferred way to play:

**GUI Version:**
```bash
run_gui.bat
```

**Text Version:**
```bash
python src/game_demo.py
```

Both are fully functional and ready to play! 🐍✨
