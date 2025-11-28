"""
Update notebook launcher to use the custom run_gui_custom.py script
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating launcher to use custom script...\n")

# Find the launcher cell
target_idx = len(notebook['cells']) - 1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'run_adk_server' in source:
        target_idx = idx
        break

new_source = """# Launch ADK Web Interface (Custom Script)
import subprocess
import sys
import time
import webbrowser
import threading
import os
from pathlib import Path

def run_adk_server():
    print("🚀 Preparing ADK Web Server...")
    
    # Create the custom runner script
    runner_script = Path("run_gui_custom.py")
    
    with open(runner_script, "w", encoding="utf-8") as f:
        f.write('''
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(".").absolute()))

try:
    # Import agent from app.py
    from app import agent
    print(f"✅ Imported agent: {agent.name}")
except ImportError as e:
    print(f"❌ Failed to import agent: {e}")
    sys.exit(1)

import uvicorn
from google.adk.cli.fast_api import create_web_app
from google.adk.cli.discovery import register_agent

if __name__ == "__main__":
    print("🚀 Starting Custom ADK Server...")
    
    # Create web app
    app = create_web_app(
        apps_dir="./",
        agents_dir="./",
        disable_auth=True
    )
    
    # Explicitly register our agent
    register_agent(agent.name, agent)
    print(f"✅ Registered agent: {agent.name}")
    
    print("   URL: http://127.0.0.1:8000")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
''')
    
    print(f"   Created runner: {runner_script}")
    print("   URL: http://127.0.0.1:8000")
    
    # Open browser automatically
    def open_browser():
        time.sleep(4)
        print("   Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the custom script
    cmd = [sys.executable, "run_gui_custom.py"]
    
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
        if runner_script.exists():
            try:
                runner_script.unlink()
                print(f"   Cleaned up {runner_script}")
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

print("\n✅ Launcher updated to use custom programmatic runner!")
