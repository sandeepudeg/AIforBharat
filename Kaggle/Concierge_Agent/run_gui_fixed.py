import sys
import os
from pathlib import Path
import uvicorn

# Add current directory to path
sys.path.insert(0, str(Path(".").absolute()))

try:
    # Import correct function
    from google.adk.cli.fast_api import get_fast_api_app
    print("✅ Imported get_fast_api_app")
except ImportError as e:
    print(f"❌ Failed to import get_fast_api_app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Fixed ADK Server...")
    
    try:
        # Create web app using the correct API
        # We point agents_dir to current directory so it finds app.py
        app = get_fast_api_app(
            agents_dir=".",
            web=True,
            host="127.0.0.1",
            port=8000
        )
        print("✅ App created successfully")
        
        print("   URL: http://127.0.0.1:8000")
        
        # Run with uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
