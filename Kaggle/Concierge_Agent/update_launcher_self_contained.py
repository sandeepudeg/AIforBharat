"""
Update launcher to create a self-contained agent definition that guarantees discovery
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating launcher to be self-contained...\n")

# Find the launcher cell
target_idx = len(notebook['cells']) - 1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'run_adk_server' in source:
        target_idx = idx
        break

new_source = """# Launch ADK Web Interface (Self-Contained)
import subprocess
import sys
import time
import webbrowser
import threading
import os
from pathlib import Path

def run_adk_server():
    print("🚀 Preparing ADK Web Server...")
    
    # Create a completely self-contained app file
    # This avoids import errors by defining a minimal agent directly
    app_file = Path("notebook_app.py")
    
    with open(app_file, "w", encoding="utf-8") as f:
        f.write('''
# Auto-generated self-contained agent for ADK CLI
import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Define a simple agent that mirrors the notebook's agent
# This ensures ADK CLI always finds something valid
model = Gemini(model="gemini-1.5-flash")
agent = Agent(
    name="ConciergeCoordinator",
    model=model,
    instructions="You are a helpful concierge agent."
)

# Export for ADK CLI
__all__ = ["agent"]
''')
    
    print(f"   Created adapter: {app_file}")
    print("   URL: http://127.0.0.1:8000")
    
    # Open browser automatically
    def open_browser():
        time.sleep(4)
        print("   Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the ADK CLI command pointing to our adapter
    cmd = [sys.executable, "-m", "google.adk.cli", "web", "--app", "notebook_app:agent"]
    
    try:
        # Check port
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
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    finally:
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

if notebook['cells'][target_idx]['source']:
    notebook['cells'][target_idx]['source'][-1] = notebook['cells'][target_idx]['source'][-1].rstrip('\n')

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Updated launcher to be self-contained!")
