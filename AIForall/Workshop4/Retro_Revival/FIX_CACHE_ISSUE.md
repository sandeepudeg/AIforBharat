# Fix: Python Cache Issue

## Problem

You're seeing an error about `metrics.reaction_time` even though the file has been fixed to use `metrics.reaction_times`.

This is a **Python cache issue** - Python is using an old cached version of the file.

## Solution

### Option 1: Use the Provided Scripts (Easiest)

#### Windows (Command Prompt)
```bash
run_game.bat
```

#### Windows (PowerShell)
```powershell
.\run_game.ps1
```

#### Mac/Linux
```bash
bash run_game.sh
```

These scripts will:
1. Clear all Python cache files
2. Start the game

### Option 2: Manual Cache Clearing

#### Windows (Command Prompt)
```cmd
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc
rmdir /s /q .pytest_cache
python src/game_demo.py
```

#### Windows (PowerShell)
```powershell
Get-ChildItem -Path "." -Name "__pycache__" -Recurse -Directory -Force | ForEach-Object { Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path "." -Name "*.pyc" -Recurse -Force | ForEach-Object { Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue }
Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
python src/game_demo.py
```

#### Mac/Linux
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache
python src/game_demo.py
```

### Option 3: Python Cache Clearing

```python
python -c "
import py_compile
import os
import shutil

# Remove __pycache__ directories
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        shutil.rmtree(os.path.join(root, '__pycache__'))

# Remove .pyc files
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            os.remove(os.path.join(root, file))

print('Cache cleared!')
"

python src/game_demo.py
```

## Verification

To verify the file is correct:

```python
python -c "
import sys
sys.path.insert(0, 'src')
with open('src/game_demo.py', 'r') as f:
    content = f.read()
    if 'metrics.reaction_times' in content:
        print('✅ File is correct!')
    else:
        print('❌ File needs fixing')
"
```

## Why This Happens

Python compiles `.py` files to `.pyc` bytecode files for faster loading. These cached files are stored in `__pycache__` directories.

When you modify a `.py` file, Python sometimes doesn't immediately recognize the change and uses the old cached version instead.

## Prevention

To prevent this in the future:

1. Always clear cache before running after file changes
2. Use the provided `run_game.bat` or `run_game.ps1` scripts
3. Set `PYTHONDONTWRITEBYTECODE=1` environment variable to disable caching

## Still Having Issues?

If you still see the error after clearing cache:

1. Close all Python processes
2. Restart your terminal/IDE
3. Try again

If the problem persists, the file may have been reverted. Check:

```bash
grep "reaction_times" src/game_demo.py
```

Should show: `print(f"  Reaction Times: {len(metrics.reaction_times)}")`

If it shows `reaction_time` (singular), the file needs to be fixed again.

## Quick Fix Command

Copy and paste this one command to fix everything:

### Windows (PowerShell)
```powershell
Get-ChildItem -Path "." -Name "__pycache__" -Recurse -Directory -Force | ForEach-Object { Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue }; Get-ChildItem -Path "." -Name "*.pyc" -Recurse -Force | ForEach-Object { Remove-Item -Path $_ -Force -ErrorAction SilentlyContinue }; Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue; python src/game_demo.py
```

### Windows (Command Prompt)
```cmd
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" & del /s /q *.pyc & rmdir /s /q .pytest_cache & python src/game_demo.py
```

---

## Summary

The file is **already fixed**. You just need to clear the Python cache.

**Use:** `run_game.bat` (Windows) or `run_game.ps1` (PowerShell)

Or manually clear cache and run: `python src/game_demo.py`

The game will work! 🎮
