"""
Verify if app.py can be imported successfully
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(".").absolute()))

print("Attempting to import app.py...")

try:
    import app
    print("✅ Import successful!")
    print(f"Agent found: {app.agent.name}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
