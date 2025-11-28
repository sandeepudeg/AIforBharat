"""
Add back the missing helper utilities that the demo needs
"""
import json

with open('Concierge_Agent.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find where to insert - after the tools definition, before the agents
# Look for the cell that ends with social tools
insert_pos = None
for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell.get('source', []))
        if 'share_to_social_media' in source and 'def share_to_social_media' in source:
            insert_pos = idx + 1
            break

if insert_pos is None:
    print("Could not find insertion point, adding at position 6")
    insert_pos = 6

print(f"Inserting helper utilities at position {insert_pos}")

# Create the helper utilities cell
helper_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# --- Helper Utilities for Session and Metrics ---\n",
        "\n",
        "# Simple Session Service (in-memory)\n",
        "class SimpleSessionService:\n",
        "    def __init__(self):\n",
        "        self.sessions = {}\n",
        "    def get(self, session_id):\n",
        "        return self.sessions.get(session_id, {})\n",
        "    def set(self, session_id, state):\n",
        "        self.sessions[session_id] = state\n",
        "    def clear(self, session_id):\n",
        "        self.sessions.pop(session_id, None)\n",
        "\n",
        "session_service = SimpleSessionService()\n",
        "\n",
        "# Context Compaction (simple token limit)\n",
        "def compact_context(messages, max_tokens=500):\n",
        "    \"\"\"Very naive compaction: keep last N messages\"\"\"\n",
        "    if len(messages) <= max_tokens:\n",
        "        return messages\n",
        "    return messages[-max_tokens:]\n",
        "\n",
        "# Metrics counters\n",
        "class Metrics:\n",
        "    def __init__(self):\n",
        "        self.counters = {}\n",
        "    def inc(self, name, amount=1):\n",
        "        self.counters[name] = self.counters.get(name, 0) + amount\n",
        "    def report(self):\n",
        "        return self.counters\n",
        "\n",
        "metrics = Metrics()\n",
        "\n",
        "print(\"✅ Helper utilities initialized (session_service, metrics, compact_context)\")\n"
    ]
}

# Convert source to proper list format
helper_cell['source'] = [line + '\n' for line in helper_cell['source']]
# Remove \n from last line
helper_cell['source'][-1] = helper_cell['source'][-1].rstrip('\n')

# Insert the cell
notebook['cells'].insert(insert_pos, helper_cell)

# Save
with open('Concierge_Agent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=4, ensure_ascii=False)

print(f"\n✅ Added helper utilities cell at position {insert_pos}")
print(f"Total cells now: {len(notebook['cells'])}")
