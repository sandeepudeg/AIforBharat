# Database Referee - Installation and Run Script (PowerShell)
# This script installs dependencies and runs the Streamlit app

Write-Host ""
Write-Host "========================================"
Write-Host "Database Referee - Setup and Run"
Write-Host "========================================"
Write-Host ""

# Try to find Python
Write-Host "Searching for Python installation..."

$pythonPath = $null

# Try python3.13
if (Test-Path "C:\ProgramData\chocolatey\bin\python3.13.exe") {
    Write-Host "Found Python 3.13 at C:\ProgramData\chocolatey\bin\python3.13.exe"
    $pythonPath = "C:\ProgramData\chocolatey\bin\python3.13.exe"
}

# Try python3
if ($null -eq $pythonPath) {
    try {
        $pythonPath = (Get-Command python3 -ErrorAction Stop).Source
        Write-Host "Found Python 3 at $pythonPath"
    } catch {
        # Continue
    }
}

# Try python
if ($null -eq $pythonPath) {
    try {
        $pythonPath = (Get-Command python -ErrorAction Stop).Source
        Write-Host "Found Python at $pythonPath"
    } catch {
        # Continue
    }
}

if ($null -eq $pythonPath) {
    Write-Host "ERROR: Python not found!"
    Write-Host "Please install Python 3.9 or higher"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing dependencies..."
Write-Host ""

& $pythonPath -m pip install --upgrade pip
& $pythonPath -m pip install streamlit pydantic hypothesis pandas pytest pytest-cov

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "Dependencies installed successfully!"
Write-Host "========================================"
Write-Host ""

Write-Host "Starting Streamlit app..."
Write-Host ""
Write-Host "The app will open in your browser at http://localhost:8501"
Write-Host "Press Ctrl+C to stop the app"
Write-Host ""

& $pythonPath -m streamlit run app.py

Read-Host "Press Enter to exit"
