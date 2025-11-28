"""
Test script to check if app.py loads correctly
"""

try:
    print("Loading app.py...")
    from app import app, root_agent
    print("✅ app.py loaded successfully!")
    print(f"App name: {app.app_name}")
    print(f"Root agent: {root_agent.name}")
    print(f"Root agent has {len(root_agent.tools)} tools")
except Exception as e:
    print(f"❌ Error loading app.py: {e}")
    import traceback
    traceback.print_exc()
