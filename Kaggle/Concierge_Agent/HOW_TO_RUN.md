# How to Run the Concierge Agent

## The Correct Way

Since `app.py` already exists with the complete configuration, just run:

```bash
cd d:\Learning\IITKML\Self_learning\Kaggle\Concierge_Agent
python -m google.adk.cli web
```

This will:
1. Automatically find and load `app.py`
2. Start the web server
3. Open http://localhost:8000 in your browser

## Alternative: From Notebook

If you want to run from the notebook:

1. Execute all cells in `Concierge_Agent.ipynb`
2. The App object will be created
3. Then run: `python -m google.adk.cli web`

## What Happened

The old syntax `adk web --app app:app` is not supported. The correct command is simply:
```bash
python -m google.adk.cli web
```

ADK CLI automatically discovers the `app.py` file in the current directory.
