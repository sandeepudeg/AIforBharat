@echo off
REM Database Referee - Install Dependencies Script

echo.
echo ========================================
echo Database Referee - Installing Dependencies
echo ========================================
echo.

REM Try different Python commands
echo Attempting to install dependencies...
echo.

REM Try python
python -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installation successful!
    echo ========================================
    echo.
    echo You can now run:
    echo   streamlit run app.py
    echo.
    pause
    exit /b 0
)

REM Try python3
python3 -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installation successful!
    echo ========================================
    echo.
    echo You can now run:
    echo   streamlit run app.py
    echo.
    pause
    exit /b 0
)

REM Try python3.13
python3.13 -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installation successful!
    echo ========================================
    echo.
    echo You can now run:
    echo   streamlit run app.py
    echo.
    pause
    exit /b 0
)

REM If all failed
echo.
echo ========================================
echo ERROR: Could not install dependencies
echo ========================================
echo.
echo Please try manually:
echo   python -m pip install -r requirements.txt
echo.
echo Or install Python from:
echo   https://www.python.org/downloads/
echo.
pause
exit /b 1
