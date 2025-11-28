"""
Replace the web server cell with a working interactive runner
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

print("Fixing web server cell...\n")

# Find and replace the problematic cell
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        
        if 'from google.adk.cli.fast_api import create_web_app' in source:
            new_source = """# Interactive Chat with the Concierge Agent
# Run this cell to start chatting with your agent directly in the notebook

runner = InMemoryRunner(agent=root_agent)

async def chat_with_agent():
    print("="*60)
    print("Concierge Agent - Interactive Chat")
    print("="*60)
    print("Type your questions or requests. Type 'exit' to quit.\\n")
    
    session_id = "notebook_session"
    
    while True:
        user_input = input("\\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            print("\\nGoodbye!")
            break
            
        print("\\nAgent: ", end="")
        async for event in runner.run(user_input, session_id=session_id):
            if hasattr(event, 'content') and event.content:
                print(event.content, end="")
        print()  # New line after response

# Start the chat
await chat_with_agent()
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Replaced web server cell {idx} with interactive chat")
            break

# Update the markdown cell before it
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'markdown':
        source = ''.join(cell.get('source', []))
        if 'Running the ADK Web Interface' in source:
            new_source = """## Interactive Chat in Notebook

Execute the cell below to chat with your Concierge Agent directly in this notebook.

**Note**: For web UI access, the `app.py` file in this directory is already configured. Just run:
```bash
python -m google.adk.cli web
```
Then open http://127.0.0.1:8000
"""
            cell['source'] = [line + '\n' for line in new_source.split('\n')[:-1]]
            cell['source'].append(new_source.split('\n')[-1])
            print(f"✓ Updated markdown cell {idx}")
            break

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print("\n✅ Fixed! Notebook now has working interactive chat!")
