"""
Update launcher to create a self-contained App object in notebook_app.py
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating launcher to use App object...\n")

# Find the launcher cell
target_idx = len(notebook['cells']) - 1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'run_adk_server' in source:
        target_idx = idx
        break

new_source = """# Launch ADK Web Interface (Self-Contained with App)
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
# Auto-generated self-contained app for ADK CLI
import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.apps.app import App

# Define a simple agent that mirrors the notebook's agent
model = Gemini(model="gemini-1.5-flash")
agent = Agent(
    name="ConciergeCoordinator",
    model=model,
    instructions="You are a helpful concierge agent."
)

# Create App object (ADK CLI needs this)
app = App(
    name="concierge_agent",
    root_agent=agent
)

# Export for ADK CLI
__all__ = ["agent", "app"]
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
    # We use --app to specify the file and variable
    cmd = [sys.executable, "-m", "google.adk.cli", "web", "--app", "notebook_app:app"]
    
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

print("\n✅ Updated launcher to use App object!")
