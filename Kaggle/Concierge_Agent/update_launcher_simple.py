"""
Update launcher to use simple invocation without --app flag, relying on standard discovery
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Updating launcher to use standard discovery...\n")

# Find the launcher cell
target_idx = len(notebook['cells']) - 1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'run_adk_server' in source:
        target_idx = idx
        break

new_source = """# Launch ADK Web Interface
import subprocess
import sys
import time
import webbrowser
import threading
import os
from pathlib import Path

def run_adk_server():
    print("🚀 Preparing ADK Web Server...")
    print("   URL: http://127.0.0.1:8000")
    
    # Open browser automatically
    def open_browser():
        time.sleep(4)
        print("   Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run ADK CLI in current directory
    # It automatically finds app.py
    cmd = [sys.executable, "-m", "google.adk.cli", "web"]
    
    try:
        # Check port
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 8000)) == 0:
                print("\\n⚠️ Port 8000 seems to be in use!")
                print("   Please stop other running servers first.")
                return

        print(f"   Executing: {' '.join(cmd)}")
        # IMPORTANT: Run in the current directory where app.py is located
        subprocess.run(cmd, check=True, cwd=str(Path('.').absolute()))
        
    except KeyboardInterrupt:
        print("\\n✅ Server stopped by user.")
    except Exception as e:
        print(f"\\n❌ Error: {e}")

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

print("\n✅ Launcher updated to use standard discovery (no --app flag)!")
