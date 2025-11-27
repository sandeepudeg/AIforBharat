# Quick Contract Generator

A modern Flask-based web application for generating professional contract templates with persistent storage and multi-contract management.

## Features

### ✨ Core Features
- **Email-Based Authentication**: Secure token-based authentication without storing passwords
- **Contract Generation**: Create professional contracts with comprehensive sections
- **Multiple Export Formats**: Download contracts as PDF or Word documents
- **Glassmorphic UI**: Modern, responsive interface with frosted glass effects
- **Contract Management**: Save, edit, view, and delete multiple contracts
- **Persistent Storage**: All contracts are saved to SQLite database and persist across sessions
- **Draft Saving**: Save contracts as drafts and continue editing later
- **Contract Templates**: Duplicate or use existing contracts as templates
- **Quick Start Dashboard**: Returning users get a personalized dashboard with quick access
- **Returning User Features**: Easily edit older contracts or create new ones from templates

### 🔐 Security
- No credential storage - uses email verification tokens only
- Session-based authentication with automatic expiration
- Protected routes requiring authentication
- Secure token generation and expiration

### 📋 Contract Sections
1. **Parties Information** - Full legal names, addresses, entity types
2. **Purpose & Scope** - Contract purpose, scope of work, deliverables
3. **Key Terms** - Dates, payment terms, performance standards
4. **Legal Compliance** - Compliance requirements, licenses, permits
5. **Risk & Liability** - Liability clauses, indemnity, insurance
6. **Confidentiality & IP** - Confidentiality obligations, IP ownership
7. **Termination** - Termination conditions, notice period, consequences
8. **Dispute Resolution** - Resolution method, jurisdiction, governing law
9. **Signatures** - Signature blocks for all parties

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd contract-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Creating a Contract

1. **Sign Up/Sign In**: Enter your email address to create an account or sign in
2. **Verify Email**: Click the verification link sent to your email
3. **Fill Form**: Complete the contract form with all required information
4. **Generate**: Click "Generate Contract" to create the contract
5. **Preview**: Review the contract before downloading
6. **Download**: Export as PDF or Word document
7. **Save**: Optionally save the contract for future reference

### Managing Contracts

#### View All Contracts
- Click "My Contracts" to see all your saved contracts
- Each contract shows creation and update dates
- Quick access to view, edit, or delete

#### View Contract
- Click the eye icon (👁️) to view a saved contract
- See the full contract preview
- Download as PDF or Word

#### Edit Contract
- Click the edit icon (✏️) to modify a saved contract
- Update any contract details
- Save changes to the database

#### Delete Contract
- Click the delete icon (🗑️) to remove a contract
- Confirm deletion when prompted
- Contract is permanently removed

## Project Structure

```
contract-generator/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── contracts.db                    # SQLite database (auto-created)
├── routes/
│   ├── auth_routes.py             # Authentication routes
│   ├── contract_routes.py         # Contract generation routes
│   └── contract_management_routes.py  # Contract management routes
├── models/
│   └── contract.py                # Contract data model
├── utils/
│   ├── database.py                # Database operations
│   ├── contract_generator.py      # PDF/Word generation
│   └── file_utils.py              # File utilities
├── templates/
│   ├── base.html                  # Base template
│   ├── signin.html                # Sign in page
│   ├── signup.html                # Sign up page
│   ├── contract_generator.html    # Contract form
│   ├── contracts_list.html        # Contracts list
│   ├── contract_view.html         # Contract view
│   └── error.html                 # Error page
├── static/
│   ├── css/
│   │   └── style.css              # Glassmorphic styling
│   └── js/
│       └── main.js                # Client-side validation
└── tests/
    ├── test_auth.py               # Authentication tests
    ├── test_contract_model.py     # Model tests
    ├── test_form_validation.py    # Form validation tests
    ├── test_pdf_generation.py     # PDF generation tests
    ├── test_docx_generation.py    # Word generation tests
    └── ... (more test files)
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

### Contracts Table
```sql
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test file:
```bash
python -m pytest tests/test_auth.py -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## API Endpoints

### Authentication
- `GET /auth/signup` - Sign up page
- `POST /auth/signup` - Submit signup
- `GET /auth/signin` - Sign in page
- `POST /auth/signin` - Submit signin
- `GET /auth/verify?token=<token>` - Verify email
- `GET /auth/logout` - Logout

### Contract Generation
- `GET /contract/generator` - Contract form
- `POST /contract/generate` - Generate contract
- `GET /contract/preview` - Preview contract
- `GET /contract/download/pdf` - Download PDF
- `GET /contract/download/docx` - Download Word

### Contract Management
- `GET /contracts/quick-start` - Quick start dashboard for returning users
- `GET /contracts/list` - List all contracts
- `POST /contracts/save` - Save new contract
- `GET /contracts/<id>/view` - View contract
- `GET /contracts/<id>/edit` - Edit contract
- `POST /contracts/<id>/update` - Update contract
- `POST /contracts/<id>/delete` - Delete contract
- `POST /contracts/<id>/duplicate` - Duplicate contract as draft
- `POST /contracts/<id>/use-as-template` - Use contract as template
- `GET /contracts/<id>/download/pdf` - Download saved contract as PDF
- `GET /contracts/<id>/download/docx` - Download saved contract as Word

## Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Generation**: ReportLab
- **Word Generation**: python-docx
- **Testing**: pytest, Hypothesis
- **Session Management**: Flask-Session

## Features Highlights

### 🎨 Glassmorphic Design
- Modern frosted glass effect UI
- Gradient backgrounds
- Smooth animations and transitions
- Responsive design for all devices

### 🔄 Session Persistence
- Contracts saved to database
- Access contracts across sessions
- Automatic user tracking
- Last login timestamps

### 📊 Contract Management
- Save multiple contracts
- Edit existing contracts
- View contract history
- Delete contracts
- Quick access to downloads

### ✅ Comprehensive Testing
- 129 passing tests
- Unit tests for all components
- Property-based testing with Hypothesis
- Form validation tests
- Authentication tests
- File generation tests

## Security Considerations

1. **No Password Storage**: Uses email verification tokens instead
2. **Session Expiration**: Sessions expire after 24 hours
3. **CSRF Protection**: Flask-Session provides CSRF protection
4. **Input Validation**: All form inputs are validated
5. **SQL Injection Prevention**: Uses parameterized queries
6. **Authentication Required**: Protected routes require authentication

## Future Enhancements

- [ ] Email notifications for contract updates
- [ ] Contract templates library
- [ ] Collaborative editing
- [ ] Version history tracking
- [ ] Advanced search and filtering
- [ ] Contract analytics
- [ ] API for third-party integrations
- [ ] Mobile app
- [ ] Cloud storage integration

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on the repository.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### Version 1.0.0
- Initial release
- Email-based authentication
- Contract generation with PDF/Word export
- Contract management system
- Persistent storage with SQLite
- Comprehensive test suite
- Glassmorphic UI design
