"""
Update the ADK launcher to be robust and ensure agent discovery
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating ADK launcher...\n")

# Find the launcher cell (last one)
target_idx = len(notebook['cells']) - 1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'run_adk_server' in source:
        target_idx = idx
        break

new_source = """# Launch ADK Web Interface (Robust Version)
import subprocess
import sys
import time
import webbrowser
import threading
import os
from pathlib import Path

def run_adk_server():
    print("🚀 Preparing ADK Web Server...")
    
    # 1. Create a temporary app file that exports our agent
    # This ensures ADK CLI can find it even if running from notebook
    app_file = Path("notebook_app.py")
    
    with open(app_file, "w", encoding="utf-8") as f:
        f.write('''
# Auto-generated adapter for ADK CLI
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(".").absolute()))

# Import the agent from app.py (which should match notebook state)
try:
    from app import agent
    print("✅ Successfully imported agent from app.py")
except ImportError:
    # Fallback: try to reconstruct if app.py is missing
    print("⚠️ Could not import from app.py, using fallback")
    from google.adk.agents import Agent
    agent = Agent(name="ConciergeCoordinator")

# Export for ADK CLI
__all__ = ["agent"]
''')
    
    print(f"   Created adapter: {app_file}")
    print("   URL: http://127.0.0.1:8000")
    print("   Press Stop (⏹) in the toolbar to shut down.")
    
    # 2. Open browser automatically
    def open_browser():
        time.sleep(4)
        print("   Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 3. Run the ADK CLI command pointing to our adapter
    # We use --app to specify the file and variable
    cmd = [sys.executable, "-m", "google.adk.cli", "web", "--app", "notebook_app:agent"]
    
    try:
        # Check if port 8000 is in use (simple check)
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 8000)) == 0:
                print("\\n⚠️ Port 8000 seems to be in use!")
                print("   Please stop other running servers first.")
                return

        print(f"   Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\\n✅ Server stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"\\n❌ Server exited with error code {e.returncode}")
        print("   Try running 'python -m google.adk.cli web' in terminal instead.")
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    finally:
        # Cleanup
        if app_file.exists():
            try:
                app_file.unlink()
                print(f"   Cleaned up {app_file}")
            except:
                pass

if __name__ == "__main__":
    run_adk_server()
"""

notebook['cells'][target_idx] = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [line + '\n' for line in new_source.split('\n')]
}

# Clean up source
if notebook['cells'][target_idx]['source']:
    notebook['cells'][target_idx]['source'][-1] = notebook['cells'][target_idx]['source'][-1].rstrip('\n')

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Updated launcher to use explicit app adapter!")
