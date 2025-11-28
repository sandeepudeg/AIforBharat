import json
import os

notebook_path = "Concierge_Agent.ipynb"

with open(notebook_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# The new content for the runner script
new_script_content = r'''
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
'''

# Find the cell and update it
found = False
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "def run_adk_server():" in source and "runner_script = Path(\"run_gui_custom.py\")" in source:
            print("✅ Found target cell")
            
            # We need to replace the f.write('''...''') block
            # This is a bit tricky with string replacement on the source list.
            # Let's reconstruct the cell source.
            
            new_source = []
            lines = source.splitlines(keepends=True)
            
            in_write_block = False
            for line in lines:
                if "f.write('''" in line:
                    new_source.append(line)
                    new_source.append(new_script_content.strip() + "\n")
                    in_write_block = True
                elif "''')" in line and in_write_block:
                    new_source.append(line)
                    in_write_block = False
                elif in_write_block:
                    continue # Skip old content
                else:
                    new_source.append(line)
            
            cell["source"] = new_source
            found = True
            break

if found:
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    print("✅ Notebook updated successfully")
else:
    print("❌ Target cell not found")
