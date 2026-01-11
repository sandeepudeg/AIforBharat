# Database Referee - Setup & Run Guide

## Prerequisites

You need to have Python 3.9+ installed on your system.

### Check Python Installation

```bash
python --version
# or
python3 --version
# or
python3.13 --version
```

If Python is not found, install it from https://www.python.org/downloads/

---

## Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd "The Referee"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit==1.28.1
- pydantic==2.5.0
- pandas==2.1.3
- pytest==7.4.3
- hypothesis==6.88.0
- pytest-cov==4.1.0

### Step 4: Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Use `python3` instead:
```bash
python3 -m venv venv
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

### Issue: "streamlit: command not found"

**Solution**: Use Python module syntax:
```bash
python -m streamlit run app.py
# or
python3 -m streamlit run app.py
```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Make sure you're running from the project root directory:
```bash
cd "The Referee"
streamlit run app.py
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Property-Based Tests Only

```bash
pytest tests/properties/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

---

## Running Basic Test

To verify the constraint parser works without Streamlit:

```bash
python test_basic.py
# or
python3 test_basic.py
```

This will test:
1. Valid constraint parsing
2. Invalid constraint rejection (out of range)
3. Invalid data structure rejection

---

## Project Structure

```
The Referee/
├── src/
│   ├── __init__.py
│   ├── models.py                    # Data models
│   └── constraint_parser.py         # Constraint validation
├── tests/
│   ├── unit/
│   ├── properties/
│   │   └── test_constraint_properties.py
│   └── integration/
├── data/                            # Configuration storage
├── app.py                           # Streamlit application
├── test_basic.py                    # Basic test script
├── requirements.txt                 # Dependencies
├── pytest.ini                       # Test configuration
├── .gitignore
└── .kiro/                           # Spec documents
    └── specs/database-referee/
        ├── requirements.md
        ├── design.md
        └── tasks.md
```

---

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run the app**: `streamlit run app.py`
3. **Test the constraint parser**: `python test_basic.py`
4. **Run tests**: `pytest tests/ -v`

---

## Common Commands

```bash
# Activate virtual environment
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/properties/test_constraint_properties.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run basic test
python test_basic.py

# Deactivate virtual environment
deactivate
```

---

## System Requirements

- Python 3.9 or higher
- pip (Python package manager)
- ~500MB disk space for dependencies
- Modern web browser for Streamlit UI

---

## Support

If you encounter issues:

1. Check Python version: `python --version`
2. Verify virtual environment is activated
3. Reinstall dependencies: `pip install --upgrade -r requirements.txt`
4. Check that you're in the correct directory: `pwd` (macOS/Linux) or `cd` (Windows)
5. Review error messages carefully - they usually indicate the exact issue

---

## What the App Does

The Database Referee helps you choose between PostgreSQL, DynamoDB, and Redis by:

1. **Collecting Constraints**: You input your requirements (data structure, consistency, scale, etc.)
2. **Validating Input**: The app validates all inputs and shows specific error messages
3. **Analyzing Options**: The app applies disqualification rules and scoring algorithms
4. **Generating Report**: The app shows which database is best for your use case with pros/cons

---

## Current Status

✅ **Completed**:
- Project structure and setup
- Constraint data model with validation
- Constraint parser with error handling
- Property-based tests
- Streamlit UI with constraint input form

🔄 **In Progress**:
- Disqualification engine
- Scoring engine
- Report generator
- Complete UI with results display

---

## Questions?

Refer to the spec documents in `.kiro/specs/database-referee/`:
- `requirements.md` - Feature requirements
- `design.md` - System design and architecture
- `tasks.md` - Implementation tasks
