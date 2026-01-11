# Installing Streamlit - Complete Guide

## Quick Install

### Windows

**Option 1: Run the batch script**
```bash
install_dependencies.bat
```

**Option 2: Manual install**
```bash
python -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
```

Or if that doesn't work:
```bash
python3 -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
```

### macOS/Linux

**Option 1: Run the shell script**
```bash
bash install_dependencies.sh
```

**Option 2: Manual install**
```bash
python3 -m pip install streamlit pydantic pandas pytest hypothesis pytest-cov
```

---

## Step-by-Step Installation

### Step 1: Check Python Installation

```bash
python --version
# or
python3 --version
```

You should see Python 3.9 or higher.

### Step 2: Install Dependencies

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

### Step 3: Verify Installation

```bash
python -c "import streamlit; print(streamlit.__version__)"
```

You should see the version number (e.g., 1.28.1)

### Step 4: Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Use `python3` instead
```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

### Issue: "pip: command not found"

**Solution**: Use Python module syntax
```bash
python -m pip install -r requirements.txt
```

Or:
```bash
python3 -m pip install -r requirements.txt
```

### Issue: "Permission denied"

**Solution**: Use `--user` flag
```bash
python -m pip install --user -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Make sure installation completed successfully
```bash
python -m pip install --upgrade streamlit
```

### Issue: Port 8501 already in use

**Solution**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

---

## Installation Scripts

### Windows Batch Script

Run this file to automatically install dependencies:
```bash
install_dependencies.bat
```

### macOS/Linux Shell Script

Run this file to automatically install dependencies:
```bash
bash install_dependencies.sh
```

---

## Manual Installation

If the scripts don't work, install each package individually:

```bash
# Install Streamlit
python -m pip install streamlit

# Install Pydantic
python -m pip install pydantic

# Install Pandas
python -m pip install pandas

# Install Pytest
python -m pip install pytest

# Install Hypothesis
python -m pip install hypothesis

# Install Pytest-cov
python -m pip install pytest-cov
```

---

## Verify Installation

After installation, verify everything works:

```bash
# Check Streamlit
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"

# Check Pydantic
python -c "import pydantic; print('Pydantic:', pydantic.__version__)"

# Check Pandas
python -c "import pandas; print('Pandas:', pandas.__version__)"

# Check Pytest
python -m pytest --version

# Check Hypothesis
python -c "import hypothesis; print('Hypothesis:', hypothesis.__version__)"
```

---

## Run the App

Once installation is complete:

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Alternative: Virtual Environment

For a clean installation, use a virtual environment:

### Windows

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## Getting Help

If you're still having issues:

1. Check Python version: `python --version`
2. Check pip version: `pip --version`
3. Try upgrading pip: `python -m pip install --upgrade pip`
4. Try installing from requirements.txt: `pip install -r requirements.txt`
5. Check the README.md for more information

---

## What Gets Installed

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.28.1 | Web UI framework |
| pydantic | 2.5.0 | Data validation |
| pandas | 2.1.3 | Data manipulation |
| pytest | 7.4.3 | Testing framework |
| hypothesis | 6.88.0 | Property-based testing |
| pytest-cov | 4.1.0 | Code coverage |

---

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`
3. Open browser to: `http://localhost:8501`
4. Start analyzing databases!

---

## Questions?

- See README.md for overview
- See SETUP_GUIDE.md for detailed setup
- See .kiro/RUNNING_THE_APP.md for how to run
- See .kiro/specs/database-referee/ for requirements and design
