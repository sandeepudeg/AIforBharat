import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(".").absolute()))

print("🔍 Starting ADK Diagnosis (Phase 2)...")

try:
    from app import agent
    print(f"   ✅ Imported agent: {agent.name}")
except Exception:
    print("   ❌ Failed to import agent from app.py")
    traceback.print_exc()
    sys.exit(1)

try:
    from google.adk.cli.fast_api import create_web_app
    from google.adk.cli.discovery import register_agent
    print("   ✅ Imported ADK CLI tools")
except ImportError:
    print("   ❌ Failed to import ADK CLI tools")
    traceback.print_exc()
    sys.exit(1)

print("\nTesting App Creation...")
try:
    # Create web app
    app = create_web_app(
        apps_dir="./",
        agents_dir="./",
        disable_auth=True
    )
    print("   ✅ create_web_app successful")
    
    # Explicitly register our agent
    register_agent(agent.name, agent)
    print(f"   ✅ Registered agent: {agent.name}")
    
except Exception:
    print("   ❌ Failed during app creation/registration")
    traceback.print_exc()
    sys.exit(1)

print("\nDiagnosis Phase 2 Complete. Ready to launch.")
