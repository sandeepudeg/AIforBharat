#!/bin/bash

# Weather & Pollen Dashboard - Startup Script (Unix/Linux/macOS)
# This script installs dependencies, sets environment variables, and starts the Flask application

set -e  # Exit on any error

echo "=========================================="
echo "Weather & Pollen Dashboard - Startup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed or not in PATH"
    echo "Please install pip and try again"
    exit 1
fi

echo "✓ pip3 is available"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed successfully"
echo ""

# Set environment variables
echo "Setting environment variables..."
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONUNBUFFERED=1
echo "✓ Environment variables set:"
echo "  - FLASK_APP=$FLASK_APP"
echo "  - FLASK_ENV=$FLASK_ENV"
echo "  - FLASK_DEBUG=$FLASK_DEBUG"
echo ""

# Create necessary directories if they don't exist
echo "Checking project structure..."
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p src
mkdir -p tests
echo "✓ Project directories verified"
echo ""

# Display startup information
echo "=========================================="
echo "Starting Flask Application"
echo "=========================================="
echo ""
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask application
python3 app.py
