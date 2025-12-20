# Supply Chain Optimizer

A multi-agent AI system built on Amazon Bedrock and Strands Agents that automates and optimizes supply chain operations across multiple warehouses and vendors.

## Features

- **Demand Forecasting**: Predict future product demand with confidence intervals
- **Inventory Optimization**: Calculate optimal inventory levels and reorder points
- **Supplier Coordination**: Manage supplier communication and order tracking
- **Anomaly Detection**: Identify unusual patterns in inventory and supplier performance
- **Analytics & Reporting**: Generate comprehensive supply chain insights and KPIs
- **Multi-Warehouse Management**: Optimize inventory distribution across locations
- **Real-Time Alerts**: Receive notifications for critical supply chain events

## Project Structure

```
supply-chain-optimizer/
├── src/
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   ├── environment.py   # Environment variables and settings
│   │   └── logger.py        # Logging configuration
│   ├── aws/                 # AWS service clients
│   │   ├── __init__.py
│   │   └── clients.py       # AWS SDK clients (RDS, DynamoDB, S3, etc.)
│   ├── observability/       # Observability and tracing
│   │   ├── __init__.py
│   │   └── xray.py          # X-Ray tracing setup
│   ├── __init__.py
│   └── main.py              # Application entry point
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_config.py       # Configuration tests
│   └── test_aws_clients.py  # AWS client tests
├── logs/                    # Application logs (created at runtime)
├── pyproject.toml           # Project configuration and dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Prerequisites

- Python 3.10+
- AWS Account with appropriate permissions
- Environment variables configured (see `.env.example`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd supply-chain-optimizer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

## Running the Application

### Development Mode

```bash
python -m src.main
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_config.py

# Run in watch mode
pytest-watch
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

### Key Configuration Areas

- **AWS Services**: Region, credentials, and service-specific settings
- **Database**: RDS connection parameters
- **DynamoDB**: Region and optional local endpoint
- **S3**: Bucket name and region
- **SNS**: Topic ARNs for alerts and notifications
- **Logging**: Log level and format (json or text)
- **Bedrock**: Model ID and region for AI agents

## AWS Services Used

- **RDS**: Relational data storage (products, suppliers, purchase orders)
- **DynamoDB**: Real-time data storage (inventory, forecasts)
- **S3**: Document and report storage
- **Lambda**: Serverless compute for agent execution
- **EventBridge**: Event-driven orchestration
- **SNS**: Alert and notification delivery
- **X-Ray**: Distributed tracing and observability

## Development

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

Run formatters:
```bash
black src tests
isort src tests
```

### Logging

The application uses structured logging with JSON format in production and human-readable format in development.

Logs are written to:
- Console (all levels)
- `logs/error.log` (errors only)
- `logs/combined.log` (all levels)

## License

[Your License Here]

## Support

For issues and questions, please contact the Supply Chain Team.
