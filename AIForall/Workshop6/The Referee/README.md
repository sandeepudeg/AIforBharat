# Database Referee ⚖️

A decision-support tool that helps teams choose between PostgreSQL, DynamoDB, and Redis based on their specific constraints.

## Overview

Rather than declaring a single "winner," the Database Referee analyzes trade-offs explicitly, showing pros and cons relative to your constraints. This enables informed decision-making in database selection.

## Features

✅ **Constraint-Based Analysis**: Input your specific requirements (data structure, consistency, scale, latency, etc.)
✅ **Disqualification Rules**: Automatically eliminates unsuitable databases based on hard constraints
✅ **Weighted Scoring**: Calculates scores based on multiple factors with adjustable weights
✅ **Trade-off Analysis**: Shows pros and cons of each option relative to your constraints
✅ **Comparison Table**: Visual comparison of all databases across key factors
✅ **Configuration Persistence**: Save and load your constraint configurations

## Quick Start

### Option 1: Command-Line Interface (No Dependencies)

```bash
python cli_app.py
```

This version works without installing Streamlit. Just answer the questions and get your analysis!

### Option 2: Streamlit Web Interface (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**

2. **Navigate to the project directory**
   ```bash
   cd "The Referee"
   ```

3. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   # Web interface
   streamlit run app.py
   
   # OR command-line interface
   python cli_app.py
   ```

## Usage

### Web Interface (Streamlit)

1. Open the app at `http://localhost:8501`
2. Fill in the constraint form with your requirements
3. Click "Analyze & Get Recommendation"
4. View the results including:
   - Disqualified options with reasons
   - Winner with score and rationale
   - Pros and cons
   - Score breakdown
   - Comparison table

### Command-Line Interface

1. Run `python cli_app.py`
2. Answer each question about your database needs
3. View your constraint summary
4. See the next steps for analysis

## Constraint Inputs

The tool asks for the following constraints:

| Constraint | Options | Description |
|-----------|---------|-------------|
| Data Structure | Relational, JSON, Key-Value | Type of data you're storing |
| Read/Write Ratio | 0-100 | Percentage of read operations |
| Consistency Level | Strong, Eventual | Consistency requirements |
| Query Complexity | Simple, Moderate, Complex | Complexity of your queries |
| Data Scale | Positive number (GB) | Expected data size |
| Latency Requirement | Positive number (ms) | Maximum acceptable latency |
| Team Expertise | Low, Medium, High | Your team's database knowledge |
| Persistence Required | Yes/No | Whether data must be persistent |

## Databases Compared

### PostgreSQL
- **Strengths**: Full SQL support, ACID transactions, complex joins, strong consistency
- **Weaknesses**: Vertical scaling, higher latency, requires schema management
- **Best for**: Relational data with complex queries

### DynamoDB
- **Strengths**: Horizontal scaling, low latency, managed service
- **Weaknesses**: Limited query flexibility, eventual consistency, no joins
- **Best for**: High-scale, simple key-value access

### Redis
- **Strengths**: Ultra-low latency, in-memory performance, caching
- **Weaknesses**: Limited persistence, memory constraints, not for primary storage
- **Best for**: Caching and real-time data

## Disqualification Rules

The tool automatically disqualifies databases that don't meet your hard constraints:

1. **Joins Required** → Disqualifies DynamoDB
2. **Strong Consistency** → Disqualifies DynamoDB
3. **Persistence Critical** → Disqualifies Redis
4. **Scale > 10GB** → Disqualifies Redis
5. **Latency < 1ms** → Disqualifies PostgreSQL

## Scoring Algorithm

Remaining databases are scored using:

```
base_score = (
    data_structure_match × 0.30 +
    consistency_match × 0.25 +
    query_flexibility × 0.20 +
    cost_score × 0.15 +
    latency_score × 0.10
)

Adjustments:
- If joins needed: multiply query_flexibility × 3.0
- If strong consistency: multiply consistency × 2.0
- If scale > 100GB: multiply scaling × 1.5

final_score = normalize(adjusted_score, 0-10 scale)
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Property-Based Tests

```bash
pytest tests/properties/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Basic Test (No Dependencies)

