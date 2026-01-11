#!/bin/bash

# Database Referee - Install Dependencies Script

echo ""
echo "========================================"
echo "Database Referee - Installing Dependencies"
echo "========================================"
echo ""

# Try to install dependencies
echo "Attempting to install dependencies..."
echo ""

# Try python3
if command -v python3 &> /dev/null; then
    echo "Found python3, installing dependencies..."
    python3 -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "Installation successful!"
        echo "========================================"
        echo ""
        echo "You can now run:"
        echo "  streamlit run app.py"
        echo ""
        exit 0
    fi
fi

# Try python
if command -v python &> /dev/null; then
    echo "Found python, installing dependencies..."
    python -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "Installation successful!"
        echo "========================================"
        echo ""
        echo "You can now run:"
        echo "  streamlit run app.py"
        echo ""
        exit 0
    fi
fi

# If all failed
echo ""
echo "========================================"
echo "ERROR: Could not install dependencies"
echo "========================================"
echo ""
echo "Please try manually:"
echo "  python -m pip install -r requirements.txt"
echo ""
echo "Or install Python from:"
echo "  https://www.python.org/downloads/"
echo ""
exit 1
