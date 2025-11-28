"""
Restore the overwritten imports cell and correctly place the ADK launcher at the end
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Restoring notebook structure...\n")

# 1. Restore imports cell at index 3
imports_source = [
    "from google.adk.agents import Agent\n",
    "from google.adk.runners import InMemoryRunner\n",
    "from google.adk.tools import AgentTool, FunctionTool, google_search\n",
    "from google.genai import types\n",
    "\n",
    "from google.adk.agents import LlmAgent\n",
    "from google.adk.models.google_llm import Gemini\n",
    "from google.adk.runners import Runner\n",
    "from google.adk.sessions import InMemorySessionService\n",
    "\n",
    "from google.adk.apps.app import App, ResumabilityConfig\n",
    "from google.adk.tools.function_tool import FunctionTool\n",
    "\n",
    "print(\"✅ ADK components imported successfully.\")\n"
]

# Check if cell 3 is currently the launcher (it has subprocess)
if len(notebook['cells']) > 3:
    cell3_source = ''.join(notebook['cells'][3].get('source', []))
    if 'subprocess' in cell3_source and 'run_adk_server' in cell3_source:
        print("Found misplaced launcher at cell 3. Restoring imports...")
        notebook['cells'][3] = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": imports_source
        }
    else:
        print("Cell 3 does not look like the launcher. Inserting imports anyway to be safe.")
        notebook['cells'].insert(3, {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": imports_source
        })

# 2. Find and replace the interactive chat cell (near the end)
# It should have 'chat_with_agent' or 'input('
chat_cell_idx = -1
for idx, cell in enumerate(notebook['cells']):
    # Skip the early cells
    if idx < 10: continue
    
    source = ''.join(cell.get('source', []))
    if 'chat_with_agent' in source or 'input(' in source:
        chat_cell_idx = idx
        break

launcher_source = [
    "# Launch ADK Web Interface\n",
    "# This cell starts the ADK web server and opens it in your browser.\n",
    "# The server uses the configuration from app.py (which exports the notebook's agent).\n",
    "\n",
    "import subprocess\n",
    "import sys\n",
    "import time\n",
    "import webbrowser\n",
    "import threading\n",
    "\n",
    "def run_adk_server():\n",
    "    print(\"🚀 Starting ADK Web Server...\")\n",
    "    print(\"   URL: http://127.0.0.1:8000\")\n",
    "    print(\"   Press Stop (⏹) in the toolbar to shut down the server.\")\n",
    "    \n",
    "    # Open browser automatically\n",
    "    def open_browser():\n",
    "        time.sleep(3)\n",
    "        print(\"   Opening browser...\")\n",
    "        webbrowser.open(\"http://127.0.0.1:8000\")\n",
    "    \n",
    "    threading.Thread(target=open_browser, daemon=True).start()\n",
    "    \n",
    "    # Run the ADK CLI command\n",
    "    # This blocks the cell until you stop it\n",
    "    try:\n",
    "        subprocess.run([sys.executable, \"-m\", \"google.adk.cli\", \"web\"], check=True)\n",
    "    except KeyboardInterrupt:\n",
    "        print(\"\\n✅ Server stopped by user.\")\n",
    "    except Exception as e:\n",
    "        print(f\"\\n❌ Error running server: {e}\")\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    run_adk_server()\n"
]

if chat_cell_idx != -1:
    print(f"Found interactive chat at cell {chat_cell_idx}. Replacing with launcher...")
    notebook['cells'][chat_cell_idx] = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": launcher_source
    }
else:
    print("Could not find interactive chat cell. Appending launcher to end.")
    notebook['cells'].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": launcher_source
    })

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Notebook structure restored and launcher placed correctly!")