```bash
python test_basic.py
```

## Project Structure

```
The Referee/
├── src/
│   ├── __init__.py
│   ├── models.py                    # Data models (Constraint, Report, etc.)
│   └── constraint_parser.py         # Constraint validation
├── tests/
│   ├── unit/                        # Unit tests
│   ├── properties/                  # Property-based tests
│   │   └── test_constraint_properties.py
│   └── integration/                 # Integration tests
├── data/                            # Configuration storage
├── app.py                           # Streamlit web interface
├── cli_app.py                       # Command-line interface
├── test_basic.py                    # Basic test script
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
├── .gitignore
├── README.md                        # This file
├── SETUP_GUIDE.md                   # Detailed setup instructions
└── .kiro/                           # Specification documents
    └── specs/database-referee/
        ├── requirements.md          # Feature requirements
        ├── design.md                # System design
        └── tasks.md                 # Implementation tasks
```

## Specification Documents

The project includes comprehensive specification documents in `.kiro/specs/database-referee/`:

- **requirements.md**: 7 requirements with 35+ acceptance criteria using EARS patterns
- **design.md**: Complete architecture, components, data models, and correctness properties
- **tasks.md**: 12 implementation tasks with 40+ sub-tasks

These documents guide the implementation and ensure all requirements are met.

## Development Status

### ✅ Completed
- Project structure and setup
- Constraint data model with validation
- Constraint parser with error handling
- Property-based tests (5 tests)
- Streamlit UI with constraint input form
- Command-line interface

### 🔄 In Progress
- Disqualification engine
- Scoring engine
- Report generator
- Complete UI with results display

### ⏳ Planned
- Persistence layer (save/load configurations)
- Full test suite (80%+ coverage)
- Documentation and deployment

## Examples

### Example 1: Relational Data with Joins

**Input**:
- Data Structure: Relational
- Read/Write Ratio: 50%
- Consistency: Strong
- Query Complexity: Complex
- Scale: 10 GB
- Latency: 5 ms
- Team Expertise: Medium
- Persistence: Yes

**Expected Output**:
- 🏆 Winner: PostgreSQL (8.5/10)
- ❌ Disqualified: DynamoDB (can't do joins), Redis (not persistent)

### Example 2: High-Scale Cache

**Input**:
- Data Structure: Key-Value
- Read/Write Ratio: 90%
- Consistency: Eventual
- Query Complexity: Simple
- Scale: 5 GB
- Latency: 1 ms
- Team Expertise: High
- Persistence: No

**Expected Output**:
- 🏆 Winner: Redis (9.0/10)
- ❌ Disqualified: PostgreSQL (latency < 1ms)

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "ModuleNotFoundError: No module named 'src'"

**Solution**: Make sure you're running from the project root directory
```bash
cd "The Referee"
streamlit run app.py
```

### "python: command not found"

**Solution**: Use `python3` instead
```bash
python3 -m streamlit run app.py
```

### Port 8501 already in use

**Solution**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

## Contributing

This project is part of a spec-driven development exercise. All changes should:

1. Reference the specification documents in `.kiro/specs/database-referee/`
2. Include property-based tests for new functionality
3. Maintain 80%+ code coverage
4. Follow the EARS pattern for requirements

## License

This project is created for educational purposes.

## Support

For detailed setup instructions, see `SETUP_GUIDE.md`

For specification details, see `.kiro/specs/database-referee/`

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run web interface
streamlit run app.py

# Run command-line interface
python cli_app.py

# Run tests
pytest tests/ -v

# Run basic test
python test_basic.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

**Database Referee v0.1.0** - Making database decisions easier, one constraint at a time. ⚖️
