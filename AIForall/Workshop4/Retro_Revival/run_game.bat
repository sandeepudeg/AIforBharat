@echo off
REM Clear Python cache and run the game
echo Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
rmdir /s /q .pytest_cache >nul 2>&1

echo.
echo Starting Snake Adaptive AI...
echo.
python src/game_demo.py

pause
