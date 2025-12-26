# Pune Local Intelligence Knowledge Base

A comprehensive web application providing detailed information about Pune, India. Built with Python Flask and featuring an interactive chat interface.

## Features

- **Interactive Chat Interface**: Ask questions about Pune and get instant answers
- **17 Knowledge Categories**: Comprehensive coverage of Pune's geography, culture, food, attractions, and more
- **Full-Text Search**: Search across all content with category filtering
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Related Articles**: Discover connected topics and deepen your knowledge
- **User-Friendly Navigation**: Easy-to-use interface with clear categorization

## Project Structure

```
.
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       ├── main.js      # Main JavaScript
│       └── chat.js      # Chat interface
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── about.html       # About page
│   └── errors/
│       ├── 404.html     # 404 error page
│       └── 500.html     # 500 error page
└── data/
    └── knowledge_base/  # Knowledge base data (JSON files)
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pune-knowledge-base
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

Configuration is managed through `config.py`. You can set environment variables:

```bash
export FLASK_ENV=development  # or testing, production
export SECRET_KEY=your-secret-key
```

## Usage

### Homepage
- Browse 17 categories of Pune information
- Use the search bar to find specific topics
- Click on any category to explore

### Chat Interface
- Click the chat button (bottom right)
- Ask questions about Pune naturally
- Get instant answers with related articles

### Search
- Use the search bar on the homepage
- Filter results by category
- Click on results to view full articles

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Running with Debug Mode

```bash
export FLASK_ENV=development
python app.py
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a chat message

### Search
- `GET /api/search?q=<query>` - Search knowledge base

### Categories
- `GET /api/categories` - Get all categories
- `GET /api/categories/<category_id>` - Get category details
- `GET /api/categories/<category_id>/articles` - Get articles in category

### Articles
- `GET /api/articles/<article_id>` - Get article details

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5
- **Icons**: Font Awesome
- **Data Format**: JSON

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Performance

- Page load time: < 2 seconds
- Search response: < 1 second
- Chat response: < 2 seconds

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader friendly
- High contrast mode support

## Future Enhancements

- User accounts and bookmarks
- Personalized recommendations
- Multi-language support
- Advanced NLP for chat
- Map integration
- Mobile app
- Voice search
- Offline mode

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For questions, issues, or suggestions, please open an issue on GitHub or contact the development team.

## Acknowledgments

- Pune's rich cultural heritage
- The Marathi community
- All contributors and supporters

---

**Version**: 1.0.0  
**Last Updated**: December 2025
