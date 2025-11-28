# Complete Guide: Using Concierge Agent with ADK GUI

## Current Setup

Your `app.py` is already configured correctly for ADK GUI. Here's what it has:
- ✅ All 23 tools defined
- ✅ 5 specialized agents (Planning, Booking, Utility, Search, Social)
- ✅ Root coordinator agent
- ✅ Agent exported as `agent = root_agent`

## How to Access the ADK GUI

### Step 1: Ensure ADK Server is Running

You already have it running! The terminal shows:
```bash
python -m google.adk.cli web
```

Server is at: http://127.0.0.1:8000

### Step 2: Open in Browser

1. Open your browser
2. Go to: **http://127.0.0.1:8000**
3. You should see the ADK Dev UI

### Step 3: Select Your Agent

In the ADK interface:
- Look for a dropdown that says "Select an agent" or "Select app"
- You should see **"ConciergeCoordinator"** in the list
- Click on it to select it

### Step 4: Start Chatting!

Once the agent is selected, you can type messages like:
- "I want to plan a trip to Japan in autumn"
- "Search for flights from NYC to Tokyo"
- "Convert 1000 USD to JPY"
- "What's the weather in Kyoto?"

## If Agent Doesn't Appear in Dropdown

### Solution 1: Restart the Server

1. In the terminal running ADK, press **Ctrl+C**
2. Wait for it to stop completely
3. Run again: `python -m google.adk.cli web`
4. Refresh your browser

### Solution 2: Check app.py Location

The server must be run from the directory containing `app.py`:
```bash
cd d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent
python -m google.adk.cli web
```

### Solution 3: Verify Agent Export

Run this to verify:
```bash
python -c "from app import agent; print(f'✅ Agent: {agent.name}')"
```

Should output: `✅ Agent: ConciergeCoordinator`

## Current Status

- ✅ `app.py` properly configured
- ✅ Agent exported correctly
- ✅ Server should be running
- ❓ Check if agent appears in dropdown

## Troubleshooting

If still not working:

1. **Check terminal output** when you run the server - any errors?
2. **Check browser console** (F12) - any errors?
3. **Verify URL** - exactly http://127.0.0.1:8000 (not localhost)

The setup is correct - the agent should appear in the ADK GUI dropdown!
