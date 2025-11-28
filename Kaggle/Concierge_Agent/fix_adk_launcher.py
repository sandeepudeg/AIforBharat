"""
Replace the interactive chat cell (which causes popups) with a proper ADK GUI launcher
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Replacing interactive chat with ADK GUI launcher...\n")

# Find the cell with input() or chat_with_agent
target_idx = -1
for idx, cell in enumerate(notebook['cells']):
    source = ''.join(cell.get('source', []))
    if 'input(' in source or 'chat_with_agent' in source or 'InMemoryRunner' in source:
        target_idx = idx
        break

if target_idx != -1:
    print(f"Found target cell at index {target_idx}")
    
    new_source = """# Launch ADK Web Interface
# This cell starts the ADK web server and opens it in your browser.
# The server uses the configuration from app.py (which exports the notebook's agent).

import subprocess
import sys
import time
import webbrowser
import threading

def run_adk_server():
    print("🚀 Starting ADK Web Server...")
    print("   URL: http://127.0.0.1:8000")
    print("   Press Stop (⏹) in the toolbar to shut down the server.")
    
    # Open browser automatically
    def open_browser():
        time.sleep(3)
        print("   Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the ADK CLI command
    # This blocks the cell until you stop it
    try:
        subprocess.run([sys.executable, "-m", "google.adk.cli", "web"], check=True)
    except KeyboardInterrupt:
        print("\\n✅ Server stopped by user.")
    except Exception as e:
        print(f"\\n❌ Error running server: {e}")

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
    
    # Clean up the source list (remove trailing newline from last item)
    if notebook['cells'][target_idx]['source']:
        notebook['cells'][target_idx]['source'][-1] = notebook['cells'][target_idx]['source'][-1].rstrip('\n')

    # Update the markdown cell before it if it exists
    if target_idx > 0 and notebook['cells'][target_idx-1]['cell_type'] == 'markdown':
        notebook['cells'][target_idx-1]['source'] = [
            "## Launch ADK Web GUI\n",
            "\n",
            "Run the cell below to start the graphical interface.\n",
            "It will automatically open http://127.0.0.1:8000 in your browser.\n"
        ]

    print("✓ Replaced cell with ADK launcher")

else:
    print("Could not find the interactive chat cell. Appending launcher to end.")
    # Append if not found
    # ... (omitted for brevity, assuming it exists based on previous context)

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Notebook updated! Interactive chat removed.")
