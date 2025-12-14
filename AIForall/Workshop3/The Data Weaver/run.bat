@echo off
REM Weather & Pollen Dashboard - Startup Script (Windows)
REM This script installs dependencies, sets environment variables, and starts the Flask application

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Weather ^& Pollen Dashboard - Startup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python version: %PYTHON_VERSION%
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed or not in PATH
    echo Please install pip and try again
    pause
    exit /b 1
)

echo [OK] pip is available
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Set environment variables
echo Setting environment variables...
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONUNBUFFERED=1
echo [OK] Environment variables set:
echo   - FLASK_APP=%FLASK_APP%
echo   - FLASK_ENV=%FLASK_ENV%
echo   - FLASK_DEBUG=%FLASK_DEBUG%
echo.

REM Create necessary directories if they don't exist
echo Checking project structure...
if not exist "templates" mkdir templates
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "src" mkdir src
if not exist "tests" mkdir tests
echo [OK] Project directories verified
echo.

REM Display startup information
echo ==========================================
echo Starting Flask Application
echo ==========================================
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start Flask application
python app.py

pause
