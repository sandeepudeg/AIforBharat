@echo off
REM Database Referee - Installation and Run Script
REM This script installs dependencies and runs the Streamlit app

echo.
echo ========================================
echo Database Referee - Setup and Run
echo ========================================
echo.

REM Try to find Python
echo Searching for Python installation...

REM Try python3.13
if exist "C:\ProgramData\chocolatey\bin\python3.13.exe" (
    echo Found Python 3.13 at C:\ProgramData\chocolatey\bin\python3.13.exe
    set PYTHON_PATH=C:\ProgramData\chocolatey\bin\python3.13.exe
    goto install
)

REM Try python3
for /f "delims=" %%i in ('where python3 2^>nul') do (
    echo Found Python 3 at %%i
    set PYTHON_PATH=%%i
    goto install
)

REM Try python
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo Found Python at %%i
    set PYTHON_PATH=%%i
    goto install
)

echo ERROR: Python not found!
echo Please install Python 3.9 or higher
pause
exit /b 1

:install
echo.
echo Installing dependencies...
echo.

"%PYTHON_PATH%" -m pip install --upgrade pip
"%PYTHON_PATH%" -m pip install streamlit pydantic hypothesis pandas pytest pytest-cov

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dependencies installed successfully!
echo ========================================
echo.

echo Starting Streamlit app...
echo.
echo The app will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the app
echo.

"%PYTHON_PATH%" -m streamlit run app.py

pause
