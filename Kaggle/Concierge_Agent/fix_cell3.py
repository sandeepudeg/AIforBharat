"""
Check and fix cell 3
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Checking cell 3...\n")

cell_3 = notebook['cells'][3]
print(f"Cell type: {cell_3['cell_type']}")
print(f"Source lines: {len(cell_3['source'])}")

# Show the problematic area (line 9 according to error)
if len(cell_3['source']) > 9:
    for i in range(max(0, 7), min(len(cell_3['source']), 12)):
        print(f"Line {i}: {repr(cell_3['source'][i])}")

# The issue is likely in the imports cell - let's rebuild it cleanly
if cell_3['cell_type'] == 'code':
    # Rebuild the imports cell with clean formatting
    clean_imports = """from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

print("✅ ADK components imported successfully.")
"""
    
    cell_3['source'] = [line + '\n' for line in clean_imports.split('\n')[:-1]]
    cell_3['source'].append(clean_imports.split('\n')[-1])
    
    print("\n✓ Rebuilt cell 3 with clean imports")

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Cell 3 fixed!")
