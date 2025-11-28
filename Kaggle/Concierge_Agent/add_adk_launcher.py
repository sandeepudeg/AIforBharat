"""
Add a cell to launch ADK GUI directly from the notebook
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Adding ADK GUI launcher cell...\n")

# Find the chat cell and replace it with ADK launcher
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'chat_with_agent()' in source or 'InMemoryRunner' in source:
            new_source = """# Launch ADK Web GUI from Notebook
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# Export agent configuration to a temporary file
temp_app_file = Path(__file__).parent / "_notebook_app.py" if '__file__' in globals() else Path("./_notebook_app.py")

app_code = '''
"""Auto-generated from Concierge_Agent.ipynb"""
import os
import json
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search

load_dotenv()

# Copy all tool definitions and agent configurations
''' + f'''
# Import everything from current notebook context
import sys
sys.path.insert(0, "{Path('.').absolute()}")

# Use the agent defined in notebook
agent = {repr(root_agent)}
'''

# Write temporary app file
with open(temp_app_file, 'w') as f:
    f.write(app_code)

print(f"✅ Created temporary app file: {temp_app_file}")
print("\\n🚀 Launching ADK Web GUI...")
print("   Server will start at: http://127.0.0.1:8000")
print("   Press Ctrl+C in terminal to stop")

# Launch ADK CLI web server
try:
    # Open browser after a short delay
    import threading
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://127.0.0.1:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run ADK web server (this will block)
    subprocess.run([sys.executable, "-m", "google.adk.cli", "web"], 
                   cwd=str(Path('.').absolute()))
except KeyboardInterrupt:
    print("\\n✅ Server stopped")
finally:
    # Cleanup
    if temp_app_file.exists():
        temp_app_file.unlink()
        print(f"Cleaned up: {temp_app_file}")
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Replaced cell {idx} with ADK GUI launcher")
            break

# Update markdown
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if 'Interactive Chat' in source or 'ADK Web Interface' in source:
            new_source = """## Launch ADK Web GUI

Execute the cell below to:
1. Export the agent configuration
2. Start the ADK web server
3. Automatically open your browser to http://127.0.0.1:8000

**The agent will appear in the dropdown and you can chat through the web interface!**

To stop the server, press Ctrl+C in the Jupyter terminal.
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Updated markdown cell {idx}")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ ADK GUI launcher added to notebook!")
print("Execute that cell to launch the web interface!")
